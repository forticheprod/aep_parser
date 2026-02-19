from __future__ import annotations

import io
import logging
from contextlib import suppress
from typing import Any

from ..cos import CosParser
from ..kaitai import Aep
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.enums import (
    KeyframeInterpolationType,
    Label,
    PropertyControlType,
    PropertyValueType,
)
from ..models.properties.keyframe import Keyframe
from ..models.properties.marker import MarkerValue
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from .match_names import MATCH_NAME_TO_NICE_NAME
from .text import parse_btdk_cos
from .utils import (
    get_chunks_by_match_name,
    parse_ldat_items,
    split_into_batches,
)

logger = logging.getLogger(__name__)


def parse_property_group(
    tdgp_chunk: Aep.Chunk, group_match_name: str, time_scale: float
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
            (`PropertyBase.property_type == Aep.PropertyType.indexed_group`)
            may not have a name value, but always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
    """
    name = MATCH_NAME_TO_NICE_NAME.get(group_match_name, group_match_name)

    properties: list[Property | PropertyGroup] = []
    chunks_by_sub_prop = get_chunks_by_match_name(tdgp_chunk)
    for match_name, sub_prop_chunks in chunks_by_sub_prop.items():
        first_chunk = sub_prop_chunks[0]
        sub_prop: Property | PropertyGroup
        if first_chunk.list_type == "tdgp":
            sub_prop = parse_property_group(
                tdgp_chunk=first_chunk,
                group_match_name=match_name,
                time_scale=time_scale,
            )
        elif first_chunk.list_type == "sspc":
            sub_prop = parse_effect(
                sspc_chunk=first_chunk,
                group_match_name=match_name,
                time_scale=time_scale,
            )
        elif first_chunk.list_type == "tdbs":
            sub_prop = parse_property(
                tdbs_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
            )
        elif first_chunk.list_type == "otst":
            sub_prop = parse_orientation(
                otst_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
            )
        elif first_chunk.list_type == "btds":
            sub_prop = parse_text_document(
                btds_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
            )
        else:
            raise NotImplementedError(f"Cannot parse {first_chunk.list_type} property")
        properties.append(sub_prop)

    prop_group = PropertyGroup(
        enabled=True,
        is_effect=False,
        match_name=group_match_name,
        name=name,
        properties=properties,
    )

    return prop_group


def parse_orientation(
    otst_chunk: Aep.Chunk, match_name: str, time_scale: float
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
    """
    tdbs_chunk = find_by_list_type(chunks=otst_chunk.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
    )
    # Override types for orientation
    prop.property_control_type = PropertyControlType.ANGLE
    prop.property_value_type = PropertyValueType.ORIENTATION

    # otky_chunk = find_by_list_type(
    #     chunks=otst_chunk.chunks,
    #     list_type="otky"
    # )
    # otda_chunks = filter_by_type(
    #     chunks=otky_chunk.chunks,
    #     chunk_type="otda"
    # )
    return prop


def parse_text_document(
    btds_chunk: Aep.Chunk, match_name: str, time_scale: float
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
    """
    tdbs_chunk = find_by_list_type(chunks=btds_chunk.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
    )

    try:
        btdk_chunk = find_by_list_type(
            chunks=btds_chunk.chunks,
            list_type="btdk",
        )
        parser = CosParser(
            io.BytesIO(btdk_chunk.binary_data),
            len(btdk_chunk.binary_data),
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


def _determine_property_types(
    no_value: bool,
    color: bool,
    integer: bool,
    vector: bool,
    dimensions: int,
    is_spatial: bool,
    match_name: str,
    name: str,
    animated: bool,
) -> tuple[PropertyControlType, PropertyValueType]:
    """Determine property control and value types from tdb4 flags.

    Uses the combination of boolean flags from the tdb4 chunk to determine
    the property control type (e.g., scalar, color, boolean) and value type
    (e.g., one_d, two_d_spatial, color).

    Args:
        no_value: Whether the property has no value.
        color: Whether the property is a color.
        integer: Whether the property is an integer.
        vector: Whether the property is a vector.
        dimensions: Number of dimensions.
        is_spatial: Whether the property is spatial.
        match_name: The property match name (for debug output).
        name: The property display name (for debug output).
        animated: Whether the property is animated (for debug output).

    Returns:
        Tuple of (property_control_type, property_value_type).
    """
    property_control_type = PropertyControlType.UNKNOWN
    property_value_type = PropertyValueType.UNKNOWN

    if no_value:
        property_value_type = PropertyValueType.NO_VALUE
    if color:
        property_control_type = PropertyControlType.COLOR
        property_value_type = PropertyValueType.COLOR
    elif integer:
        property_control_type = PropertyControlType.BOOLEAN
        property_value_type = PropertyValueType.ONE_D
    elif vector:
        if dimensions == 1:
            property_control_type = PropertyControlType.SCALAR
            property_value_type = PropertyValueType.ONE_D
        elif dimensions == 2:
            property_control_type = PropertyControlType.TWO_D
            property_value_type = (
                PropertyValueType.TWO_D_SPATIAL if is_spatial else PropertyValueType.TWO_D
            )
        elif dimensions == 3:
            property_control_type = PropertyControlType.THREE_D
            property_value_type = (
                PropertyValueType.THREE_D_SPATIAL
                if is_spatial
                else PropertyValueType.THREE_D
            )

    if property_control_type == PropertyControlType.UNKNOWN:
        logger.warning(
            "Could not determine type for property %s"
            " | name: %s"
            " | dimensions: %s"
            " | animated: %s"
            " | integer: %s"
            " | is_spatial: %s"
            " | vector: %s"
            " | no_value: %s"
            " | color: %s",
            match_name,
            name,
            dimensions,
            animated,
            integer,
            is_spatial,
            vector,
            no_value,
            color,
        )

    return property_control_type, property_value_type


def parse_property(
    tdbs_chunk: Aep.Chunk,
    match_name: str,
    time_scale: float,
) -> Property:
    """
    Parse a property.

    Args:
        tdbs_chunk: The TDBS chunk to parse.
        match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
    """
    tdbs_child_chunks = tdbs_chunk.chunks

    tdsb_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="tdsb")

    locked_ratio = tdsb_chunk.locked_ratio
    enabled = tdsb_chunk.enabled
    dimensions_separated = tdsb_chunk.dimensions_separated

    name = _get_user_defined_name(tdbs_chunk) or MATCH_NAME_TO_NICE_NAME.get(
        match_name, match_name
    )

    tdb4_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="tdb4")

    is_spatial = tdb4_chunk.is_spatial
    expression_enabled = tdb4_chunk.expression_enabled
    animated = tdb4_chunk.animated
    dimensions = tdb4_chunk.dimensions
    integer = tdb4_chunk.integer
    vector = tdb4_chunk.vector
    no_value = tdb4_chunk.no_value
    color = tdb4_chunk.color

    property_control_type, property_value_type = _determine_property_types(
        no_value=no_value,
        color=color,
        integer=integer,
        vector=vector,
        dimensions=dimensions,
        is_spatial=is_spatial,
        match_name=match_name,
        name=name,
        animated=animated,
    )

    try:
        cdat_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="cdat")
        value = cdat_chunk.value[:dimensions]
    except ChunkNotFoundError:
        value = None

    try:
        utf8_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="Utf8")
        expression = str_contents(utf8_chunk)
    except ChunkNotFoundError:
        expression = ""

    keyframes = _parse_keyframes(tdbs_child_chunks, time_scale, is_spatial)

    return Property(
        animated=animated,
        color=color,
        dimensions_separated=dimensions_separated,
        dimensions=dimensions,
        enabled=enabled,
        expression_enabled=expression_enabled,
        expression=expression,
        integer=integer,
        is_spatial=is_spatial,
        keyframes=keyframes,
        locked_ratio=locked_ratio,
        match_name=match_name,
        name=name,
        no_value=no_value,
        property_control_type=property_control_type,
        property_value_type=property_value_type,
        value=value,
        vector=vector,
    )


def _parse_keyframes(
    tdbs_child_chunks: list[Aep.Chunk], time_scale: float, is_spatial: bool
) -> list[Keyframe]:
    """Parse keyframes from a property's child chunks."""
    try:
        list_chunk = find_by_list_type(chunks=tdbs_child_chunks, list_type="list")
    except ChunkNotFoundError:
        return []

    kf_items = parse_ldat_items(list_chunk, is_spatial=is_spatial)

    keyframes = [
        Keyframe(
            frame_time=round(kf.time_raw / time_scale),
            keyframe_interpolation_type=KeyframeInterpolationType.from_binary(
                kf.keyframe_interpolation_type
            ),
            label=Label(int(kf.label)),
            continuous_bezier=kf.continuous_bezier,
            auto_bezier=kf.auto_bezier,
            roving_across_time=kf.roving_across_time,
        )
        for kf in kf_items
    ]
    return keyframes


def _parse_effect_param_defs(
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
    prop.min_value = param_def.get("min_value") or prop.min_value
    prop.max_value = param_def.get("max_value") or prop.max_value
    prop.nb_options = param_def.get("nb_options")
    prop.property_parameters = param_def.get("property_parameters")


def _parse_effect_properties(
    tdgp_chunk: Aep.Chunk,
    param_defs: dict[str, dict[str, Any]],
    time_scale: float,
) -> list[Property | PropertyGroup]:
    """Parse effect properties and merge with parameter definitions.

    Iterates the tdgp chunk's sub-properties, parses each one, and merges
    in the corresponding parameter definition if available.

    Args:
        tdgp_chunk: The tdgp chunk containing property data.
        param_defs: Parameter definitions to merge into properties.
        time_scale: The time scale of the parent composition.

    Returns:
        List of parsed and merged properties.
    """
    properties: list[Property | PropertyGroup] = []
    chunks_by_property = get_chunks_by_match_name(tdgp_chunk)
    for match_name, prop_chunks in chunks_by_property.items():
        first_chunk = prop_chunks[0]
        if first_chunk.list_type == "tdbs":
            prop = parse_property(
                tdbs_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
            )
            if match_name in param_defs:
                _merge_param_def(prop, param_defs[match_name])
            properties.append(prop)
        elif first_chunk.list_type == "tdgp":
            # Encountered with "ADBE FreePin3" effect (Obsolete > Puppet)
            pass
        else:
            raise NotImplementedError(
                f"Cannot parse parameter value : {first_chunk.list_type}"
            )
    return properties


def parse_effect(
    sspc_chunk: Aep.Chunk, group_match_name: str, time_scale: float
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
            Aep.PropertyType.indexed_group`) may not have a name value, but
            always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
    """
    sspc_child_chunks = sspc_chunk.chunks
    fnam_chunk = find_by_type(chunks=sspc_child_chunks, chunk_type="fnam")

    utf8_chunk = fnam_chunk.chunk
    tdgp_chunk = find_by_list_type(chunks=sspc_child_chunks, list_type="tdgp")
    name = _get_user_defined_name(tdgp_chunk) or str_contents(utf8_chunk)

    param_defs = _parse_effect_param_defs(sspc_child_chunks)
    properties = _parse_effect_properties(tdgp_chunk, param_defs, time_scale)

    return PropertyGroup(
        enabled=True,
        is_effect=True,
        match_name=group_match_name,
        name=name,
        properties=properties,
    )


def _parse_effect_parameter_def(parameter_chunks: list[Aep.Chunk]) -> dict[str, Any]:
    """Parse effect parameter definition from pard chunk, returning a dict of values."""
    pard_chunk = find_by_type(chunks=parameter_chunks, chunk_type="pard")

    control_type = PropertyControlType(int(pard_chunk.property_control_type))

    result: dict[str, Any] = {
        "name": pard_chunk.name,
        "property_control_type": control_type,
    }

    if control_type == PropertyControlType.ANGLE:
        result["last_value"] = pard_chunk.last_value
        result["property_value_type"] = PropertyValueType.ORIENTATION

    elif control_type == PropertyControlType.BOOLEAN:
        result["last_value"] = pard_chunk.last_value
        result["default_value"] = pard_chunk.default

    elif control_type == PropertyControlType.COLOR:
        result["last_value"] = pard_chunk.last_color
        result["default_value"] = pard_chunk.default_color
        result["max_value"] = pard_chunk.max_color
        result["property_value_type"] = PropertyValueType.COLOR

    elif control_type == PropertyControlType.ENUM:
        result["last_value"] = pard_chunk.last_value
        result["nb_options"] = pard_chunk.nb_options
        result["default_value"] = pard_chunk.default

    elif control_type == PropertyControlType.SCALAR:
        result["last_value"] = pard_chunk.last_value
        result["min_value"] = pard_chunk.min_value
        result["max_value"] = pard_chunk.max_value

    elif control_type == PropertyControlType.SLIDER:
        result["last_value"] = pard_chunk.last_value
        result["max_value"] = pard_chunk.max_value

    elif control_type == PropertyControlType.THREE_D:
        result["last_value"] = [
            pard_chunk.last_value_x,
            pard_chunk.last_value_y,
            pard_chunk.last_value_z,
        ]

    elif control_type == PropertyControlType.TWO_D:
        result["last_value"] = [pard_chunk.last_value_x, pard_chunk.last_value_y]

    with suppress(ChunkNotFoundError):
        pdnm_chunk = find_by_type(chunks=parameter_chunks, chunk_type="pdnm")
        utf8_chunk = pdnm_chunk.chunk
        pdnm_data = str_contents(utf8_chunk)
        if control_type == PropertyControlType.ENUM:
            result["property_parameters"] = pdnm_data.split("|")
        elif pdnm_data:
            result["name"] = pdnm_data

    return result


def parse_markers(
    mrst_chunk: Aep.Chunk, group_match_name: str, time_scale: float, frame_rate: float
) -> list[MarkerValue]:
    """
    Parse markers.

    Args:
        mrst_chunk: The MRST chunk to parse.
        group_match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized. An indexed group (`PropertyBase.property_type ==
            Aep.PropertyType.indexed_group`) may not have a name value, but
            always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        frame_rate: The frame rate of the parent composition, used to compute
            marker duration in seconds.
    """
    tdbs_chunk = find_by_list_type(chunks=mrst_chunk.chunks, list_type="tdbs")
    marker_group = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=group_match_name,
        time_scale=time_scale,
    )
    mrky_chunk = find_by_list_type(chunks=mrst_chunk.chunks, list_type="mrky")
    nmrd_chunks = filter_by_list_type(chunks=mrky_chunk.chunks, list_type="Nmrd")
    markers = []
    for i, nmrd_chunk in enumerate(nmrd_chunks):
        frame_time = marker_group.keyframes[i].frame_time
        marker = parse_marker(
            nmrd_chunk=nmrd_chunk,
            frame_rate=frame_rate,
            frame_time=frame_time,
        )
        markers.append(marker)
    return markers


def parse_marker(
    nmrd_chunk: Aep.Chunk, frame_rate: float, frame_time: int
) -> MarkerValue:
    """
    Parse a marker.

    Args:
        nmrd_chunk: The NMRD chunk to parse.
        frame_rate: The frame rate of the parent composition (unused but kept
            for API consistency).
        frame_time: The time of the marker, in frames.
    """
    nmhd_chunk = find_by_type(chunks=nmrd_chunk.chunks, chunk_type="NmHd")

    utf8_chunks = filter_by_type(chunks=nmrd_chunk.chunks, chunk_type="Utf8")

    # Marker duration from Kaitai instance (stored in 600ths of a second)
    duration = nmhd_chunk.duration

    # Parse cue point params
    params = {}
    for param_name, param_value in split_into_batches(utf8_chunks[5:], 2):
        params[str_contents(param_name)] = str_contents(param_value)

    return MarkerValue(
        chapter=str_contents(utf8_chunks[1]),
        comment=str_contents(utf8_chunks[0]),
        cue_point_name=str_contents(utf8_chunks[4]),
        duration=duration,
        navigation=nmhd_chunk.navigation,
        frame_target=str_contents(utf8_chunks[3]),
        url=str_contents(utf8_chunks[2]),
        label=Label(int(nmhd_chunk.label)),
        protected_region=nmhd_chunk.protected_region,
        params=params,
        frame_duration=nmhd_chunk.frame_duration,
        frame_time=frame_time,
    )


def _get_user_defined_name(root_chunk: Aep.Chunk) -> str:
    """Get the user defined name of the property if there is one, else an empty string.

    Args:
        root_chunk (Aep.Chunk): The LIST chunk to parse.
    """
    tdsn_chunk = find_by_type(chunks=root_chunk.chunks, chunk_type="tdsn")
    utf8_chunk = tdsn_chunk.chunk
    name = str_contents(utf8_chunk)

    # Check if there is a custom user defined name added.
    # The default if there is not is "-_0_/-".
    if name != "-_0_/-":
        return name
    return ""
