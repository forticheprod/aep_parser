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


def parse_composition(child_chunks, item_id, item_name, label, parent_folder):
    cdta_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="cdta"
    )
    cdta_data = cdta_chunk.data
    time_scale = cdta_data.time_scale

    # Parse composition's layers
    layer_sub_chunks = filter_by_list_type(
        chunks=child_chunks,
        list_type="Layr"
    )
    layers = []
    for index, layer_chunk in enumerate(layer_sub_chunks, 1):
        layer = parse_layer(
            layer_chunk=layer_chunk,
            time_scale=time_scale,
        )
        layer.index = index
        layers.append(layer)

    marker_property = _get_marker_property(
        child_chunks=child_chunks,
        time_scale=time_scale,
    )

    item = CompItem(
        item_id=item_id,
        label=label,
        name=item_name,
        type_name="Composition",
        parent_folder=parent_folder,

        duration=cdta_data.duration,
        frame_duration=int(cdta_data.frame_duration),
        frame_rate=cdta_data.frame_rate,
        height=cdta_data.height,
        pixel_aspect=cdta_data.pixel_aspect,
        width=cdta_data.width,

        bg_color=cdta_data.bg_color,
        frame_blending=cdta_data.frame_blending,
        layers=layers,
        marker_property=marker_property,
        motion_blur=cdta_data.motion_blur,
        motion_blur_adaptive_sample_limit=cdta_data.motion_blur_adaptive_sample_limit,
        motion_blur_samples_per_frame=cdta_data.motion_blur_samples_per_frame,
        preserve_nested_frame_rate=cdta_data.preserve_nested_frame_rate,
        preserve_nested_resolution=cdta_data.preserve_nested_resolution,
        shutter_angle=cdta_data.shutter_angle,
        shutter_phase=cdta_data.shutter_phase,
        resolution_factor=cdta_data.resolution_factor,
        time_scale=time_scale,

        # in_time_frames=int(cdta_data.in_time_frames),  # TODO check
        # in_time_sec=cdta_data.in_time,  # TODO check
        # out_time_frames=int(cdta_data.out_time_frames),  # TODO check
        # out_time_sec=cdta_data.out_time,  # TODO check
        # playhead_frames=int(cdta_data.playhead_frames),  # TODO check
        # playhead_sec=cdta_data.playhead_frames * cdta_data.frame_rate,  # TODO check
        # shy_enabled=cdta_data.shy_enabled,  # TODO check
    )
    return item


def _get_marker_property(child_chunks, time_scale):
    markers_layer_chunk = find_by_list_type(
        chunks=child_chunks,
        list_type="SecL"
    )
    markers_layer = parse_layer(
        layer_chunk=markers_layer_chunk,
        time_scale=time_scale,
    )
    return markers_layer.marker_property
