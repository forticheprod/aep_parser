from __future__ import annotations

import typing

from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    find_by_list_type,
    find_by_type,
)
from ..models.enums import Label
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
        draft_3d=False,  # Set later from fips chunk in parse_project
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
        )
        composition.layers.append(layer)

    return composition


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
    )

    # Adjust marker frame_time from layer-relative to comp-relative time.
    # Binary keyframe times are relative to the SecL layer's own timeline,
    # but ExtendScript reports marker times in composition time.
    for marker in markers_layer.markers:
        marker.frame_time += markers_layer.frame_start_time

    return markers_layer.markers
