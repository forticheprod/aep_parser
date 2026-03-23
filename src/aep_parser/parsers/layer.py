from __future__ import annotations

import math
import typing
from typing import Any

from ..enums import (
    LightType,
    PropertyControlType,
)
from ..enums.mappings import (
    map_auto_orient_type,
)
from ..kaitai.utils import (
    ChunkNotFoundError,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.layers.av_layer import AVLayer
from ..models.layers.camera_layer import CameraLayer
from ..models.layers.light_layer import LightLayer
from ..models.layers.shape_layer import ShapeLayer
from ..models.layers.text_layer import TextLayer
from ..models.layers.three_d_model_layer import ThreeDModelLayer
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from .marker import parse_markers
from .property import parse_property_group
from .property_value import parse_property
from .utils import (
    get_chunks_by_match_name,
    get_comment,
)

if typing.TYPE_CHECKING:
    from ..kaitai import Aep
    from ..models.items.composition import CompItem
    from ..models.layers.layer import Layer


#: Sentinel value indicating an undefined source id in the binary format.
UNDEFINED_ID = 0xFFFFFFFF


# Maps layer_type.name (from ldta binary) to its ExtendScript match name.
_LAYER_MATCH_NAMES: dict[str, str] = {
    "avlayer": "ADBE AV Layer",
    "shape": "ADBE AV Layer",
    "text": "ADBE Text Layer",
    "camera": "ADBE Camera Layer",
    "light": "ADBE Light Layer",
    "three_d_model": "ADBE 3D Model Layer",
}

# Maps raw binary layer type name to ExtendScript layerType string.
_LAYER_TYPE_NAMES: dict[str, str] = {
    "avlayer": "AVLayer",
    "shape": "Layer",
    "text": "Layer",
    "camera": "CameraLayer",
    "light": "LightLayer",
    "three_d_model": "Layer",
}


def _offset_keyframe_times(
    properties: list[Property | PropertyGroup],
    start_time: float,
    frame_rate: float,
) -> None:
    """Offset all keyframe times by *start_time* (layer > comp time).

    Recursively walks the property tree and shifts `frame_time` on every
    keyframe, then recomputes `time` from the new frame number so that
    both fields are expressed in composition time.  Recomputing `time`
    from the integer `frame_time` avoids precision loss when *start_time*
    does not sit on an exact frame boundary.
    """
    frame_offset = round(start_time * frame_rate)
    for prop in properties:
        if isinstance(prop, Property) and prop.keyframes:
            for kf in prop.keyframes:
                kf.frame_time += frame_offset
                kf.time = kf.frame_time / frame_rate
                if kf.value is not None and hasattr(kf.value, "frame_time"):
                    kf.value.frame_time += frame_offset
        if isinstance(prop, PropertyGroup) and prop.properties:
            _offset_keyframe_times(prop.properties, start_time, frame_rate)


def _scale_effect_point_speeds(
    keyframes: list[Any],
    scale: list[float],
) -> None:
    """Scale temporal ease speeds after denormalizing 2D effect point values.

    The binary stores speed in normalized (0-1) units per second.
    ExtendScript reports speed in pixel units per second.  The scale
    factor depends on the direction of motion between adjacent keyframes:

        factor = |delta_pixel| / |delta_normalized|

    For BEZIER keyframes the stored speed is already non-zero and just
    needs rescaling.  LINEAR/HOLD speeds are computed later by
    `_compute_linear_hold_ease` which already sees pixel values, so
    they don't need adjustment here.
    """
    n = len(keyframes)
    for i, kf in enumerate(keyframes):
        # Compute direction factor from adjacent keyframe values.
        # Outgoing side uses direction towards next keyframe;
        # incoming side uses direction from previous keyframe.
        for ease_list, other_idx in [
            (kf.out_temporal_ease, i + 1),
            (kf.in_temporal_ease, i - 1),
        ]:
            if not ease_list or other_idx < 0 or other_idx >= n:
                continue
            other_kf = keyframes[other_idx]
            val_a = kf.value
            val_b = other_kf.value
            if (
                not isinstance(val_a, list)
                or not isinstance(val_b, list)
                or len(val_a) < 2
                or len(val_b) < 2
            ):
                continue
            # Both values are already in pixel coords at this point.
            # Compute pixel-space delta and normalized-space delta.
            delta_px = [b - a for a, b in zip(val_a, val_b)]
            delta_norm = [d / s if s else 0.0 for d, s in zip(delta_px, scale)]
            dist_px = math.sqrt(sum(d * d for d in delta_px))
            dist_norm = math.sqrt(sum(d * d for d in delta_norm))
            if dist_norm == 0:
                continue
            factor = dist_px / dist_norm
            for ease in ease_list:
                ease.speed *= factor


def _denormalize_effect_points(
    properties: list[Property | PropertyGroup],
    width: int,
    height: int,
    in_effect: bool = False,
) -> None:
    """Scale normalized 0-1 effect point values to pixel coordinates.

    Effect point properties (PropertyControlType.TWO_D) inside effects
    store 2D values as fractions of composition dimensions.  ExtendScript
    reports them as absolute pixel coordinates.  This function multiplies
    static values and keyframe values by `[width, height]`.

    Temporal ease speeds for spatial 2D effect properties are also
    scaled.  The binary stores speed in normalized units/second;
    ExtendScript reports pixels/second.  The scale factor depends on
    the direction of motion between adjacent keyframes.
    """
    scale = [float(width), float(height)]
    for prop in properties:
        is_effect = getattr(prop, "is_effect", False)
        child_in_effect = in_effect or is_effect
        if (
            child_in_effect
            and isinstance(prop, Property)
            and prop.property_control_type == PropertyControlType.TWO_D
        ):
            if isinstance(prop.value, list) and len(prop.value) >= 2:
                prop.value = [v * s for v, s in zip(prop.value, scale)]
            for kf in prop.keyframes:
                if isinstance(kf.value, list) and len(kf.value) >= 2:
                    kf.value = [v * s for v, s in zip(kf.value, scale)]
            _scale_effect_point_speeds(prop.keyframes, scale)
        if isinstance(prop, PropertyGroup) and prop.properties:
            _denormalize_effect_points(prop.properties, width, height, child_in_effect)


def _parse_layer_property_groups(
    child_chunks: list[Aep.Chunk],
    composition: CompItem,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    layer_id_to_index: dict[int, int] | None,
) -> list[Property | PropertyGroup]:
    """Parse all property groups for a layer.

    Iterates all named property groups in binary order and returns them as a
    flat list, including markers and leaf properties like Time Remap.

    Args:
        child_chunks: The layer's child chunks.
        composition: The parent composition.
        effect_param_defs: Project-level effect parameter definitions, used as
            fallback when layer-level parT chunks are missing.
        layer_id_to_index: Mapping from binary layer IDs to 1-based layer
            indices, used to resolve LAYER_INDEX property values.

    Returns:
        Ordered list of all top-level properties and property groups.
    """
    root_tdgp_chunk = find_by_list_type(chunks=child_chunks, list_type="tdgp")
    tdgp_map = get_chunks_by_match_name(root_tdgp_chunk)

    properties: list[Property | PropertyGroup] = []
    for match_name, sub_chunks in tdgp_map.items():
        try:
            first_list = find_by_type(chunks=sub_chunks, chunk_type="LIST")
        except ChunkNotFoundError:
            continue
        if first_list.body.list_type == "tdgp":
            prop_group = parse_property_group(
                tdgp_chunk=first_list,
                group_match_name=match_name,
                time_scale=composition.time_scale,
                property_depth=1,
                effect_param_defs=effect_param_defs,
                frame_rate=composition.frame_rate,
                comp_size=(composition.width, composition.height),
                layer_id_to_index=layer_id_to_index,
            )
            properties.append(prop_group)
        elif first_list.body.list_type == "tdbs":
            # Leaf property at layer level (e.g. Time Remap)
            prop = parse_property(
                tdbs_chunk=first_list,
                match_name=match_name,
                time_scale=composition.time_scale,
                property_depth=1,
                frame_rate=composition.frame_rate,
            )
            properties.append(prop)
        elif first_list.body.list_type == "mrst":
            # Marker property
            marker_prop = parse_markers(
                mrst_chunk=first_list,
                time_scale=composition.time_scale,
                frame_rate=composition.frame_rate,
            )
            properties.append(marker_prop)

    return properties


def parse_layer(
    layer_chunk: Aep.Chunk,
    composition: CompItem,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    layer_id_to_index: dict[int, int] | None = None,
) -> Layer:
    """
    Parse a composition layer.

    This layer is an instance of an item in a composition. Some information can
    only be found on the source item. To access it, use `source_item = layer.source`.

    Args:
        layer_chunk: The LIST chunk to parse.
        composition: The composition.
        effect_param_defs: Project-level effect parameter definitions, used as
            fallback when layer-level parT chunks are missing.
        layer_id_to_index: Mapping from binary layer IDs to 1-based layer
            indices, used to resolve LAYER_INDEX property values.

    Returns:
        An [AVLayer][] for most layers, or a [LightLayer][] for light layers.
    """
    child_chunks = layer_chunk.body.chunks

    comment = get_comment(child_chunks)

    ldta_chunk = find_by_type(chunks=child_chunks, chunk_type="ldta")

    name_chunk = find_by_type(chunks=child_chunks, chunk_type="Utf8")
    name = str_contents(name_chunk)

    layer_type_name = ldta_chunk.body.layer_type.name

    properties = _parse_layer_property_groups(
        child_chunks, composition, effect_param_defs, layer_id_to_index
    )

    # Adjust keyframe times from layer-relative to composition-relative
    # time.  Binary keyframe times are stored relative to the layer;
    # ExtendScript reports them in comp time.
    start_time: float = ldta_chunk.body.start_time
    if start_time != 0.0:
        _offset_keyframe_times(properties, start_time, composition.frame_rate)

    # Denormalize effect point values from 0-1 fractions to pixel coordinates.
    _denormalize_effect_points(properties, composition.width, composition.height)

    layer_attrs = {
        "_ldta": ldta_chunk.body,
        "match_name": _LAYER_MATCH_NAMES.get(layer_type_name, "ADBE AV Layer"),
        "name": name,
        "properties": properties,
        "auto_orient": map_auto_orient_type(
            auto_orient_along_path=ldta_chunk.body.auto_orient_along_path,
            camera_or_poi_auto_orient=ldta_chunk.body.camera_or_poi_auto_orient,
            three_d_layer=ldta_chunk.body.three_d_layer,
            characters_toward_camera=ldta_chunk.body.characters_toward_camera,
            three_d_per_char=ldta_chunk.body.three_d_per_char,
        ),
        "comment": comment,
        "containing_comp": composition,
        "layer_type": _LAYER_TYPE_NAMES.get(layer_type_name, "AVLayer"),
    }

    av_layer_attrs = {
        "_matte_layer_id": getattr(ldta_chunk.body, "matte_layer_id", 0) or 0,
    }

    layer: Layer
    if layer_type_name == "light":
        light_source_id = ldta_chunk.body.source_id
        layer = LightLayer(
            **layer_attrs,  # type: ignore[arg-type]
            light_type=LightType.from_binary(ldta_chunk.body.light_type),
            _light_source_id=light_source_id if light_source_id != UNDEFINED_ID else 0,
        )
    elif layer_type_name == "camera":
        layer = CameraLayer(**layer_attrs)  # type: ignore[arg-type]
    elif layer_type_name == "shape":
        layer = ShapeLayer(**layer_attrs, **av_layer_attrs)  # type: ignore[arg-type]
    elif layer_type_name == "text":
        layer = TextLayer(**layer_attrs, **av_layer_attrs)  # type: ignore[arg-type]
    elif layer_type_name == "three_d_model":
        layer = ThreeDModelLayer(**layer_attrs, **av_layer_attrs)  # type: ignore[arg-type]
    else:
        layer = AVLayer(**layer_attrs, **av_layer_attrs)  # type: ignore[arg-type]

    return layer
