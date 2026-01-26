from __future__ import annotations

import typing

from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
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

if typing.TYPE_CHECKING:
    from ..kaitai.aep import Aep
    from ..models.items.composition import CompItem


def parse_layer(layer_chunk: Aep.Chunk, composition: CompItem) -> AVLayer:
    """
    Parse a composition layer.

    This layer is an instance of an item in a composition. Some information can
    only be found on the source item. To access it, use
    `source_item = project.project_items[layer.source_id]`.

    Args:
        layer_chunk: The LIST chunk to parse.
        composition: The composition.
    """
    child_chunks = layer_chunk.data.chunks

    comment = get_comment(child_chunks)

    ldta_chunk = find_by_type(chunks=child_chunks, chunk_type="ldta")
    name_chunk = find_by_type(chunks=child_chunks, chunk_type="Utf8")
    name = str_contents(name_chunk)

    ldta_data = ldta_chunk.data
    layer_type = ldta_data.layer_type
    try:
        stretch = float(ldta_data.stretch_dividend) / ldta_data.stretch_divisor
    except ZeroDivisionError:
        stretch = None

    # Maybe we need to use composition.display_start_time or
    # layer_source_item.display_start_time instead of ldta_data.start_time for
    # in_point, out_point (and display_start_frame for frame_in_point, frame_out_point)
    layer = AVLayer(
        auto_orient=ldta_data.auto_orient,
        comment=comment,
        effects=[],
        enabled=ldta_data.enabled,
        frame_in_point=int(
            round((ldta_data.start_time + ldta_data.in_point) * composition.frame_rate)
        ),
        frame_out_point=int(
            round((ldta_data.start_time + ldta_data.out_point) * composition.frame_rate)
        ),
        frame_start_time=int(round(ldta_data.start_time * composition.frame_rate)),
        in_point=ldta_data.start_time + ldta_data.in_point,
        label=ldta_data.label,
        layer_id=ldta_data.layer_id,
        layer_type=layer_type,
        locked=ldta_data.locked,
        markers=[],
        name=name,
        null_layer=ldta_data.null_layer,
        out_point=ldta_data.start_time + ldta_data.out_point,
        parent_id=ldta_data.parent_id,
        shy=ldta_data.shy,
        solo=ldta_data.solo,
        start_time=ldta_data.start_time,
        stretch=stretch,
        text=[],
        time=0,
        transform=[],
        adjustment_layer=ldta_data.adjustment_layer,
        audio_enabled=ldta_data.audio_enabled,
        blending_mode=ldta_data.blending_mode,
        collapse_transformation=ldta_data.collapse_transformation,
        effects_active=ldta_data.effects_active,
        environment_layer=ldta_data.environment_layer,
        frame_blending=ldta_data.frame_blending,
        frame_blending_type=ldta_data.frame_blending_type,
        guide_layer=ldta_data.guide_layer,
        motion_blur=ldta_data.motion_blur,
        preserve_transparency=bool(ldta_data.preserve_transparency),
        quality=ldta_data.quality,
        sampling_quality=ldta_data.sampling_quality,
        source_id=ldta_data.source_id,
        three_d_layer=ldta_data.three_d_layer,
        track_matte_type=ldta_data.track_matte_type,
    )

    root_tdgp_chunk = find_by_list_type(chunks=child_chunks, list_type="tdgp")
    tdgp_map = get_chunks_by_match_name(root_tdgp_chunk)

    # Parse transform stack
    transform_tdgp = tdgp_map.get("ADBE Transform Group", [])
    if transform_tdgp:
        transform_prop = parse_property_group(
            tdgp_chunk=transform_tdgp[0],
            group_match_name="ADBE Transform Group",
            time_scale=composition.time_scale,
        )
        layer.transform = transform_prop.properties

    # Parse effects stack
    effects_tdgp = tdgp_map.get("ADBE Effect Parade", [])
    if effects_tdgp:
        effects_prop = parse_property_group(
            tdgp_chunk=effects_tdgp[0],
            group_match_name="ADBE Effect Parade",
            time_scale=composition.time_scale,
        )
        layer.effects = effects_prop.properties

    # Parse text layer properties
    text_tdgp = tdgp_map.get("ADBE Text Properties", [])
    if text_tdgp:
        layer.text = parse_property_group(
            tdgp_chunk=text_tdgp[0],
            group_match_name="ADBE Text Properties",
            time_scale=composition.time_scale,
        )

    # Parse markers
    markers_mrst = tdgp_map.get("ADBE Marker", [])
    if markers_mrst:
        layer.markers = parse_markers(
            mrst_chunk=markers_mrst[0],
            group_match_name="ADBE Marker",
            time_scale=composition.time_scale,
        )

    return layer
