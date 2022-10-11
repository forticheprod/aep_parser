from __future__ import absolute_import
from __future__ import unicode_literals


from aep_parser.kaitai.aep import Aep
from aep_parser.models.layer import Layer
from aep_parser.models.layer_quality_level import LayerQualityLevel
from aep_parser.models.layer_frame_blend_mode import LayerFrameBlendMode
from aep_parser.models.layer_sampling_mode import LayerSamplingMode
from aep_parser.property_parser import (
    parse_property,
    indexed_group_to_map,
)
from aep_parser.rifx.utils import (
    sublist_find_by_type,
    sublist_filter_by_identifier,
)


def parse_layer(layer_block):
    ldta_block = sublist_find_by_type([layer_block], Aep.ChunkType.ldta)
    if ldta_block is None:
        return
    ldta_data = ldta_block.data

    layer = Layer(
        source_id=ldta_data.source_id,
        quality=LayerQualityLevel(ldta_data.quality),
        guide_enabled=ldta_data.guide_enabled,
        frame_blend_mode=LayerFrameBlendMode(ldta_data.frame_blend_mode),
        sampling_mode=LayerSamplingMode(ldta_data.sampling_mode),
        adjustment_layer_enabled=ldta_data.adjustment_layer_enabled,
        three_d_enabled=ldta_data.three_d_enabled,
        solo_enabled=ldta_data.solo_enabled,
        video_enabled=ldta_data.video_enabled,
        audio_enabled=ldta_data.audio_enabled,
        effects_enabled=ldta_data.effects_enabled,
        motion_blur_enabled=ldta_data.motion_blur_enabled,
        frame_blend_enabled=ldta_data.frame_blend_enabled,
        lock_enabled=ldta_data.lock_enabled,
        shy_enabled=ldta_data.shy_enabled,
        collapse_transform_enabled=ldta_data.collapse_transform_enabled,
    )

    name_block = sublist_find_by_type([layer_block], Aep.ChunkType.utf8)
    if name_block is None:
        return

    layer.name = to_string(name_block.data.data)  # FIXME

    tdgp_blocks = sublist_filter_by_identifier([layer_block], "tdgp")
    root_tdgp_block = tdgp_blocks[0]
    tdgp_map, match_names = indexed_group_to_map(root_tdgp_block)

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

    return layer
