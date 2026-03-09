from __future__ import annotations

import typing
from typing import Any

from ..enums import Label
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    find_by_list_type,
    find_by_type,
)
from ..models.items.composition import CompItem
from .layer import parse_layer

if typing.TYPE_CHECKING:
    from ..kaitai import Aep
    from ..models.items.folder import FolderItem
    from ..models.properties.marker import MarkerValue


def parse_composition(
    child_chunks: list[Aep.Chunk],
    item_id: int,
    item_name: str,
    label: Label,
    parent_folder: FolderItem,
    comment: str,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
) -> CompItem:
    """
    Parse a composition item.

    Args:
        child_chunks: child chunks of the composition LIST chunk.
        item_id: The unique item ID.
        item_name: The composition name.
        label: The label color. Colors are represented by their number (0 for
            None, or 1 to 16 for one of the preset colors in the Labels
            preferences).
        parent_folder: The composition's parent folder.
        comment: The composition comment.
        effect_param_defs: Project-level effect parameter definitions, used as
            fallback when layer-level parT chunks are missing.
    """
    cdta_chunk = find_by_type(chunks=child_chunks, chunk_type="cdta")
    try:
        cdrp_chunk = find_by_type(chunks=child_chunks, chunk_type="cdrp")
        drop_frame = bool(cdrp_chunk.drop_frame)
    except ChunkNotFoundError:
        drop_frame = False

    # Normalize bg_color from 0-255 to 0-1 range to match ExtendScript output
    bg_color = [c / 255 for c in cdta_chunk.bg_color]

    composition = CompItem(
        comment=comment,
        id=item_id,
        label=label,
        name=item_name,
        type_name="Composition",
        parent_folder=parent_folder,
        draft3d=cdta_chunk.draft3d,
        duration=cdta_chunk.duration,
        frame_duration=int(
            cdta_chunk.frame_duration
        ),  # in JSX API, this value is 1 / frame_rate (the duration of a frame). Here, duration * frame_rate
        frame_rate=cdta_chunk.frame_rate,
        height=cdta_chunk.height,
        pixel_aspect=cdta_chunk.pixel_aspect,
        width=cdta_chunk.width,
        bg_color=bg_color,
        frame_blending=cdta_chunk.frame_blending,
        hide_shy_layers=cdta_chunk.hide_shy_layers,
        layers=[],
        markers=[],
        motion_blur=cdta_chunk.motion_blur,
        motion_blur_adaptive_sample_limit=cdta_chunk.motion_blur_adaptive_sample_limit,
        motion_blur_samples_per_frame=cdta_chunk.motion_blur_samples_per_frame,
        preserve_nested_frame_rate=cdta_chunk.preserve_nested_frame_rate,
        preserve_nested_resolution=cdta_chunk.preserve_nested_resolution,
        shutter_angle=cdta_chunk.shutter_angle,
        shutter_phase=cdta_chunk.shutter_phase,
        resolution_factor=cdta_chunk.resolution_factor,
        time_scale=cdta_chunk.time_scale,
        in_point=cdta_chunk.in_point,
        frame_in_point=int(cdta_chunk.frame_in_point),
        out_point=cdta_chunk.out_point,
        frame_out_point=int(cdta_chunk.frame_out_point),
        frame_time=int(cdta_chunk.frame_time),
        time=cdta_chunk.time,
        display_start_time=cdta_chunk.display_start_time,
        display_start_frame=int(cdta_chunk.display_start_frame),
        drop_frame=drop_frame,
    )

    composition.markers = _get_markers(
        child_chunks=child_chunks,
        composition=composition,
    )

    # Parse composition's layers
    layer_sub_chunks = filter_by_list_type(chunks=child_chunks, list_type="Layr")
    for layer_chunk in layer_sub_chunks:
        layer = parse_layer(
            layer_chunk=layer_chunk,
            composition=composition,
            effect_param_defs=effect_param_defs,
        )
        composition.layers.append(layer)

    # Apply effect selected states from Ewst/ewot chunks
    selected_states = _parse_effect_selected(child_chunks)
    effect_idx = 0
    for layer in composition.layers:
        if layer.effects is None:
            continue
        for effect in layer.effects:
            if effect_idx < len(selected_states):
                effect.selected = selected_states[effect_idx]
            effect_idx += 1

    return composition


def _parse_effect_selected(child_chunks: list[Aep.Chunk]) -> list[bool]:
    """Parse effect selected states from LIST:Ewst / ewot chunks.

    The ``ewot`` chunk inside ``LIST:Ewst`` stores per-property flags for
    the effect workspace.  Each entry is 4 bytes: the first byte contains
    flags where bit 6 (``0x40``) indicates *selected*.  Entries whose first
    byte has bit 7 (``0x80``) set are child properties of an effect; entries
    **without** bit 7 are effect-group-level entries.  By filtering to the
    group-level entries and checking bit 6 we obtain a boolean per effect.

    Args:
        child_chunks: The composition item's child chunks.

    Returns:
        Ordered list of booleans, one per effect across all layers.
    """
    selected: list[bool] = []
    ewst_chunks = filter_by_list_type(chunks=child_chunks, list_type="Ewst")
    for ewst_chunk in ewst_chunks:
        try:
            ewot_chunk = find_by_type(chunks=ewst_chunk.chunks, chunk_type="ewot")
        except ChunkNotFoundError:
            continue

        for entry in ewot_chunk.entries:
            # Entries without is_child_property are effect group nodes
            if not entry.is_child_property:
                selected.append(entry.selected)

    return selected


def _get_markers(
    child_chunks: list[Aep.Chunk], composition: CompItem
) -> list[MarkerValue]:
    """
    Get the composition markers.

    Marker keyframe times in the binary format are stored relative to the
    hidden marker layer's (SecL) own start time. They must be offset by the
    layer's start_time to obtain composition time, which is what ExtendScript
    reports via ``marker.time``.

    Args:
        child_chunks: child chunks of the composition LIST chunk.
        composition: The parent composition.
    """
    markers_layer_chunk = find_by_list_type(chunks=child_chunks, list_type="SecL")
    markers_layer = parse_layer(
        layer_chunk=markers_layer_chunk,
        composition=composition,
        effect_param_defs={},
    )

    # Adjust marker frame_time from layer-relative to comp-relative time.
    # Binary keyframe times are relative to the SecL layer's own timeline,
    # but ExtendScript reports marker times in composition time.
    for marker in markers_layer.markers:
        marker.frame_time += markers_layer.frame_start_time

    return markers_layer.markers
