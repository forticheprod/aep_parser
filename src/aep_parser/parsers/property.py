from __future__ import annotations

from contextlib import suppress
from typing import Any

from ..kaitai import Aep
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.enums import KeyframeInterpolationType
from ..models.properties.keyframe import Keyframe
from ..models.properties.marker import MarkerValue
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from .match_names import MATCH_NAME_TO_NICE_NAME
from .utils import (
    get_chunks_by_match_name,
    parse_ldat_items,
    split_in_chunks,
)


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
            raise NotImplementedError(
                f"Cannot parse {first_chunk.list_type} property"
            )
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
    prop.property_control_type = Aep.PropertyControlType.angle
    prop.property_value_type = Aep.LdatItemType.orientation

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

    # btdk_chunk = find_by_list_type(
    #     chunks=btds_chunk.chunks,
    #     list_type="btdk"
    # )
    # parser = CosParser(
    #     io.BytesIO(btdk_chunk.binary_data),
    #     len(btdk_chunk.binary_data)
    # )

    # content_as_dict = parser.parse()
    return prop


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

    # Get property settings from tdsb chunk
    tdsb_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="tdsb")

    locked_ratio = tdsb_chunk.locked_ratio
    enabled = tdsb_chunk.enabled
    dimensions_separated = tdsb_chunk.dimensions_separated

    # Get nice name
    name = _get_user_defined_name(tdbs_chunk) or MATCH_NAME_TO_NICE_NAME.get(match_name, match_name)

    # Get property type info from tdb4 chunk
    tdb4_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="tdb4")

    is_spatial = tdb4_chunk.is_spatial
    expression_enabled = tdb4_chunk.expression_enabled
    animated = tdb4_chunk.animated
    dimensions = tdb4_chunk.dimensions
    integer = tdb4_chunk.integer
    vector = tdb4_chunk.vector
    no_value = tdb4_chunk.no_value
    color = tdb4_chunk.color

    # Determine property control and value types
    property_control_type = Aep.PropertyControlType.unknown
    property_value_type = Aep.LdatItemType.unknown

    if no_value:
        property_value_type = Aep.LdatItemType.no_value
    if color:
        property_control_type = Aep.PropertyControlType.color
        property_value_type = Aep.LdatItemType.color
    elif integer:
        property_control_type = Aep.PropertyControlType.boolean
        property_value_type = Aep.LdatItemType.one_d
    elif vector:
        if dimensions == 1:
            property_control_type = Aep.PropertyControlType.scalar
            property_value_type = Aep.LdatItemType.one_d
        elif dimensions == 2:
            property_control_type = Aep.PropertyControlType.two_d
            property_value_type = (
                Aep.LdatItemType.two_d_spatial
                if is_spatial
                else Aep.LdatItemType.two_d
            )
        elif dimensions == 3:
            property_control_type = Aep.PropertyControlType.three_d
            property_value_type = (
                Aep.LdatItemType.three_d_spatial
                if is_spatial
                else Aep.LdatItemType.three_d
            )

    if property_control_type == Aep.PropertyControlType.unknown:
        print(
            f"Could not determine type for property {match_name}"
            f" | name: {name}"
            f" | dimensions: {dimensions}"
            f" | animated: {animated}"
            f" | integer: {integer}"
            f" | is_spatial: {is_spatial}"
            f" | vector: {vector}"
            f" | no_value: {no_value}"
            f" | color: {color}"
        )

    # Get property value
    try:
        cdat_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="cdat")
        value = cdat_chunk.value[:dimensions]
    except ChunkNotFoundError:
        value = None

    # Get property expression
    try:
        utf8_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="Utf8")
        expression = str_contents(utf8_chunk)
    except ChunkNotFoundError:
        expression = ""

    # Get property keyframes
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
            frame_time=int(round(kf.time_raw / time_scale)),
            keyframe_interpolation_type=KeyframeInterpolationType.from_binary(
                kf.keyframe_interpolation_type
            ),
            label=kf.label,
            continuous_bezier=kf.continuous_bezier,
            auto_bezier=kf.auto_bezier,
            roving_across_time=kf.roving_across_time,
        )
        for kf in kf_items
    ]
    return keyframes


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

    # Get effect parameter definitions from parT chunk
    param_defs: dict[str, dict[str, Any]] = {}

    part_chunk = find_by_list_type(chunks=sspc_child_chunks, list_type="parT")

    chunks_by_parameter = get_chunks_by_match_name(part_chunk)
    for index, (match_name, parameter_chunks) in enumerate(
        chunks_by_parameter.items()
    ):
        # Skip first, it describes parent
        if index == 0:
            continue
        param_defs[match_name] = _parse_effect_parameter_def(parameter_chunks)

    # Parse properties and merge with parameter definitions
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
            # Merge parameter definition if available
            if match_name in param_defs:
                param_def = param_defs[match_name]
                prop.name = param_def.get("name") or prop.name
                prop.property_control_type = param_def.get(
                    "property_control_type", prop.property_control_type
                )
                prop.property_value_type = param_def.get(
                    "property_value_type", prop.property_value_type
                )
                prop.last_value = param_def.get("last_value")
                prop.default_value = param_def.get("default_value")
                prop.min_value = param_def.get("min_value") or prop.min_value
                prop.max_value = param_def.get("max_value") or prop.max_value
                prop.nb_options = param_def.get("nb_options")
                prop.property_parameters = param_def.get("property_parameters")
            properties.append(prop)
        elif first_chunk.list_type == "tdgp":
            # Encountered with "ADBE FreePin3" effect (Obsolete > Puppet)
            pass
        else:
            raise NotImplementedError(
                f"Cannot parse parameter value : {first_chunk.list_type}"
            )

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

    result: dict[str, Any] = {
        "name": pard_chunk.name,
        "property_control_type": pard_chunk.property_control_type,
    }
    control_type = pard_chunk.property_control_type

    if control_type == Aep.PropertyControlType.angle:
        result["last_value"] = pard_chunk.last_value
        result["property_value_type"] = Aep.LdatItemType.orientation

    elif control_type == Aep.PropertyControlType.boolean:
        result["last_value"] = pard_chunk.last_value
        result["default_value"] = pard_chunk.default

    elif control_type == Aep.PropertyControlType.color:
        result["last_value"] = pard_chunk.last_color
        result["default_value"] = pard_chunk.default_color
        result["max_value"] = pard_chunk.max_color
        result["property_value_type"] = Aep.LdatItemType.color

    elif control_type == Aep.PropertyControlType.enum:
        result["last_value"] = pard_chunk.last_value
        result["nb_options"] = pard_chunk.nb_options
        result["default_value"] = pard_chunk.default

    elif control_type == Aep.PropertyControlType.scalar:
        result["last_value"] = pard_chunk.last_value
        result["min_value"] = pard_chunk.min_value
        result["max_value"] = pard_chunk.max_value

    elif control_type == Aep.PropertyControlType.slider:
        result["last_value"] = pard_chunk.last_value
        result["max_value"] = pard_chunk.max_value

    elif control_type == Aep.PropertyControlType.three_d:
        result["last_value"] = [
            pard_chunk.last_value_x,
            pard_chunk.last_value_y,
            pard_chunk.last_value_z,
        ]

    elif control_type == Aep.PropertyControlType.two_d:
        result["last_value"] = [pard_chunk.last_value_x, pard_chunk.last_value_y]

    # Check for display name override or enum options
    with suppress(ChunkNotFoundError):
        pdnm_chunk = find_by_type(chunks=parameter_chunks, chunk_type="pdnm")
        utf8_chunk = pdnm_chunk.chunk
        pdnm_data = str_contents(utf8_chunk)
        if control_type == Aep.PropertyControlType.enum:
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
    # Get keyframes (markers time)
    marker_group = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=group_match_name,
        time_scale=time_scale,
    )
    mrky_chunk = find_by_list_type(chunks=mrst_chunk.chunks, list_type="mrky")
    # Get each marker with its frame_time
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


def parse_marker(nmrd_chunk: Aep.Chunk, frame_rate: float, frame_time: int) -> MarkerValue:
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

    # FIXME Marker duration is stored in 600ths of a second
    # It is hardcoded here until we have a better time representation
    duration = nmhd_chunk.frame_duration / 600

    # Parse cue point params
    params = {}
    for param_name, param_value in split_in_chunks(utf8_chunks[5:], 2):
        params[str_contents(param_name)] = str_contents(param_value)

    return MarkerValue(
        chapter=str_contents(utf8_chunks[1]),
        comment=str_contents(utf8_chunks[0]),
        cue_point_name=str_contents(utf8_chunks[4]),
        duration=duration,
        navigation=nmhd_chunk.navigation,
        frame_target=str_contents(utf8_chunks[3]),
        url=str_contents(utf8_chunks[2]),
        label=nmhd_chunk.label,
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
    # Look for a tdsn which specifies the user-defined name of the property
    tdsn_chunk = find_by_type(chunks=root_chunk.chunks, chunk_type="tdsn")
    utf8_chunk = tdsn_chunk.chunk
    name = str_contents(utf8_chunk)

    # Check if there is a custom user defined name added.
    # The default if there is not is "-_0_/-".
    if name != "-_0_/-":
        return name
    return ""
