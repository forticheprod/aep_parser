from __future__ import absolute_import
from __future__ import unicode_literals


from .kaitai.aep import Aep
from .models.layer import Layer
from .models.layer_quality_level import LayerQualityLevel
from .models.layer_frame_blend_mode import LayerFrameBlendMode
from .models.layer_sampling_mode import LayerSamplingMode
from .property_parser import (
    parse_property,
    get_properties,
)
from .rifx.utils import (
    find_by_type,
    find_by_identifier,
    str_contents,
)


def parse_layer(layer_chunk):
    child_chunks = layer_chunk.data.chunks

    ldta_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="ldta"
    )
    if ldta_chunk is None:
        print(
            "could not find ldta for chunk {layer_chunk}"
            .format(layer_chunk=layer_chunk)
        )
        return

    name_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="Utf8"
    )
    if name_chunk is None:
        print(
            "could not find name for chunk {layer_chunk}"
            .format(layer_chunk=layer_chunk)
        )
        return

    ldta_data = ldta_chunk.data

    layer = Layer(
        name=str_contents(name_chunk),
        layer_id=ldta_data.layer_id,
        quality=LayerQualityLevel(ldta_data.quality),
        start_time_sec=ldta_data.start_time,
        in_time_sec=ldta_data.in_time,
        out_time_sec=ldta_data.out_time,  # TODO check
        source_id=ldta_data.source_id,
        label_color=Aep.LabelColor(ldta_data.label_color),
        matte_mode=Aep.MatteMode(ldta_data.matte_mode),
        layer_type=Aep.LayerType(ldta_data.layer_type),
        parent_id=ldta_data.parent_id,
        guide_enabled=ldta_data.guide_enabled,
        frame_blend_mode=LayerFrameBlendMode(ldta_data.frame_blend_mode),
        sampling_mode=LayerSamplingMode(ldta_data.sampling_mode),
        auto_orient=ldta_data.auto_orient,
        adjustment_layer_enabled=ldta_data.adjustment_layer_enabled,
        three_d_enabled=ldta_data.three_d_enabled,
        solo_enabled=ldta_data.solo_enabled,
        null_layer=ldta_data.null_layer,
        video_enabled=ldta_data.video_enabled,
        audio_enabled=ldta_data.audio_enabled,
        effects_enabled=ldta_data.effects_enabled,
        motion_blur_enabled=ldta_data.motion_blur_enabled,
        frame_blend_enabled=ldta_data.frame_blend_enabled,
        lock_enabled=ldta_data.lock_enabled,
        shy_enabled=ldta_data.shy_enabled,
        collapse_transform_enabled=ldta_data.collapse_transform_enabled,
    )

    root_tdgp_chunk = find_by_identifier(
        chunks=child_chunks,
        identifier="tdgp"
    )
    if root_tdgp_chunk is None:
        print(
            "could not find tdgp for chunk {layer_chunk}"
            .format(layer_chunk=layer_chunk)
        )
        return
    tdgp_map = get_properties(root_tdgp_chunk)

    # Parse transform stack
    transform_tdgp = tdgp_map.get("ADBE Transform Group")
    if transform_tdgp is not None:
        transform_prop = parse_property(transform_tdgp, "ADBE Transform Group")
        if transform_prop is None:
            return
        layer.transform = transform_prop.properties

    # Parse effects stack
    effects_tdgp = tdgp_map.get("ADBE Effect Parade")
    if effects_tdgp is not None:
        effects_prop = parse_property(effects_tdgp, "ADBE Effect Parade")
        if effects_prop is None:
            return
        layer.effects = effects_prop.properties

    # Parse text layer properties
    text_tdgp = tdgp_map.get("ADBE Text Properties")
    if text_tdgp is not None:
        text_prop = parse_property(text_tdgp, "ADBE Text Properties")
        if text_prop is None:
            return
        layer.text = text_prop

    # Parse markers
    markers_tdgp = tdgp_map.get("ADBE Marker")
    if markers_tdgp is not None:
        markers_prop = parse_property(markers_tdgp, "ADBE Marker")
        if markers_prop is None:
            return
        layer.markers = markers_prop

    
    return layer
