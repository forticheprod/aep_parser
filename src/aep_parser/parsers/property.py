"""Property group, effect, mask, orientation, shape, and text parsers."""

from __future__ import annotations

import io
import logging
import struct
from contextlib import suppress
from typing import Any

from ..cos import CosParser
from ..enums import (
    PropertyControlType,
    PropertyType,
    PropertyValueType,
)
from ..kaitai import Aep
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.properties.mask_property_group import MaskPropertyGroup
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from ..models.properties.shape import FeatherPoint, Shape
from .match_names import MATCH_NAME_TO_NICE_NAME
from .property_value import (
    get_user_defined_name,
    parse_property,
)
from .text import parse_btdk_cos
from .utils import (
    get_chunks_by_match_name,
)

logger = logging.getLogger(__name__)

# Match names that correspond to indexed groups in After Effects.
INDEXED_GROUP_MATCH_NAMES = {
    "ADBE Effect Parade",
    "ADBE Mask Parade",
    "ADBE Effect Mask Parade",
}


def parse_property_group(
    tdgp_chunk: Aep.Chunk,
    group_match_name: str,
    time_scale: float,
    property_depth: int,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    frame_rate: float,
    comp_size: tuple[int, int],
    layer_id_to_index: dict[int, int] | None,
) -> PropertyGroup:
    """
    Parse a property group.

    Args:
        tdgp_chunk: The TDGP chunk to parse.
        group_match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized. An indexed group
            (`PropertyBase.property_type == PropertyType.indexed_group`)
            may not have a name value, but always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        property_depth: The nesting depth of this group (0 = layer level).
        effect_param_defs: Project-level effect parameter definitions, used as
            fallback when layer-level parT chunks are missing.
        frame_rate: The frame rate of the parent composition.
        comp_size: `(width, height)` of the parent composition in pixels.
        layer_id_to_index: Mapping from binary layer IDs to 1-based layer
            indices, used to resolve LAYER_INDEX property values.
    """
    name = MATCH_NAME_TO_NICE_NAME.get(group_match_name, group_match_name)
    child_depth = property_depth + 1

    properties: list[Property | PropertyGroup] = []
    chunks_by_sub_prop = get_chunks_by_match_name(tdgp_chunk)
    for match_name, sub_prop_chunks in chunks_by_sub_prop.items():
        # Find the first LIST chunk; non-LIST chunks (e.g. mkif for masks)
        # are auxiliary data that we skip when determining the property type.
        try:
            first_chunk = find_by_type(chunks=sub_prop_chunks, chunk_type="LIST")
        except ChunkNotFoundError:
            continue
        # Effects can share a match name when the same effect type is applied
        # multiple times. Iterate all LIST chunks for sspc and tdgp; other
        # types use the first chunk (additional chunks are auxiliary data).
        if first_chunk.data.list_type == "sspc":
            for chunk in filter_by_list_type(chunks=sub_prop_chunks, list_type="sspc"):
                sub_prop: Property | PropertyGroup = parse_effect(
                    sspc_chunk=chunk,
                    group_match_name=match_name,
                    time_scale=time_scale,
                    property_depth=child_depth,
                    effect_param_defs=effect_param_defs,
                    frame_rate=frame_rate,
                    comp_size=comp_size,
                    layer_id_to_index=layer_id_to_index,
                )
                properties.append(sub_prop)
        elif first_chunk.data.list_type == "tdgp":
            if match_name == "ADBE Mask Atom":
                # Pair each mask tdgp chunk with its mkif (mask info) chunk
                for tdgp_c, mkif_c in zip(
                    filter_by_list_type(chunks=sub_prop_chunks, list_type="tdgp"),
                    filter_by_type(chunks=sub_prop_chunks, chunk_type="mkif"),
                ):
                    sub_prop = _parse_mask_atom(
                        tdgp_chunk=tdgp_c,
                        mkif_chunk=mkif_c,
                        time_scale=time_scale,
                        property_depth=child_depth,
                        effect_param_defs=effect_param_defs,
                        frame_rate=frame_rate,
                        comp_size=comp_size,
                        layer_id_to_index=layer_id_to_index,
                    )
                    properties.append(sub_prop)
                # Append 1-based index to mask names (e.g. "Mask 1", "Mask 2")
                mask_count = 0
                for p in properties:
                    if isinstance(p, MaskPropertyGroup):
                        mask_count += 1
                        p.name = f"Mask {mask_count}"
            else:
                # Indexed groups (e.g. effects) can share a match name.
                for tdgp_c in filter_by_list_type(
                    chunks=sub_prop_chunks, list_type="tdgp"
                ):
                    sub_prop = parse_property_group(
                        tdgp_chunk=tdgp_c,
                        group_match_name=match_name,
                        time_scale=time_scale,
                        property_depth=child_depth,
                        effect_param_defs=effect_param_defs,
                        frame_rate=frame_rate,
                        comp_size=comp_size,
                        layer_id_to_index=layer_id_to_index,
                    )
                    properties.append(sub_prop)
        elif first_chunk.data.list_type == "tdbs":
            sub_prop = parse_property(
                tdbs_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                frame_rate=frame_rate,
                layer_id_to_index=layer_id_to_index,
            )
            properties.append(sub_prop)
        elif first_chunk.data.list_type == "otst":
            sub_prop = parse_orientation(
                otst_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                frame_rate=frame_rate,
            )
            properties.append(sub_prop)
        elif first_chunk.data.list_type == "btds":
            sub_prop = parse_text_document(
                btds_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                frame_rate=frame_rate,
            )
            properties.append(sub_prop)
        elif first_chunk.data.list_type == "om-s":
            sub_prop = parse_shape(
                oms_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                frame_rate=frame_rate,
                comp_size=comp_size,
            )
            properties.append(sub_prop)
        else:
            logger.warning(
                "Skipping unsupported property list type '%s' (match name '%s')",
                first_chunk.data.list_type,
                match_name,
            )

    # Try to read the group-level enabled flag from its tdsb chunk.
    # Leaf properties always have a tdsb; groups may or may not.
    group_enabled = True
    with suppress(ChunkNotFoundError):
        group_tdsb = find_by_type(chunks=tdgp_chunk.data.chunks, chunk_type="tdsb")
        group_enabled = group_tdsb.data.enabled

    prop_group = PropertyGroup(
        enabled=group_enabled,
        match_name=group_match_name,
        name=name,
        property_depth=property_depth,
        properties=properties,
    )

    # Set parent reference on all children
    for child in properties:
        child.parent_property = prop_group

    # Mark indexed groups
    if group_match_name in INDEXED_GROUP_MATCH_NAMES:
        prop_group.property_type = PropertyType.INDEXED_GROUP

    # Mark special group types
    if group_match_name == "ADBE Effect Mask Parade":
        prop_group.elided = True
    return prop_group


def _parse_mask_atom(
    tdgp_chunk: Aep.Chunk,
    mkif_chunk: Aep.Chunk,
    time_scale: float,
    property_depth: int,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    frame_rate: float,
    comp_size: tuple[int, int],
    layer_id_to_index: dict[int, int] | None,
) -> MaskPropertyGroup:
    """Parse a mask atom into a MaskPropertyGroup.

    Combines the child properties from the tdgp chunk with the mask-specific
    attributes (inverted, locked, mask_mode, color, mask_feather_falloff,
    mask_motion_blur) parsed from the mkif chunk, and the rotoBezier flag
    from the ADBE Mask Shape tdsb chunk.

    Args:
        tdgp_chunk: The tdgp chunk for this mask atom.
        mkif_chunk: The mkif (mask info) chunk containing mask attributes.
        time_scale: The time scale of the parent composition.
        property_depth: The nesting depth of this group.
        effect_param_defs: Project-level effect parameter definitions.
        frame_rate: The frame rate of the parent composition.
        comp_size: `(width, height)` of the parent composition in pixels.
        layer_id_to_index: Mapping from binary layer IDs to 1-based layer
            indices, used to resolve LAYER_INDEX property values.
    """
    from ..enums import MaskFeatherFalloff, MaskMode, MaskMotionBlur

    base = parse_property_group(
        tdgp_chunk=tdgp_chunk,
        group_match_name="ADBE Mask Atom",
        time_scale=time_scale,
        property_depth=property_depth,
        effect_param_defs=effect_param_defs,
        frame_rate=frame_rate,
        comp_size=comp_size,
        layer_id_to_index=layer_id_to_index,
    )

    # Extract rotoBezier from ADBE Mask Shape tdsb (byte 0).
    roto_bezier = False
    chunks_by_mn = get_chunks_by_match_name(tdgp_chunk)
    mask_shape_chunks = chunks_by_mn.get("ADBE Mask Shape", [])
    for chunk in mask_shape_chunks:
        if chunk.chunk_type == "LIST" and chunk.data.list_type == "om-s":
            with suppress(ChunkNotFoundError):
                tdbs = find_by_list_type(chunks=chunk.data.chunks, list_type="tdbs")
                tdsb = find_by_type(chunks=tdbs.data.chunks, chunk_type="tdsb")
                roto_bezier = bool(tdsb.data.roto_bezier)
            break

    mask_group = MaskPropertyGroup(
        enabled=base.enabled,
        match_name=base.match_name,
        name=base.name,
        property_depth=base.property_depth,
        properties=base.properties,
        color=[
            mkif_chunk.data.color_red / 255.0,
            mkif_chunk.data.color_green / 255.0,
            mkif_chunk.data.color_blue / 255.0,
        ],
        inverted=bool(mkif_chunk.data.inverted),
        locked=bool(mkif_chunk.data.locked),
        mask_feather_falloff=MaskFeatherFalloff.from_binary(
            int(mkif_chunk.data.mask_feather_falloff)
        ),
        mask_mode=MaskMode.from_binary(int(mkif_chunk.data.mode)),
        mask_motion_blur=MaskMotionBlur.from_binary(
            int(mkif_chunk.data.mask_motion_blur)
        ),
        roto_bezier=roto_bezier,
    )
    mask_group.property_type = base.property_type
    mask_group.is_mask = True
    # Fix parent references so children point to the new mask_group
    for child in mask_group.properties:
        child.parent_property = mask_group
    return mask_group


def parse_orientation(
    otst_chunk: Aep.Chunk,
    match_name: str,
    time_scale: float,
    property_depth: int,
    frame_rate: float,
) -> Property:
    """
    Parse an orientation property.

    Args:
        otst_chunk: The OTST chunk to parse.
        match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        property_depth: The nesting depth of this property (0 = layer level).
        frame_rate: The frame rate of the parent composition.
    """
    tdbs_chunk = find_by_list_type(chunks=otst_chunk.data.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
        property_depth=property_depth,
        frame_rate=frame_rate,
    )
    # Orientation uses an angle dial control.  ExtendScript reports
    # propertyValueType as ThreeD_SPATIAL and isSpatial as True, even
    # though the binary stores is_spatial=False.
    prop.property_control_type = PropertyControlType.ANGLE
    prop.property_value_type = PropertyValueType.ThreeD_SPATIAL
    prop.is_spatial = True
    prop.dimensions = 3
    prop.vector = True

    # The cdat inside OTST stores doubles as little-endian, unlike the
    # rest of the big-endian RIFX file.  Re-read the raw bytes as LE.
    try:
        cdat_chunk = find_by_type(chunks=tdbs_chunk.data.chunks, chunk_type="cdat")
        n = cdat_chunk.len_data // 8
        values = list(struct.unpack(f"<{n}d", cdat_chunk._raw_data))
        while len(values) < 3:
            values.append(0.0)
        prop.value = values[:3]
    except ChunkNotFoundError:
        prop.value = None

    # Animated orientation keyframes store their 3-component values
    # in otky > otda chunks (big-endian, one otda per keyframe),
    # a sibling of tdbs inside otst.  The standard _parse_keyframes()
    # reads from tdbs which only has 1D orientation data, so we
    # override each keyframe's value with the full 3D otda data.
    try:
        otky_chunk = find_by_list_type(chunks=otst_chunk.data.chunks, list_type="otky")
        otda_chunks = filter_by_type(chunks=otky_chunk.data.chunks, chunk_type="otda")
        for idx, kf in enumerate(prop.keyframes):
            if idx < len(otda_chunks):
                n = otda_chunks[idx].len_data // 8
                kf.value = list(struct.unpack(f">{n}d", otda_chunks[idx]._raw_data))
    except ChunkNotFoundError:
        pass

    return prop


def _parse_shape_shap(
    shap_chunk: Aep.Chunk,
    comp_size: tuple[int, int],
    is_mask_shape: bool,
) -> Shape:
    """Parse a single shape path from a `shap` LIST chunk.

    Each `shap` LIST contains:
    - `shph` chunk: shape header with closed flag and bounding box
    - `list` LIST:  contains `lhd3` (point count/size) and `ldat`
      (raw normalized bezier points)

    Points in `ldat` are stored as big-endian `(f4 x, f4 y)` pairs,
    normalized to the `[0, 1]` range of the bounding box.  Every three
    consecutive points form a cycle:
    `vertex, out_tangent, in_tangent_of_next_vertex`.

    Mask shapes use a normalized `[0, 1]` bounding box, so the
    resulting coordinates must be scaled by `comp_size` to get pixel
    values.  Shape-layer paths already have a pixel bounding box.

    Args:
        shap_chunk: A `shap` LIST chunk.
        comp_size: `(width, height)` of the containing composition,
            used for denormalizing mask shapes.
        is_mask_shape: Whether this shape belongs to a mask property.

    Returns:
        A [Shape][] with absolute coordinates and tangent offsets.
    """
    shph_chunk = find_by_type(chunks=shap_chunk.data.chunks, chunk_type="shph")
    list_chunk = find_by_list_type(chunks=shap_chunk.data.chunks, list_type="list")

    # Bounding box from shape header
    tl_x = shph_chunk.data.top_left_x
    tl_y = shph_chunk.data.top_left_y
    br_x = shph_chunk.data.bottom_right_x
    br_y = shph_chunk.data.bottom_right_y
    closed = shph_chunk.data.closed

    # Read raw bezier points from ldat
    lhd3 = find_by_type(chunks=list_chunk.data.chunks, chunk_type="lhd3")
    ldat = find_by_type(chunks=list_chunk.data.chunks, chunk_type="ldat")

    point_count = lhd3.data.count
    raw_bytes = ldat.data.items

    # Parse (f4 x, f4 y) pairs - big-endian
    points: list[tuple[float, float]] = []
    for i in range(point_count):
        offset = i * 8
        px, py = struct.unpack_from(">ff", raw_bytes, offset)
        points.append((px, py))

    # De-interleave into vertex / out_tangent / in_tangent triples.
    # Raw order per cycle of 3:  vertex, out_tangent, in_tangent_of_next
    # Following python-lottie:
    #   vertex      = points[i]
    #   out_tangent = points[i + 1]
    #   in_tangent  = points[(i - 1) % len(points)]
    vertices: list[list[float]] = []
    in_tangents: list[list[float]] = []
    out_tangents: list[list[float]] = []

    for i in range(0, len(points), 3):
        vx = tl_x * (1 - points[i][0]) + br_x * points[i][0]
        vy = tl_y * (1 - points[i][1]) + br_y * points[i][1]

        ox = tl_x * (1 - points[i + 1][0]) + br_x * points[i + 1][0]
        oy = tl_y * (1 - points[i + 1][1]) + br_y * points[i + 1][1]

        in_idx = (i - 1) % len(points)
        ix = tl_x * (1 - points[in_idx][0]) + br_x * points[in_idx][0]
        iy = tl_y * (1 - points[in_idx][1]) + br_y * points[in_idx][1]

        vertices.append([vx, vy])
        # Tangents as offsets relative to vertex
        in_tangents.append([ix - vx, iy - vy])
        out_tangents.append([ox - vx, oy - vy])

    # Mask shapes use a [0, 1] bounding box; scale to pixel coordinates.
    if is_mask_shape:
        w, h = float(comp_size[0]), float(comp_size[1])
        vertices = [[x * w, y * h] for x, y in vertices]
        in_tangents = [[x * w, y * h] for x, y in in_tangents]
        out_tangents = [[x * w, y * h] for x, y in out_tangents]

    return Shape(
        closed=closed,
        vertices=vertices,
        in_tangents=in_tangents,
        out_tangents=out_tangents,
        feather_points=_parse_feather_points(shap_chunk),
    )


def _parse_feather_points(shap_chunk: Aep.Chunk) -> list[FeatherPoint]:
    """Extract variable-width mask feather data from a `fth5` chunk.

    Args:
        shap_chunk: The `shap` LIST chunk that may contain `fth5`.

    Returns:
        List of [FeatherPoint][] instances (empty if no `fth5`).
    """
    try:
        fth5 = find_by_type(chunks=shap_chunk.data.chunks, chunk_type="fth5")
    except ChunkNotFoundError:
        return []

    points: list[FeatherPoint] = []
    for pt in fth5.data.points:
        points.append(
            FeatherPoint(
                seg_loc=int(pt.seg_loc),
                rel_seg_loc=float(pt.rel_seg_loc),
                radius=float(pt.radius),
                type=1 if pt.radius < 0 else 0,
                interp=1 if pt.interp_raw == 2 else 0,
                tension=float(pt.tension),
                rel_corner_angle=float(pt.corner_angle),
            )
        )
    return points


def parse_shape(
    oms_chunk: Aep.Chunk,
    match_name: str,
    time_scale: float,
    property_depth: int,
    frame_rate: float,
    comp_size: tuple[int, int],
) -> Property:
    """Parse a shape/mask-path property from an `om-s` LIST chunk.

    An `om-s` LIST contains:
    - `tdbs` LIST: standard property metadata (timing, keyframes, etc.)
    - `omks` LIST: shape keyframe values (one `shap` per keyframe,
      or one `shap` for static shapes)

    Args:
        oms_chunk: The `om-s` LIST chunk to parse.
        match_name: The property match name.
        time_scale: Time scale divisor of the parent composition.
        property_depth: Nesting depth of this property.
        frame_rate: The frame rate of the parent composition.

    Returns:
        A [Property][] with `property_value_type` set to
        [SHAPE][aep_parser.enums.PropertyValueType.SHAPE] and `value`
        set to a [Shape][].
    """
    tdbs_chunk = find_by_list_type(chunks=oms_chunk.data.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
        property_depth=property_depth,
        frame_rate=frame_rate,
    )

    prop.property_value_type = PropertyValueType.SHAPE
    prop.is_spatial = True
    # Shape properties always carry a value (from omks), even though
    # tdb4 may report no_value=True (there is no cdat for shapes).
    prop.no_value = False

    # Collect shape values from omks > shap LISTs
    try:
        omks_chunk = find_by_list_type(chunks=oms_chunk.data.chunks, list_type="omks")
        shape_values: list[Shape] = []
        is_mask = match_name == "ADBE Mask Shape"
        for shap_chunk in filter_by_list_type(
            chunks=omks_chunk.data.chunks, list_type="shap"
        ):
            shape_values.append(_parse_shape_shap(shap_chunk, comp_size, is_mask))
    except (ChunkNotFoundError, Exception):
        logger.debug("Could not parse omks shape data for %s", match_name)
        return prop

    # Assign static value (first shape).  Set an empty Shape as default
    # so that is_modified detects any real mask path as modified.
    prop.default_value = Shape(
        closed=False,
        vertices=[],
        in_tangents=[],
        out_tangents=[],
    )
    if shape_values:
        prop.value = shape_values[0]

    # Assign shape values to keyframes by index
    for idx, kf in enumerate(prop.keyframes):
        if idx < len(shape_values):
            kf.value = shape_values[idx]

    return prop


def parse_text_document(
    btds_chunk: Aep.Chunk,
    match_name: str,
    time_scale: float,
    property_depth: int,
    frame_rate: float,
) -> Property:
    """
    Parse a text document property.

    Args:
        btds_chunk: The BTDS chunk to parse.
        match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        property_depth: The nesting depth of this property (0 = layer level).
        frame_rate: The frame rate of the parent composition.
    """
    tdbs_chunk = find_by_list_type(chunks=btds_chunk.data.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
        property_depth=property_depth,
        frame_rate=frame_rate,
    )

    try:
        btdk_chunk = find_by_list_type(
            chunks=btds_chunk.data.chunks,
            list_type="btdk",
        )
        parser = CosParser(
            io.BytesIO(btdk_chunk.data.binary_data),
            len(btdk_chunk.data.binary_data),
        )
        cos_data = parser.parse()
        if not isinstance(cos_data, dict):
            raise TypeError("Expected dict from COS parser")
        text_documents, _fonts = parse_btdk_cos(cos_data)
        if text_documents:
            prop.value = text_documents[0]
    except (ChunkNotFoundError, Exception):
        logger.debug("Could not parse btdk COS data for %s", match_name)

    return prop


def parse_effect_param_defs(
    sspc_child_chunks: list[Aep.Chunk],
) -> dict[str, dict[str, Any]]:
    """Parse effect parameter definitions from parT chunk.

    Each effect has a parT LIST containing parameter definitions that
    describe the control type, default values, and ranges.

    Args:
        sspc_child_chunks: The SSPC chunk's child chunks.

    Returns:
        Dict mapping parameter match names to definition dicts.
    """
    part_chunk = find_by_list_type(chunks=sspc_child_chunks, list_type="parT")
    param_defs: dict[str, dict[str, Any]] = {}

    chunks_by_parameter = get_chunks_by_match_name(part_chunk)
    for index, (match_name, parameter_chunks) in enumerate(chunks_by_parameter.items()):
        # Skip first, it describes parent
        if index == 0:
            continue
        param_defs[match_name] = _parse_effect_parameter_def(parameter_chunks)

    return param_defs


def _merge_param_def(prop: Property, param_def: dict[str, Any]) -> None:
    """Merge parameter definition values into a parsed property.

    Overrides auto-detected property attributes with the more precise
    values from the effect's parameter definition.

    Args:
        prop: The property to update in place.
        param_def: The parameter definition dict.
    """
    prop.name = param_def["name"] or prop.name
    prop.property_control_type = param_def["property_control_type"]
    prop.property_value_type = param_def.get(
        "property_value_type", prop.property_value_type
    )
    prop.last_value = param_def.get("last_value")
    prop.default_value = param_def.get("default_value")
    min_val = param_def.get("min_value")
    if min_val is not None:
        prop.min_value = min_val
    max_val = param_def.get("max_value")
    if max_val is not None:
        prop.max_value = max_val
    prop.nb_options = param_def.get("nb_options")
    prop.property_parameters = param_def.get("property_parameters")


def _synthesize_effect_property(
    match_name: str,
    param_def: dict[str, Any],
    property_depth: int,
) -> Property | PropertyGroup:
    """Create a default Property from an effect parameter definition.

    When effect parameters are at their default value, AE omits them from
    the binary tdgp chunk.  This function builds a Property (or, for group
    separators, a PropertyGroup) from the parT definition so the parsed
    output matches what ExtendScript reports.

    Args:
        match_name: The property's match name.
        param_def: The parameter definition dict from parT parsing.
        property_depth: The nesting depth for this property.

    Returns:
        A Property or PropertyGroup with default values.
    """
    control_type = param_def["property_control_type"]
    pvt = param_def.get("property_value_type", PropertyValueType.OneD)

    if pvt == PropertyValueType.NO_VALUE:
        return PropertyGroup(
            enabled=True,
            match_name=match_name,
            name=param_def.get("name") or match_name,
            property_depth=property_depth,
            properties=[],
        )

    # Synthesised properties are at their defaults (AE omits them from
    # tdgp when unmodified).  Choose the appropriate default value and
    # ensure default_value == value so that is_modified stays False.
    control_type = param_def["property_control_type"]

    if control_type == PropertyControlType.ENUM:
        # parT stores 0-indexed default; ExtendScript uses 1-indexed.
        raw_default = param_def.get("default_value", 0)
        value: Any = raw_default + 1
        default_value: Any = value
    elif control_type == PropertyControlType.BOOLEAN:
        value = param_def.get("default_value", param_def.get("last_value"))
        default_value = value
    else:
        value = param_def.get("last_value")
        if value is None:
            value = param_def.get("default_value")
        default_value = param_def.get("default_value")

    is_color = control_type == PropertyControlType.COLOR
    is_spatial = pvt in (
        PropertyValueType.TwoD_SPATIAL,
        PropertyValueType.ThreeD_SPATIAL,
    )

    if pvt == PropertyValueType.COLOR:
        dims = 4
    elif pvt == PropertyValueType.ThreeD_SPATIAL:
        dims = 3
    elif pvt == PropertyValueType.TwoD_SPATIAL:
        dims = 2
    else:
        dims = 1

    prop = Property(
        animated=False,
        can_vary_over_time=True,
        color=is_color,
        dimensions_separated=False,
        dimensions=dims,
        enabled=True,
        expression_enabled=False,
        expression="",
        integer=control_type == PropertyControlType.INTEGER,
        is_spatial=is_spatial,
        keyframes=[],
        locked_ratio=False,
        match_name=match_name,
        name=param_def.get("name") or match_name,
        no_value=False,
        property_control_type=control_type,
        property_depth=property_depth,
        property_value_type=pvt,
        units_text=("degrees" if control_type == PropertyControlType.ANGLE else ""),
        value=value,
        vector=dims > 1,
    )
    prop.default_value = default_value
    prop.last_value = param_def.get("last_value")
    prop.min_value = param_def.get("min_value")
    prop.max_value = param_def.get("max_value")
    prop.nb_options = param_def.get("nb_options")
    prop.property_parameters = param_def.get("property_parameters")
    return prop


def _parse_effect_properties(
    tdgp_chunk: Aep.Chunk,
    param_defs: dict[str, dict[str, Any]],
    time_scale: float,
    child_depth: int,
    frame_rate: float,
    comp_size: tuple[int, int],
    layer_id_to_index: dict[int, int] | None,
) -> list[Property | PropertyGroup]:
    """Parse effect properties and merge with parameter definitions.

    Iterates the tdgp chunk's sub-properties, parses each one, and merges
    in the corresponding parameter definition if available.  Parameters
    defined in parT but absent from tdgp (because they hold default
    values) are synthesized as default properties.

    Args:
        tdgp_chunk: The tdgp chunk containing property data.
        param_defs: Parameter definitions to merge into properties.
        time_scale: The time scale of the parent composition.
        child_depth: The property depth for parsed child properties.
        frame_rate: The frame rate of the parent composition.
        comp_size: `(width, height)` of the parent composition in pixels.
        layer_id_to_index: Mapping from binary layer IDs to 1-based layer
            indices, used to resolve LAYER_INDEX property values.

    Returns:
        List of parsed and merged properties.
    """
    properties: list[Property | PropertyGroup] = []
    chunks_by_property = get_chunks_by_match_name(tdgp_chunk)
    for match_name, prop_chunks in chunks_by_property.items():
        # Skip index-0 internal parameters (not exposed in ExtendScript).
        if match_name.endswith("-0000"):
            continue
        first_chunk = prop_chunks[0]
        if first_chunk.data.list_type == "tdbs":
            prop = parse_property(
                tdbs_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                frame_rate=frame_rate,
                layer_id_to_index=layer_id_to_index,
            )
            if match_name in param_defs:
                _merge_param_def(prop, param_defs[match_name])
            properties.append(prop)
        elif first_chunk.data.list_type == "tdgp":
            sub_group = parse_property_group(
                tdgp_chunk=first_chunk,
                group_match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                effect_param_defs={},
                frame_rate=frame_rate,
                comp_size=comp_size,
                layer_id_to_index=layer_id_to_index,
            )
            properties.append(sub_group)
        else:
            raise NotImplementedError(
                f"Cannot parse parameter value : {first_chunk.data.list_type}"
            )

    # Synthesize default properties for parT entries not in tdgp.
    # Skip ADBE Force CPU GPU - it belongs inside ADBE Effect Built In Params,
    # not at the effect top level.
    parsed_match_names = set(chunks_by_property.keys())
    for match_name, param_def in param_defs.items():
        if match_name not in parsed_match_names and match_name != "ADBE Force CPU GPU":
            properties.append(
                _synthesize_effect_property(match_name, param_def, child_depth)
            )

    # ExtendScript always places Compositing Options last within an effect,
    # but the binary may store it among the first children.  Reorder.
    for j, child in enumerate(properties):
        if (
            isinstance(child, PropertyGroup)
            and child.match_name == "ADBE Effect Built In Params"
        ):
            properties.append(properties.pop(j))
            break

    return properties


def parse_effect(
    sspc_chunk: Aep.Chunk,
    group_match_name: str,
    time_scale: float,
    property_depth: int,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    frame_rate: float,
    comp_size: tuple[int, int],
    layer_id_to_index: dict[int, int] | None,
) -> PropertyGroup:
    """
    Parse an effect.

    Args:
        sspc_chunk: The SSPC chunk to parse.
        group_match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized. An indexed group (`PropertyBase.property_type ==
            PropertyType.indexed_group`) may not have a name value, but
            always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        property_depth: The nesting depth of this group (0 = layer level).
        effect_param_defs: Project-level effect parameter definitions, used as
            fallback when layer-level parT chunks are missing.
        frame_rate: The frame rate of the parent composition.
        comp_size: `(width, height)` of the parent composition in pixels.
        layer_id_to_index: Mapping from binary layer IDs to 1-based layer
            indices, used to resolve LAYER_INDEX property values.
    """
    sspc_child_chunks = sspc_chunk.data.chunks
    fnam_chunk = find_by_type(chunks=sspc_child_chunks, chunk_type="fnam")

    utf8_chunk = fnam_chunk.data.chunk
    tdgp_chunk = find_by_list_type(chunks=sspc_child_chunks, list_type="tdgp")
    name = get_user_defined_name(tdgp_chunk) or str_contents(utf8_chunk)

    try:
        param_defs = parse_effect_param_defs(sspc_child_chunks)
    except ChunkNotFoundError:
        param_defs = {}

    # Layer-level sspc may have an empty parT when the same effect type
    # is used more than once (AE doesn't duplicate the data).  Fall back
    # to previously cached or project-level EfdG definitions.
    if not param_defs and group_match_name in effect_param_defs:
        param_defs = effect_param_defs[group_match_name]

    # Cache successful parT parsing so later instances of the same
    # effect can reuse the definitions.
    if param_defs and group_match_name not in effect_param_defs:
        effect_param_defs[group_match_name] = param_defs
    properties = _parse_effect_properties(
        tdgp_chunk,
        param_defs,
        time_scale,
        child_depth=property_depth + 1,
        frame_rate=frame_rate,
        comp_size=comp_size,
        layer_id_to_index=layer_id_to_index,
    )

    effect_group = PropertyGroup(
        enabled=True,
        match_name=group_match_name,
        name=name,
        property_depth=property_depth,
        properties=properties,
    )
    effect_group.is_effect = True
    effect_group.property_type = PropertyType.INDEXED_GROUP

    # Set parent reference on all children
    for child in properties:
        child.parent_property = effect_group

    return effect_group


def _parse_effect_parameter_def(parameter_chunks: list[Aep.Chunk]) -> dict[str, Any]:
    """Parse effect parameter definition from pard chunk, returning a dict of values."""
    pard_chunk = find_by_type(chunks=parameter_chunks, chunk_type="pard")

    control_type = PropertyControlType(int(pard_chunk.data.property_control_type))

    result: dict[str, Any] = {
        "name": pard_chunk.data.name.split("\x00")[0],
        "property_control_type": control_type,
    }

    if control_type == PropertyControlType.ANGLE:
        result["last_value"] = pard_chunk.data.last_value / 65536
        result["property_value_type"] = PropertyValueType.OneD

    elif control_type == PropertyControlType.BOOLEAN:
        result["last_value"] = pard_chunk.data.last_value
        result["default_value"] = pard_chunk.data.default
        result["min_value"] = 0
        result["max_value"] = 1

    elif control_type == PropertyControlType.COLOR:
        result["last_value"] = pard_chunk.data.last_color
        result["default_value"] = pard_chunk.data.default_color
        result["max_value"] = pard_chunk.data.max_color
        result["property_value_type"] = PropertyValueType.COLOR

    elif control_type == PropertyControlType.ENUM:
        result["last_value"] = pard_chunk.data.last_value
        # nb_options is stored with the count in the high 16 bits
        nb_options = pard_chunk.data.nb_options >> 16
        result["nb_options"] = nb_options
        result["default_value"] = pard_chunk.data.default
        result["min_value"] = 1
        result["max_value"] = nb_options

    elif control_type == PropertyControlType.SCALAR:
        result["last_value"] = pard_chunk.data.last_value / 65536
        result["min_value"] = pard_chunk.data.min_value
        result["max_value"] = pard_chunk.data.max_value

    elif control_type == PropertyControlType.SLIDER:
        result["last_value"] = pard_chunk.data.last_value
        result["max_value"] = pard_chunk.data.max_value

    elif control_type == PropertyControlType.THREE_D:
        result["last_value"] = [
            pard_chunk.data.last_value_x,
            pard_chunk.data.last_value_y,
            pard_chunk.data.last_value_z,
        ]
        result["property_value_type"] = PropertyValueType.ThreeD_SPATIAL

    elif control_type == PropertyControlType.TWO_D:
        result["last_value"] = [
            pard_chunk.data.last_value_x,
            pard_chunk.data.last_value_y,
        ]
        result["property_value_type"] = PropertyValueType.TwoD_SPATIAL

    elif control_type == PropertyControlType.LAYER:
        result["property_value_type"] = PropertyValueType.LAYER_INDEX
        result["default_value"] = 0

    elif control_type == PropertyControlType.MASK:
        result["property_value_type"] = PropertyValueType.MASK_INDEX
        result["default_value"] = 0

    elif control_type == PropertyControlType.CURVE:
        result["property_value_type"] = PropertyValueType.CUSTOM_VALUE

    elif control_type in (
        PropertyControlType.GROUP,
        PropertyControlType.UNKNOWN,
        PropertyControlType.UNKNOWN_14,
        PropertyControlType.PAINT_GROUP,
    ):
        result["property_value_type"] = PropertyValueType.NO_VALUE

    with suppress(ChunkNotFoundError):
        pdnm_chunk = find_by_type(chunks=parameter_chunks, chunk_type="pdnm")
        utf8_chunk = pdnm_chunk.data.chunk
        pdnm_data = str_contents(utf8_chunk)
        if control_type == PropertyControlType.ENUM:
            result["property_parameters"] = pdnm_data.split("|")
        elif pdnm_data:
            result["name"] = pdnm_data

    return result
