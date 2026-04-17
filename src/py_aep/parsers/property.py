"""Property group, effect, mask, orientation, shape, and text parsers."""

from __future__ import annotations

import io
import logging
import typing
from contextlib import suppress
from typing import Any

from ..cos import CosParser
from ..data.match_names import MATCH_NAME_TO_NICE_NAME
from ..enums import (
    PropertyControlType,
    PropertyType,
    PropertyValueType,
)
from ..kaitai import Aep
from ..kaitai.proxy import ProxyBody
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.properties.mask_property_group import MaskPropertyGroup
from ..models.properties.overrides import _PROPERTY_DEFAULTS
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from ..models.properties.shape import FeatherPoint, Shape
from .marker import parse_markers
from .property_value import (
    parse_property,
)
from .text import parse_btdk_cos
from .utils import (
    get_chunks_by_match_name,
)

if typing.TYPE_CHECKING:
    from ..models.items.composition import CompItem

logger = logging.getLogger(__name__)


def parse_properties(
    chunks_by_match_name: dict[str, list[Aep.Chunk]],
    child_depth: int,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    composition: CompItem,
) -> list[Property | PropertyGroup]:
    """Dispatch sub-property chunks into parsed Property/PropertyGroup items.

    Iterates each match-name group, finds the first LIST chunk, and
    dispatches to the appropriate parser based on its list type.

    Args:
        chunks_by_match_name: Sub-property chunks grouped by match name
            (from `get_chunks_by_match_name`).
        child_depth: The property depth for parsed child properties.
        effect_param_defs: Project-level effect parameter definitions.
        composition: The parent composition.

    Returns:
        Ordered list of parsed properties and property groups.
    """
    properties: list[Property | PropertyGroup] = []
    for match_name, sub_prop_chunks in chunks_by_match_name.items():
        # Find the first LIST chunk; non-LIST chunks (e.g. mkif for masks)
        # are auxiliary data that we skip when determining the property type.
        try:
            first_chunk = find_by_type(chunks=sub_prop_chunks, chunk_type="LIST")
        except ChunkNotFoundError:
            continue
        # Effects can share a match name when the same effect type is applied
        # multiple times. Iterate all LIST chunks for sspc and tdgp; other
        # types use the first chunk (additional chunks are auxiliary data).
        if first_chunk.body.list_type == "sspc":
            for chunk in filter_by_list_type(chunks=sub_prop_chunks, list_type="sspc"):
                sub_prop: Property | PropertyGroup = parse_effect(
                    sspc_chunk=chunk,
                    group_match_name=match_name,
                    property_depth=child_depth,
                    effect_param_defs=effect_param_defs,
                    composition=composition,
                )
                properties.append(sub_prop)
        elif first_chunk.body.list_type == "tdgp":
            if match_name == "ADBE Mask Atom":
                # Pair each mask tdgp chunk with its mkif (mask info) chunk
                for tdgp_c, mkif_c in zip(
                    filter_by_list_type(chunks=sub_prop_chunks, list_type="tdgp"),
                    filter_by_type(chunks=sub_prop_chunks, chunk_type="mkif"),
                ):
                    sub_prop = _parse_mask_atom(
                        tdgp_chunk=tdgp_c,
                        mkif_chunk=mkif_c,
                        property_depth=child_depth,
                        effect_param_defs=effect_param_defs,
                        composition=composition,
                    )
                    properties.append(sub_prop)
                # Append 1-based index to mask names (e.g. "Mask 1", "Mask 2")
                mask_count = 0
                for p in properties:
                    if isinstance(p, MaskPropertyGroup):
                        mask_count += 1
                        p._auto_name = f"Mask {mask_count}"
            else:
                # Indexed groups (e.g. effects) can share a match name.
                for tdgp_c in filter_by_list_type(
                    chunks=sub_prop_chunks, list_type="tdgp"
                ):
                    sub_prop = parse_property_group(
                        tdgp_chunk=tdgp_c,
                        group_match_name=match_name,
                        property_depth=child_depth,
                        effect_param_defs=effect_param_defs,
                        composition=composition,
                    )
                    properties.append(sub_prop)
        elif first_chunk.body.list_type == "tdbs":
            sub_prop = parse_property(
                tdbs_chunk=first_chunk,
                match_name=match_name,
                composition=composition,
                property_depth=child_depth,
            )
            properties.append(sub_prop)
        elif first_chunk.body.list_type == "otst":
            sub_prop = parse_orientation(
                otst_chunk=first_chunk,
                match_name=match_name,
                property_depth=child_depth,
                composition=composition,
            )
            properties.append(sub_prop)
        elif first_chunk.body.list_type == "btds":
            sub_prop = parse_text_document(
                btds_chunk=first_chunk,
                match_name=match_name,
                property_depth=child_depth,
                composition=composition,
            )
            properties.append(sub_prop)
        elif first_chunk.body.list_type == "om-s":
            sub_prop = parse_shape(
                oms_chunk=first_chunk,
                match_name=match_name,
                property_depth=child_depth,
                composition=composition,
            )
            properties.append(sub_prop)
        elif first_chunk.body.list_type == "mrst":
            sub_prop = parse_markers(
                mrst_chunk=first_chunk,
                composition=composition,
                property_depth=child_depth,
            )
            properties.append(sub_prop)
        elif first_chunk.body.list_type == "OvG2":
            # Essential Properties override metadata (UUID linkage to
            # CIF3 controller definitions). The actual override values
            # live in the sibling tdgp and are already parsed.
            logger.debug("Skipping OvG2 metadata (match name '%s')", match_name)
        else:
            logger.warning(
                "Skipping unsupported property list type '%s' (match name '%s')",
                first_chunk.body.list_type,
                match_name,
            )

    return properties


def parse_property_group(
    tdgp_chunk: Aep.Chunk,
    group_match_name: str,
    property_depth: int,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    composition: CompItem,
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
        property_depth: The nesting depth of this group (0 = layer level).
        effect_param_defs: Project-level effect parameter definitions, used as
            fallback when layer-level parT chunks are missing.
        composition: The parent composition.
    """
    properties = parse_properties(
        chunks_by_match_name=get_chunks_by_match_name(tdgp_chunk),
        child_depth=property_depth + 1,
        effect_param_defs=effect_param_defs,
        composition=composition,
    )

    # Try to read the group-level tdsb chunk.
    # Leaf properties always have a tdsb; groups may or may not.
    try:
        group_tdsb = find_by_type(chunks=tdgp_chunk.body.chunks, chunk_type="tdsb")
        group_tdsb_body = group_tdsb.body
    except ChunkNotFoundError:
        group_tdsb_body = None

    # Resolve _name_utf8 from the tdgp's tdsn child
    try:
        name_utf8 = (
            find_by_type(chunks=tdgp_chunk.body.chunks, chunk_type="tdsn")
            .body.chunks[0]
            .body
        )
    except ChunkNotFoundError:
        name_utf8 = None

    prop_group = PropertyGroup(
        _tdgp=tdgp_chunk.body,
        _tdsb=group_tdsb_body,
        _name_utf8=name_utf8,
        match_name=group_match_name,
        property_depth=property_depth,
        properties=properties,
    )

    return prop_group


def _parse_mask_atom(
    tdgp_chunk: Aep.Chunk,
    mkif_chunk: Aep.Chunk,
    property_depth: int,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    composition: CompItem,
) -> MaskPropertyGroup:
    """Parse a mask atom into a MaskPropertyGroup.

    Combines the child properties from the tdgp chunk with the mask-specific
    attributes (inverted, locked, mask_mode, color, mask_feather_falloff,
    mask_motion_blur) parsed from the mkif chunk, and the rotoBezier flag
    from the ADBE Mask Shape tdsb chunk.

    Args:
        tdgp_chunk: The tdgp chunk for this mask atom.
        mkif_chunk: The mkif (mask info) chunk containing mask attributes.
        property_depth: The nesting depth of this group.
        effect_param_defs: Project-level effect parameter definitions.
        composition: The parent composition.
    """
    base = parse_property_group(
        tdgp_chunk=tdgp_chunk,
        group_match_name="ADBE Mask Atom",
        property_depth=property_depth,
        effect_param_defs=effect_param_defs,
        composition=composition,
    )

    # Extract the mask shape's tdsb body for the roto_bezier descriptor.
    mask_shape_tdsb_body = None
    chunks_by_mn = get_chunks_by_match_name(tdgp_chunk)
    mask_shape_chunks = chunks_by_mn.get("ADBE Mask Shape", [])
    for chunk in mask_shape_chunks:
        if chunk.chunk_type == "LIST" and chunk.body.list_type == "om-s":
            with suppress(ChunkNotFoundError):
                tdbs = find_by_list_type(chunks=chunk.body.chunks, list_type="tdbs")
                mask_shape_tdsb_body = tdbs.body.tdsb.body
            break

    mask_group = MaskPropertyGroup(
        _tdgp=base._tdgp,
        _tdsb=base._tdsb,
        _name_utf8=base._name_utf8,
        _mkif=mkif_chunk.body,
        _mask_shape_tdsb=mask_shape_tdsb_body,
        match_name=base.match_name,
        property_depth=base.property_depth,
        properties=base.properties,
    )
    mask_group.property_type = base.property_type
    mask_group.is_mask = True
    return mask_group


def parse_orientation(
    otst_chunk: Aep.Chunk,
    match_name: str,
    property_depth: int,
    composition: CompItem,
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
        property_depth: The nesting depth of this property (0 = layer level).
        composition: The parent composition.
    """
    tdbs_chunk = find_by_list_type(chunks=otst_chunk.body.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        composition=composition,
        property_depth=property_depth,
    )
    # Orientation uses an angle dial control.  ExtendScript reports
    # propertyValueType as ThreeD_SPATIAL and isSpatial as True, even
    # though the binary stores is_spatial=False.
    prop._property_control_type = PropertyControlType.ANGLE
    prop._property_value_type = PropertyValueType.ThreeD_SPATIAL
    prop.__dict__["dimensions"] = 3
    prop.__dict__["_vector"] = True

    # cdat_body is parameterized with is_le; .value instance returns
    # the correctly-endian doubles regardless of context.
    try:
        values = list(
            find_by_type(chunks=tdbs_chunk.body.chunks, chunk_type="cdat").body.value
        )
        while len(values) < 3:
            values.append(0.0)
        prop.value = values[:3]
    except ChunkNotFoundError:
        prop.value = None

    # Animated orientation keyframes store their 3-component values in
    # otky > otda chunks (one otda per keyframe), a sibling of tdbs inside
    # otst.  The standard _parse_keyframes() reads from tdbs which only has 1D
    # orientation data, so we override each keyframe's value with the full 3D
    # otda data.
    with suppress(ChunkNotFoundError):
        otky_chunk = find_by_list_type(chunks=otst_chunk.body.chunks, list_type="otky")
        otda_chunks = filter_by_type(chunks=otky_chunk.body.chunks, chunk_type="otda")
        for idx, kf in enumerate(prop.keyframes):
            if idx < len(otda_chunks):
                kf.value = list(otda_chunks[idx].body.value)

    return prop


def _parse_shape_shap(
    shap_chunk: Aep.Chunk,
    composition: CompItem,
    is_mask_shape: bool,
) -> Shape:
    """Parse a single shape path from a `shap` LIST chunk.

    Each `shap` LIST contains:
    - `shph` chunk: shape header with closed flag and bounding box
    - `list` LIST:  contains `lhd3` (point count/size) and `ldat`
      (raw normalized bezier points)

    Points in `ldat` are stored as `(x, y)` pairs,
    normalized to the `[0, 1]` range of the bounding box.  Every three
    consecutive points form a cycle:
    `vertex, out_tangent, in_tangent_of_next_vertex`.

    Mask shapes use a normalized `[0, 1]` bounding box, so the
    resulting coordinates must be scaled by the composition size to get
    pixel values.  Shape-layer paths already have a pixel bounding box.

    Args:
        shap_chunk: A `shap` LIST chunk.
        composition: The parent composition, used for denormalizing
            mask shapes.
        is_mask_shape: Whether this shape belongs to a mask property.

    Returns:
        A [Shape][] with absolute coordinates and tangent offsets.
    """
    shph_chunk = find_by_type(chunks=shap_chunk.body.chunks, chunk_type="shph")
    list_chunk = find_by_list_type(chunks=shap_chunk.body.chunks, list_type="list")

    shph = shph_chunk.body
    points: list[Aep.ShapePoint] = list_chunk.body.ldat.body.items

    # Extract variable-width mask feather data from fth5 chunk (if present).
    try:
        fth5 = find_by_type(chunks=shap_chunk.body.chunks, chunk_type="fth5")
        feather_points = [FeatherPoint(_fp=pt) for pt in fth5.body.points]
    except ChunkNotFoundError:
        feather_points = []

    return Shape(
        _shph=shph,
        _points=points,
        _is_mask=is_mask_shape,
        _composition=composition if is_mask_shape else None,
        feather_points=feather_points,
    )


def parse_shape(
    oms_chunk: Aep.Chunk,
    match_name: str,
    property_depth: int,
    composition: CompItem,
) -> Property:
    """Parse a shape/mask-path property from an `om-s` LIST chunk.

    An `om-s` LIST contains:
    - `tdbs` LIST: standard property metadata (timing, keyframes, etc.)
    - `omks` LIST: shape keyframe values (one `shap` per keyframe,
      or one `shap` for static shapes)

    Args:
        oms_chunk: The `om-s` LIST chunk to parse.
        match_name: The property match name.
        property_depth: Nesting depth of this property.
        composition: The parent composition.

    Returns:
        A [Property][] with `property_value_type` set to
        [SHAPE][py_aep.enums.PropertyValueType.SHAPE] and `value`
        set to a [Shape][].
    """
    tdbs_chunk = find_by_list_type(chunks=oms_chunk.body.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        composition=composition,
        property_depth=property_depth,
    )

    prop._property_value_type = PropertyValueType.SHAPE
    # Shape properties always carry a value (from omks), even though
    # tdb4 may report no_value=True (there is no cdat for shapes).
    prop.__dict__["_no_value"] = False

    # Collect shape values from omks > shap LISTs
    try:
        omks_chunk = find_by_list_type(chunks=oms_chunk.body.chunks, list_type="omks")
        shape_values: list[Shape] = []
        is_mask = match_name == "ADBE Mask Shape"
        for shap_chunk in filter_by_list_type(
            chunks=omks_chunk.body.chunks, list_type="shap"
        ):
            shape_values.append(_parse_shape_shap(shap_chunk, composition, is_mask))
    except ChunkNotFoundError:
        logger.debug("Could not parse omks shape data for %s", match_name)
        return prop

    # Assign static value (first shape).  Set an empty Shape as default
    # so that is_modified detects any real mask path as modified.
    prop.default_value = Shape(closed=False)
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
    property_depth: int,
    composition: CompItem,
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
        property_depth: The nesting depth of this property (0 = layer level).
        composition: The parent composition.
    """
    tdbs_chunk = find_by_list_type(chunks=btds_chunk.body.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        composition=composition,
        property_depth=property_depth,
    )
    prop._property_value_type = PropertyValueType.TEXT_DOCUMENT

    try:
        btdk_chunk = find_by_list_type(
            chunks=btds_chunk.body.chunks,
            list_type="btdk",
        )
        parser = CosParser(
            io.BytesIO(btdk_chunk.body.binary_data),
            len(btdk_chunk.body.binary_data),
        )
        cos_data = parser.parse()
        if not isinstance(cos_data, dict):
            raise TypeError("Expected dict from COS parser")
        text_documents, _fonts = parse_btdk_cos(cos_data, btdk_chunk.body)
        if text_documents:
            if prop.keyframes:
                for kf, doc in zip(prop.keyframes, text_documents):
                    kf._value = doc
            else:
                prop.value = text_documents[0]
    except Exception:
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
    prop._auto_name = param_def["name"] or prop._auto_name
    prop._property_control_type = param_def["property_control_type"]
    prop._property_value_type = param_def.get(
        "property_value_type", prop.property_value_type
    )
    prop.last_value = param_def.get("last_value")
    # Prefer the static lookup for defaults - pard defaults may be
    # incorrect (e.g. 0 for properties whose real AE default is non-zero).
    # For LAYER references, pard stores a meaningless 0 and we have no
    # static override, so leave default_value unset entirely.
    static_default = _PROPERTY_DEFAULTS.get(prop.match_name)
    if static_default is not None:
        prop.default_value = static_default
    elif param_def["property_control_type"] != PropertyControlType.LAYER:
        prop.default_value = param_def.get("default_value")
    min_val = param_def.get("min_value")
    if min_val is not None:
        prop._min_value_fallback = min_val
    max_val = param_def.get("max_value")
    if max_val is not None:
        prop._max_value_fallback = max_val
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
            _tdsb=ProxyBody(
                enabled=1,
                locked_ratio=0,
                roto_bezier=0,
                dimensions_separated=0,
            ),
            match_name=match_name,
            auto_name=param_def.get("name")
            or MATCH_NAME_TO_NICE_NAME.get(match_name, ""),
            property_depth=property_depth,
            properties=[],
        )

    # Synthesised properties are at their defaults (AE omits them from
    # tdgp when unmodified).  Choose the appropriate default value and
    # ensure default_value == value so that is_modified stays False.
    control_type = param_def["property_control_type"]

    if control_type == PropertyControlType.ENUM:
        # parT stores 0-indexed default; ExtendScript uses 1-indexed.
        # last_value from parT is already 1-indexed and reflects the
        # current value even when the property is absent from tdgp.
        raw_default = param_def.get("default_value", 0)
        fallback: Any = raw_default + 1
        value: Any = param_def.get("last_value", fallback)
        default_value: Any = value
    elif control_type == PropertyControlType.BOOLEAN:
        value = param_def.get("default_value", param_def.get("last_value"))
        default_value = value
    else:
        value = param_def.get("last_value")
        if value is None:
            value = param_def.get("default_value")
        if value is None:
            value = _PROPERTY_DEFAULTS.get(match_name)
        default_value = param_def.get("default_value")
        if default_value is None:
            default_value = value

    is_color = control_type == PropertyControlType.COLOR
    is_spatial = (
        pvt
        in (
            PropertyValueType.TwoD_SPATIAL,
            PropertyValueType.ThreeD_SPATIAL,
        )
        or is_color
    )

    if pvt == PropertyValueType.COLOR:
        dims = 4
    elif pvt == PropertyValueType.ThreeD_SPATIAL:
        dims = 3
    elif pvt == PropertyValueType.TwoD_SPATIAL:
        dims = 2
    else:
        dims = 1

    is_integer = control_type == PropertyControlType.INTEGER
    # MASK properties cannot vary over time in ExtendScript.
    can_vary = control_type != PropertyControlType.MASK
    prop = Property(
        _tdsb=ProxyBody(
            enabled=1,
            locked_ratio=0,
            roto_bezier=0,
            dimensions_separated=0,
        ),
        _tdb4=ProxyBody(
            dimensions=dims,
            is_spatial=int(is_spatial),
            animated=0,
            color=int(is_color),
            integer=int(is_integer),
            no_value=0,
            vector=int(dims > 1),
            can_vary_over_time=int(can_vary),
            expression_enabled=0,
        ),
        keyframes=[],
        match_name=match_name,
        auto_name=param_def.get("name") or match_name,
        property_control_type=control_type,
        property_depth=property_depth,
        property_value_type=pvt,
        units_text=("degrees" if control_type == PropertyControlType.ANGLE else None),
        value=value,
    )
    prop.default_value = default_value
    prop.last_value = param_def.get("last_value")
    min_val = param_def.get("min_value")
    if min_val is not None:
        prop._min_value_fallback = min_val
    max_val = param_def.get("max_value")
    if max_val is not None:
        prop._max_value_fallback = max_val
    prop.nb_options = param_def.get("nb_options")
    prop.property_parameters = param_def.get("property_parameters")
    return prop


def _parse_effect_properties(
    tdgp_chunk: Aep.Chunk,
    param_defs: dict[str, dict[str, Any]],
    child_depth: int,
    composition: CompItem,
    group_match_name: str = "",
) -> list[Property | PropertyGroup]:
    """Parse effect properties and merge with parameter definitions.

    Iterates the tdgp chunk's sub-properties, parses each one, and merges
    in the corresponding parameter definition if available.  Parameters
    defined in parT but absent from tdgp (because they hold default
    values) are synthesized as default properties.

    Args:
        tdgp_chunk: The tdgp chunk containing property data.
        param_defs: Parameter definitions to merge into properties.
        child_depth: The property depth for parsed child properties.
        composition: The parent composition.

    Returns:
        List of parsed and merged properties.
    """
    properties: list[Property | PropertyGroup] = []
    chunks_by_property = get_chunks_by_match_name(tdgp_chunk)
    # Skip index-0 internal parameters (not exposed in ExtendScript).
    for key in [k for k in chunks_by_property if k.endswith("-0000")]:
        del chunks_by_property[key]

    properties = parse_properties(
        chunks_by_match_name=chunks_by_property,
        child_depth=child_depth,
        effect_param_defs={},
        composition=composition,
    )

    # Merge parameter definitions into parsed properties.
    for prop in properties:
        if isinstance(prop, Property) and prop.match_name in param_defs:
            _merge_param_def(prop, param_defs[prop.match_name])

    # Synthesize default properties for parT entries not in tdgp.
    # Skip ADBE Force CPU GPU - it belongs inside ADBE Effect Built In Params,
    # not at the effect top level.
    parsed_match_names = set(chunks_by_property.keys())
    for match_name, param_def in param_defs.items():
        if match_name not in parsed_match_names and match_name != "ADBE Force CPU GPU":
            synth = _synthesize_effect_property(match_name, param_def, child_depth)
            # parT stores 2D point values in a 0-512 range; convert to
            # pixel coordinates so they match parsed (cdat-backed) values.
            if (
                isinstance(synth, Property)
                and synth._property_control_type == PropertyControlType.TWO_D
                and isinstance(synth._value, list)
                and len(synth._value) >= 2
            ):
                w = composition.width
                h = composition.height
                synth._value = [
                    synth._value[0] / 512.0 * w,
                    synth._value[1] / 512.0 * h,
                ]
                if (
                    isinstance(synth.default_value, list)
                    and len(synth.default_value) >= 2
                ):
                    synth.default_value = [
                        synth.default_value[0] / 512.0 * w,
                        synth.default_value[1] / 512.0 * h,
                    ]
            properties.append(synth)

    # Reorder to match parT/pard canonical order.  Properties parsed from
    # binary chunks or synthesized above may appear in arbitrary order;
    # param_defs preserves the order ExtendScript expects.  Items not in
    # param_defs (e.g. ADBE Effect Built In Params) sort to the end.
    if param_defs:
        def_order = {mn: i for i, mn in enumerate(param_defs)}
        properties.sort(key=lambda p: def_order.get(p.match_name, len(def_order)))

    return properties


def parse_effect(
    sspc_chunk: Aep.Chunk,
    group_match_name: str,
    property_depth: int,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    composition: CompItem,
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
        property_depth: The nesting depth of this group (0 = layer level).
        effect_param_defs: Project-level effect parameter definitions, used as
            fallback when layer-level parT chunks are missing.
        composition: The parent composition.
    """
    sspc_child_chunks = sspc_chunk.body.chunks
    fnam_chunk = find_by_type(chunks=sspc_child_chunks, chunk_type="fnam")

    fnam_utf8_body = fnam_chunk.body.chunks[0].body
    tdgp_chunk = find_by_list_type(chunks=sspc_child_chunks, list_type="tdgp")

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
        child_depth=property_depth + 1,
        composition=composition,
        group_match_name=group_match_name,
    )

    # Resolve _name_utf8 from the effect tdgp's tdsn child
    try:
        effect_name_utf8 = (
            find_by_type(chunks=tdgp_chunk.body.chunks, chunk_type="tdsn")
            .body.chunks[0]
            .body
        )
    except ChunkNotFoundError:
        effect_name_utf8 = None

    try:
        effect_tdsb_body = find_by_type(
            chunks=tdgp_chunk.body.chunks, chunk_type="tdsb"
        ).body
    except ChunkNotFoundError:
        effect_tdsb_body = None

    effect_group = PropertyGroup(
        _tdgp=tdgp_chunk.body,
        _tdsb=effect_tdsb_body,
        _name_utf8=effect_name_utf8,
        _fnam_utf8=fnam_utf8_body,
        match_name=group_match_name,
        property_depth=property_depth,
        properties=properties,
    )
    effect_group.is_effect = True
    effect_group.property_type = PropertyType.INDEXED_GROUP

    return effect_group


def _parse_effect_parameter_def(parameter_chunks: list[Aep.Chunk]) -> dict[str, Any]:
    """Parse effect parameter definition from pard chunk, returning a dict of values."""
    pard_chunk = find_by_type(chunks=parameter_chunks, chunk_type="pard")

    control_type = PropertyControlType(int(pard_chunk.body.property_control_type))

    result: dict[str, Any] = {
        "name": pard_chunk.body.__dict__["name"].split("\x00", 1)[0],
        "property_control_type": control_type,
    }

    if control_type == PropertyControlType.ANGLE:
        result["last_value"] = pard_chunk.body.last_value / 65536
        result["property_value_type"] = PropertyValueType.OneD

    elif control_type == PropertyControlType.BOOLEAN:
        result["last_value"] = pard_chunk.body.last_value
        result["default_value"] = pard_chunk.body.default
        result["min_value"] = 0
        result["max_value"] = 1

    elif control_type == PropertyControlType.COLOR:
        # pard stores colors as [A, R, G, B] in 0-255 range;
        # ExtendScript uses [R, G, B, A] in 0-1 range.
        a, r, g, b = pard_chunk.body.last_color
        result["last_value"] = [r / 255.0, g / 255.0, b / 255.0, a / 255.0]
        a, r, g, b = pard_chunk.body.default_color
        result["default_value"] = [r / 255.0, g / 255.0, b / 255.0, a / 255.0]
        result["min_value"] = -3921568.62745098
        result["max_value"] = 3921568.62745098
        result["property_value_type"] = PropertyValueType.COLOR

    elif control_type == PropertyControlType.ENUM:
        result["last_value"] = pard_chunk.body.last_value
        # nb_options is stored with the count in the high 16 bits
        nb_options = pard_chunk.body.nb_options >> 16
        result["nb_options"] = nb_options
        result["default_value"] = pard_chunk.body.default
        result["min_value"] = 1
        result["max_value"] = nb_options

    elif control_type == PropertyControlType.SCALAR:
        result["last_value"] = pard_chunk.body.last_value / 65536
        result["min_value"] = pard_chunk.body.min_value
        result["max_value"] = pard_chunk.body.max_value

    elif control_type == PropertyControlType.SLIDER:
        result["last_value"] = pard_chunk.body.last_value
        result["max_value"] = pard_chunk.body.max_value

    elif control_type == PropertyControlType.THREE_D:
        result["last_value"] = [
            pard_chunk.body.last_value_x,
            pard_chunk.body.last_value_y,
            pard_chunk.body.last_value_z,
        ]
        result["property_value_type"] = PropertyValueType.ThreeD_SPATIAL

    elif control_type == PropertyControlType.TWO_D:
        result["last_value"] = [
            pard_chunk.body.last_value_x,
            pard_chunk.body.last_value_y,
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
        utf8_chunk = pdnm_chunk.body.chunks[0]
        pdnm_data = str_contents(utf8_chunk)
        if control_type == PropertyControlType.ENUM:
            result["property_parameters"] = pdnm_data.split("|")
        elif pdnm_data:
            result["name"] = pdnm_data

    return result
