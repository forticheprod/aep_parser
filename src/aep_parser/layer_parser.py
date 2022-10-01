from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function


from aep_parser.models.layer import Layer
from aep_parser.models.layer_frame_blend_mode import LayerFrameBlendMode
from aep_parser.models.layer_sampling_mode import LayerSamplingMode
from aep_parser.models.ldta import LDTA
from aep_parser.property_parser import (
    parse_property,
    indexed_group_to_map,
)
from aep_parser.rifx.utils import (
    find_by_type,
    sublist_merge,
)


def parse_layer(layer_block):
    layer = Layer()

    ldta_block = find_by_type(layer_block, "ldta")
    if ldta_block is None:
        return None

    ldta = LDTA(
        unknown01=ldta_block.unknown01,
        quality=ldta_block.quality,
        unknown02=ldta_block.unknown02,
        layer_attr_bits=ldta_block.layer_attr_bits,
        source_id=ldta_block.source_id
    )
    layer.source_id = ldta.source_id
    layer.quality = ldta.quality
    layer.sampling_mode = LayerSamplingMode((ldta.layer_attr_bits[0] & (1 << 6)) >> 6)
    layer.frame_blend_mode = LayerFrameBlendMode((ldta.layer_attr_bits[0] & (1 << 2)) >> 2)
    layer.guide_enabled = ((ldta.layer_attr_bits[0] & (1 << 1)) >> 1) == 1
    layer.solo_enabled = ((ldta.layer_attr_bits[1] & (1 << 3)) >> 3) == 1
    layer.three_d_enabled = ((ldta.layer_attr_bits[1] & (1 << 2)) >> 2) == 1
    layer.adjustment_layer_enabled = ((ldta.layer_attr_bits[1] & (1 << 1)) >> 1) == 1
    layer.collapse_transform_enabled = ((ldta.layer_attr_bits[2] & (1 << 7)) >> 7) == 1
    layer.shy_enabled = ((ldta.layer_attr_bits[2] & (1 << 6)) >> 6) == 1
    layer.lock_enabled = ((ldta.layer_attr_bits[2] & (1 << 5)) >> 5) == 1
    layer.frame_blend_enabled = ((ldta.layer_attr_bits[2] & (1 << 4)) >> 4) == 1
    layer.motion_blur_enabled = ((ldta.layer_attr_bits[2] & (1 << 3)) >> 3) == 1
    layer.effects_enabled = ((ldta.layer_attr_bits[2] & (1 << 2)) >> 2) == 1
    layer.audio_enabled = ((ldta.layer_attr_bits[2] & (1 << 1)) >> 1) == 1
    layer.video_enabled = ((ldta.layer_attr_bits[2] & (1 << 0)) >> 0) == 1

    name_block = find_by_type(layer_block, "Utf8")
    if name_block is None:
        return None

    layer.name = name_block  # TODO .data ? str() ?

    root_tdgp = indexed_group_to_map(sublist_merge(layer_block, "tdgp"))

    # Parse effects stack
    effects_tdgp = root_tdgp["ADBE Effect Parade"]
    if effects_tdgp is not None:
        effects_prop = parse_property(effects_tdgp, "ADBE Effect Parade")
        if effects_prop is None:
            return None
        layer.effects = effects_prop.properties
    else:
        layer.effects = []

    # Parse text layer properties
    text_tdgp = root_tdgp["ADBE Text Properties"]
    if text_tdgp is not None:
        text_prop = parse_property(text_tdgp, "ADBE Text Properties")
        if text_prop is None:
            return None
        layer.Text = text_prop

    return layer
