from __future__ import annotations

import typing

from ..kaitai.utils import (
    filter_by_list_type,
    find_by_list_type,
    find_by_type,
)
from ..models.items.composition import CompItem
from .layer import parse_layer

if typing.TYPE_CHECKING:
    from ..kaitai import Aep
    from ..models.properties.marker import Marker


def parse_composition(
    child_chunks: list[Aep.Chunk],
    item_id: int,
    item_name: str,
    label: Aep.Label,
    parent_id: int | None,
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
        parent_id: The composition's parent folder unique ID.
        comment: The composition comment.
    """
    cdta_chunk = find_by_type(chunks=child_chunks, chunk_type="cdta")
    cdta_data = cdta_chunk.data

    # Normalize bg_color from 0-255 to 0-1 range to match ExtendScript output
    bg_color = [c / 255 for c in cdta_data.bg_color]

    composition = CompItem(
        comment=comment,
        item_id=item_id,
        label=label,
        name=item_name,
        type_name="Composition",
        parent_id=parent_id,
        duration=cdta_data.duration,
        frame_duration=int(
            cdta_data.frame_duration
        ),  # in JSX API, this value is 1 / frame_rate (the duration of a frame). Here, duration * frame_rate
        frame_rate=cdta_data.frame_rate,
        height=cdta_data.height,
        pixel_aspect=cdta_data.pixel_aspect,
        width=cdta_data.width,
        bg_color=bg_color,
        frame_blending=cdta_data.frame_blending,
        hide_shy_layers=cdta_data.hide_shy_layers,
        layers=[],
        markers=[],
        motion_blur=cdta_data.motion_blur,
        motion_blur_adaptive_sample_limit=cdta_data.motion_blur_adaptive_sample_limit,
        motion_blur_samples_per_frame=cdta_data.motion_blur_samples_per_frame,
        preserve_nested_frame_rate=cdta_data.preserve_nested_frame_rate,
        preserve_nested_resolution=cdta_data.preserve_nested_resolution,
        shutter_angle=cdta_data.shutter_angle,
        shutter_phase=cdta_data.shutter_phase,
        resolution_factor=cdta_data.resolution_factor,
        time_scale=cdta_data.time_scale,
        in_point=cdta_data.in_point,
        frame_in_point=int(cdta_data.frame_in_point),
        out_point=cdta_data.out_point,
        frame_out_point=int(cdta_data.frame_out_point),
        frame_time=int(cdta_data.frame_time),
        time=cdta_data.time,
        display_start_time=cdta_data.display_start_time,
        display_start_frame=int(cdta_data.display_start_frame),
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
        layer.containing_comp_id = item_id
        composition.layers.append(layer)

    return composition


def _get_markers(
    child_chunks: list[Aep.Chunk], composition: CompItem
) -> list[Marker]:
    """
    Get the composition markers.
    Args:
        child_chunks: child chunks of the composition LIST chunk.
        composition: The parent composition.
    """
    markers_layer_chunk = find_by_list_type(chunks=child_chunks, list_type="SecL")
    markers_layer = parse_layer(
        layer_chunk=markers_layer_chunk,
        composition=composition,
    )
    return markers_layer.markers
