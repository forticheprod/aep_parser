from __future__ import (
    absolute_import,
    unicode_literals,
    division
)

from ..kaitai.utils import (
    find_by_type,
    find_by_list_type,
    str_contents,
)
from ..models.layer import Layer
from .property import (
    parse_markers,
    parse_property_group,
    get_chunks_by_match_name,
)


def parse_layer(layer_chunk, time_scale):
    # TODO add classes for different layer types (camera, etc)
    # TODO split parser for different layer types (camera, etc)
    child_chunks = layer_chunk.data.chunks

    ldta_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="ldta"
    )
    name_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="Utf8"
    )

    ldta_data = ldta_chunk.data

    layer = Layer(
        name=str_contents(name_chunk),
        layer_id=ldta_data.layer_id,
        quality=ldta_data.quality,
        stretch_numerator=ldta_data.stretch_numerator,
        start_time_sec=ldta_data.start_time_sec,  # TODO check
        in_time_sec=ldta_data.in_time_sec,  # TODO check
        out_time_sec=ldta_data.out_time_sec,  # TODO check
        source_id=ldta_data.source_id,
        label=ldta_data.label,
        matte_mode=ldta_data.matte_mode,
        stretch_denominator=ldta_data.stretch_denominator,
        layer_type=ldta_data.layer_type,
        parent_id=ldta_data.parent_id,

        guide_enabled=ldta_data.guide_enabled,
        frame_blend_mode=ldta_data.frame_blend_mode,
        sampling_mode=ldta_data.sampling_mode,
        auto_orient=ldta_data.auto_orient,
        adjustment_layer_enabled=ldta_data.adjustment_layer_enabled,
        three_d_enabled=ldta_data.three_d_enabled,
        solo_enabled=ldta_data.solo_enabled,
        null_layer=ldta_data.null_layer,
        video_enabled=ldta_data.video_enabled,
        audio_enabled=ldta_data.audio_enabled,
        effects_enabled=ldta_data.effects_enabled,
        motion_blur=ldta_data.motion_blur,
        frame_blending=ldta_data.frame_blending,
        lock_enabled=ldta_data.lock_enabled,
        shy_enabled=ldta_data.shy_enabled,
        collapse_transform_enabled=ldta_data.collapse_transform_enabled,
    )

    root_tdgp_chunk = find_by_list_type(
        chunks=child_chunks,
        list_type="tdgp"
    )
    tdgp_map = get_chunks_by_match_name(root_tdgp_chunk)

    # Parse transform stack
    transform_tdgp = tdgp_map.get("ADBE Transform Group", [])
    if transform_tdgp:
        transform_prop = parse_property_group(
            tdgp_chunk=transform_tdgp[0],
            group_match_name="ADBE Transform Group",
            time_scale=time_scale,
            parent_property=layer,
        )
        layer.transform = transform_prop.properties

    # Parse effects stack
    effects_tdgp = tdgp_map.get("ADBE Effect Parade", [])
    if effects_tdgp:
        effects_prop = parse_property_group(
            tdgp_chunk=effects_tdgp[0],
            group_match_name="ADBE Effect Parade",
            time_scale=time_scale,
            parent_property=layer,
        )
        layer.effects = effects_prop.properties

    # Parse text layer properties
    text_tdgp = tdgp_map.get("ADBE Text Properties", [])
    if text_tdgp:
        text_prop = parse_property_group(
            tdgp_chunk=text_tdgp[0],
            group_match_name="ADBE Text Properties",
            time_scale=time_scale,
            parent_property=layer,
        )
        layer.text = text_prop

    # Parse markers
    markers_mrst = tdgp_map.get("ADBE Marker", [])
    if markers_mrst:
        marker_property = parse_markers(
            mrst_chunk=markers_mrst[0],
            group_match_name="ADBE Marker",
            time_scale=time_scale,
            parent_property=layer,
        )
        layer.marker_property = marker_property

    
    return layer
