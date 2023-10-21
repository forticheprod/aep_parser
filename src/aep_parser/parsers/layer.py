from __future__ import (
    absolute_import,
    unicode_literals,
    division
)

from ..kaitai.aep import Aep
from ..kaitai.utils import (
    find_by_type,
    find_by_list_type,
    str_contents,
)
from ..models.layers.av_layer import AVLayer
from .property import (
    parse_markers,
    parse_property_group,
)
from .utils import (
    get_chunks_by_match_name,
    get_comment,
)


def parse_layer(layer_chunk, time_scale):
    # TODO add classes for different layer types (camera, etc)
    # TODO split parser for different layer types (camera, etc)
    child_chunks = layer_chunk.data.chunks
    
    comment = get_comment(child_chunks)

    ldta_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="ldta"
    )
    name_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="Utf8"
    )
    name = str_contents(name_chunk)

    ldta_data = ldta_chunk.data
    layer_type = ldta_data.layer_type
    try:
        stretch = float(ldta_data.stretch_numerator) / ldta_data.stretch_denominator
    except ZeroDivisionError:
        stretch = None

    layer = AVLayer(
        auto_orient=ldta_data.auto_orient,
        comment=comment,
        effects=[],
        enabled=ldta_data.enabled,
        in_point=ldta_data.in_point,  # TODO check if it's frames or needs to divide by time scale
        label=ldta_data.label,
        layer_id=ldta_data.layer_id,
        locked=ldta_data.locked,
        markers=[],
        name=name,
        null_layer=ldta_data.null_layer,
        out_point=ldta_data.out_point,  # TODO check if it's frames or needs to divide by time scale
        parent_id=ldta_data.parent_id,
        shy=ldta_data.shy,
        solo=ldta_data.solo,
        start_time=ldta_data.start_time,  # TODO check if it's frames or needs to divide by time scale
        stretch=stretch,
        text=[],
        time=0,  # TODO
        transform=[],
        adjustment_layer=ldta_data.adjustment_layer,
        audio_enabled=ldta_data.audio_enabled,
        blending_mode=Aep.BlendingMode(1),  # TODO
        collapse_transformation=ldta_data.collapse_transformation,
        effects_active=ldta_data.effects_active,
        environment_layer=False,  # TODO
        frame_blending=ldta_data.frame_blending,
        frame_blending_type=ldta_data.frame_blending_type,
        guide_layer=ldta_data.guide_layer,
        height=0,  # TODO
        motion_blur=ldta_data.motion_blur,
        preserve_transparency=True,  # TODO
        quality=ldta_data.quality,
        sampling_quality=ldta_data.sampling_quality,
        source_id=ldta_data.source_id,
        three_d_per_char=ldta_data.three_d_per_char,
        time_remap_enabled=False,  # TODO
        track_matte_type=ldta_data.track_matte_type,
        width=0,  # TODO
    )
    # TODO use different classes for different layer types (camera, light, etc)
    layer.layer_type = layer_type

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
        )
        layer.transform = transform_prop.properties

    # Parse effects stack
    effects_tdgp = tdgp_map.get("ADBE Effect Parade", [])
    if effects_tdgp:
        effects_prop = parse_property_group(
            tdgp_chunk=effects_tdgp[0],
            group_match_name="ADBE Effect Parade",
            time_scale=time_scale,
        )
        layer.effects = effects_prop.properties

    # Parse text layer properties
    text_tdgp = tdgp_map.get("ADBE Text Properties", [])
    if text_tdgp:
        layer.text = parse_property_group(
            tdgp_chunk=text_tdgp[0],
            group_match_name="ADBE Text Properties",
            time_scale=time_scale,
        )

    # Parse markers
    markers_mrst = tdgp_map.get("ADBE Marker", [])
    if markers_mrst:
        layer.markers = parse_markers(
            mrst_chunk=markers_mrst[0],
            group_match_name="ADBE Marker",
            time_scale=time_scale,
        )

    return layer
