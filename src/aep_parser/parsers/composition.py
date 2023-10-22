from __future__ import (
    absolute_import,
    unicode_literals,
    division
)

from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
    filter_by_list_type,
)
from ..models.items.composition import CompItem
from .layer import parse_layer


def parse_composition(child_chunks, item_id, item_name, label, parent_id, comment):
    cdta_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="cdta"
    )
    cdta_data = cdta_chunk.data
    time_scale = cdta_data.time_scale

    markers = _get_markers(
        child_chunks=child_chunks,
        time_scale=time_scale,
    )

    composition = CompItem(
        comment=comment,
        item_id=item_id,
        label=label,
        name=item_name,
        type_name="Composition",
        parent_id=parent_id,

        duration=cdta_data.duration,
        frame_duration=int(cdta_data.frame_duration),
        frame_rate=cdta_data.frame_rate,
        height=cdta_data.height,
        pixel_aspect=cdta_data.pixel_aspect,
        width=cdta_data.width,

        bg_color=cdta_data.bg_color,
        frame_blending=cdta_data.frame_blending,
        hide_shy_layers=cdta_data.hide_shy_layers,  # TODO check this (could be just a shy attribute)
        layers=[],
        markers=markers,
        motion_blur=cdta_data.motion_blur,
        motion_blur_adaptive_sample_limit=cdta_data.motion_blur_adaptive_sample_limit,
        motion_blur_samples_per_frame=cdta_data.motion_blur_samples_per_frame,
        preserve_nested_frame_rate=cdta_data.preserve_nested_frame_rate,
        preserve_nested_resolution=cdta_data.preserve_nested_resolution,
        shutter_angle=cdta_data.shutter_angle,
        shutter_phase=cdta_data.shutter_phase,
        resolution_factor=cdta_data.resolution_factor,
        time_scale=time_scale,

        in_point=cdta_data.in_point,
        frame_in_point=int(cdta_data.frame_in_point),
        out_point=cdta_data.out_point,
        frame_out_point=int(cdta_data.frame_out_point),
        frame_time=int(cdta_data.frame_time),
        time=cdta_data.time,
        display_start_time=cdta_data.display_start_time,
        display_start_frame=int(cdta_data.display_start_frame),
    )

    # Parse composition's layers
    layer_sub_chunks = filter_by_list_type(
        chunks=child_chunks,
        list_type="Layr"
    )
    for layer_chunk in layer_sub_chunks:
        layer = parse_layer(
            layer_chunk=layer_chunk,
            time_scale=time_scale,
        )
        layer.containing_comp_id = item_id
        composition.layers.append(layer)

    return composition


def _get_markers(child_chunks, time_scale):
    markers_layer_chunk = find_by_list_type(
        chunks=child_chunks,
        list_type="SecL"
    )
    markers_layer = parse_layer(
        layer_chunk=markers_layer_chunk,
        time_scale=time_scale,
    )
    return markers_layer.markers
