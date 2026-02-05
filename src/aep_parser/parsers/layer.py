from __future__ import annotations

import typing

from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
    get_enum_value,
    str_contents,
)
from ..models.layers.av_layer import AVLayer
from ..models.layers.camera_layer import CameraLayer
from ..models.layers.light_layer import LightLayer
from ..models.layers.shape_layer import ShapeLayer
from ..models.layers.text_layer import TextLayer
from .mappings import (
    map_auto_orient_type,
    map_blending_mode,
    map_frame_blending_type,
    map_layer_quality,
    map_layer_sampling_quality,
    map_light_type,
    map_track_matte_type,
)
from .property import (
    parse_markers,
    parse_property_group,
)
from .utils import (
    get_chunks_by_match_name,
    get_comment,
    property_has_keyframes,
)

if typing.TYPE_CHECKING:
    from ..kaitai import Aep
    from ..models.items.composition import CompItem
    from ..models.layers.layer import Layer


def parse_layer(layer_chunk: Aep.Chunk, composition: CompItem) -> Layer:
    """
    Parse a composition layer.

    This layer is an instance of an item in a composition. Some information can
    only be found on the source item. To access it, use `source_item = layer.source`.

    Args:
        layer_chunk: The LIST chunk to parse.
        composition: The composition.

    Returns:
        An AVLayer for most layers, or a LightLayer for light layers.
    """
    child_chunks = layer_chunk.data.chunks

    comment = get_comment(child_chunks)

    ldta_chunk = find_by_type(chunks=child_chunks, chunk_type="ldta")
    name_chunk = find_by_type(chunks=child_chunks, chunk_type="Utf8")
    name = str_contents(name_chunk)

    ldta_data = ldta_chunk.data
    layer_type = ldta_data.layer_type
    try:
        # ExtendScript stretch is a percentage: 100 = normal, 200 = half speed, -100 = reverse
        stretch = float(ldta_data.stretch_dividend) / ldta_data.stretch_divisor * 100
    except ZeroDivisionError:
        stretch = None

    # Calculate absolute in_point and out_point from relative binary values
    # Binary stores in_point/out_point relative to start_time
    in_point = ldta_data.start_time + ldta_data.in_point
    out_point = ldta_data.start_time + ldta_data.out_point

    # Clamp out_point to composition duration (ExtendScript behavior)
    # Layers cannot extend past the composition's end
    out_point = min(out_point, composition.duration)

    # Parse property groups early to compute time_remap_enabled
    root_tdgp_chunk = find_by_list_type(chunks=child_chunks, list_type="tdgp")
    tdgp_map = get_chunks_by_match_name(root_tdgp_chunk)

    # Time remap is enabled when "ADBE Time Remapping" property has keyframes
    time_remap_props = tdgp_map.get("ADBE Time Remapping", [])
    time_remap_enabled = (
        property_has_keyframes(time_remap_props[0]) if time_remap_props else False
    )

    # Parse transform stack
    transform_tdgp = tdgp_map.get("ADBE Transform Group", [])
    transform = []
    if transform_tdgp:
        transform_prop = parse_property_group(
            tdgp_chunk=transform_tdgp[0],
            group_match_name="ADBE Transform Group",
            time_scale=composition.time_scale,
        )
        transform = transform_prop.properties

    # Parse effects stack
    effects_tdgp = tdgp_map.get("ADBE Effect Parade", [])
    effects = []
    if effects_tdgp:
        effects_prop = parse_property_group(
            tdgp_chunk=effects_tdgp[0],
            group_match_name="ADBE Effect Parade",
            time_scale=composition.time_scale,
        )
        effects = effects_prop.properties

    # Parse text layer properties
    text_tdgp = tdgp_map.get("ADBE Text Properties", [])
    text = None
    if text_tdgp:
        text = parse_property_group(
            tdgp_chunk=text_tdgp[0],
            group_match_name="ADBE Text Properties",
            time_scale=composition.time_scale,
        )

    # Parse markers
    markers_mrst = tdgp_map.get("ADBE Marker", [])
    markers = []
    if markers_mrst:
        markers = parse_markers(
            mrst_chunk=markers_mrst[0],
            group_match_name="ADBE Marker",
            time_scale=composition.time_scale,
            frame_rate=composition.frame_rate,
        )

    # Base Layer attributes (shared by all layer types)
    layer_attrs = {
        "auto_orient": map_auto_orient_type(
            auto_orient_along_path=ldta_data.auto_orient_along_path,
            camera_or_poi_auto_orient=ldta_data.camera_or_poi_auto_orient,
            three_d_layer=ldta_data.three_d_layer,
            characters_toward_camera=ldta_data.characters_toward_camera,
        ),
        "comment": comment,
        "containing_comp": composition,
        "effects": effects,
        "enabled": ldta_data.enabled,
        "frame_in_point": int(round(in_point * composition.frame_rate)),
        "frame_out_point": int(round(out_point * composition.frame_rate)),
        "frame_start_time": int(round(ldta_data.start_time * composition.frame_rate)),
        "in_point": in_point,
        "label": ldta_data.label,
        "layer_id": ldta_data.layer_id,
        "layer_type": layer_type,
        "locked": ldta_data.locked,
        "markers": markers,
        "name": name,
        "null_layer": ldta_data.null_layer,
        "out_point": out_point,
        "parent_id": ldta_data.parent_id,
        "shy": ldta_data.shy,
        "solo": ldta_data.solo,
        "start_time": ldta_data.start_time,
        "stretch": stretch,
        "text": text,
        "time": 0,
        "transform": transform,
    }

    # Additional AVLayer attributes
    av_layer_attrs = {
        "adjustment_layer": ldta_data.adjustment_layer,
        "audio_enabled": ldta_data.audio_enabled,
        "blending_mode": map_blending_mode(get_enum_value(ldta_data.blending_mode)),
        "collapse_transformation": ldta_data.collapse_transformation,
        "effects_active": ldta_data.effects_active,
        "environment_layer": ldta_data.environment_layer,
        "frame_blending": ldta_data.frame_blending,
        "frame_blending_type": map_frame_blending_type(
            get_enum_value(ldta_data.frame_blending_type),
            ldta_data.frame_blending,
        ),
        "guide_layer": ldta_data.guide_layer,
        "motion_blur": ldta_data.motion_blur,
        "preserve_transparency": bool(ldta_data.preserve_transparency),
        "quality": map_layer_quality(get_enum_value(ldta_data.quality)),
        "sampling_quality": map_layer_sampling_quality(
            get_enum_value(ldta_data.sampling_quality)
        ),
        "source_id": ldta_data.source_id,
        "three_d_layer": ldta_data.three_d_layer,
        "time_remap_enabled": time_remap_enabled,
        "track_matte_type": map_track_matte_type(
            get_enum_value(ldta_data.track_matte_type)
        ),
    }

    # Create the appropriate layer type
    layer_type_name = getattr(layer_type, "name", None)
    if layer_type_name == "light":
        layer: Layer = LightLayer(
            **layer_attrs,
            light_type=map_light_type(get_enum_value(ldta_data.light_type)),
        )
    elif layer_type_name == "camera":
        layer = CameraLayer(**layer_attrs)
    elif layer_type_name == "shape":
        layer = ShapeLayer(**layer_attrs, **av_layer_attrs)
    elif layer_type_name == "text":
        layer = TextLayer(**layer_attrs, **av_layer_attrs)
    else:
        layer = AVLayer(**layer_attrs, **av_layer_attrs)

    return layer
