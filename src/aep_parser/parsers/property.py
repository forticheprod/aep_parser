from __future__ import annotations

from kaitaistruct import BytesIO, KaitaiStream

from ..kaitai import Aep
from ..kaitai.utils import (
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    get_enum_value,
    str_contents,
)
from ..models.properties.keyframe import Keyframe
from ..models.properties.marker import Marker
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from .mappings import map_keyframe_interpolation_type
from .match_names import MATCH_NAME_TO_NICE_NAME
from .utils import (
    get_chunks_by_match_name,
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
            localized. An indexed group (PropertyBase.propertyType ==
            Aep.PropertyType.indexed_group) may not have a name value, but
            always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
    """
    nice_name = MATCH_NAME_TO_NICE_NAME.get(group_match_name, group_match_name)

    properties = []
    chunks_by_sub_prop = get_chunks_by_match_name(tdgp_chunk)
    for match_name, sub_prop_chunks in chunks_by_sub_prop.items():
        first_chunk = sub_prop_chunks[0]
        if first_chunk.data.list_type == "tdgp":
            sub_prop = parse_property_group(
                tdgp_chunk=first_chunk,
                group_match_name=match_name,
                time_scale=time_scale,
            )
        elif first_chunk.data.list_type == "sspc":
            sub_prop = parse_effect(
                sspc_chunk=first_chunk,
                group_match_name=match_name,
                time_scale=time_scale,
            )
        elif first_chunk.data.list_type == "tdbs":
            sub_prop = parse_property(
                tdbs_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
            )
        elif first_chunk.data.list_type == "otst":
            sub_prop = parse_orientation(
                otst_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
            )
        elif first_chunk.data.list_type == "btds":
            sub_prop = parse_text_document(
                btds_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
            )
        else:
            raise NotImplementedError(
                f"Cannot parse {first_chunk.data.list_type} property"
            )
        properties.append(sub_prop)

    prop_group = PropertyGroup(
        match_name=group_match_name,
        name=nice_name,
        is_effect=False,
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
    tdbs_chunk = find_by_list_type(chunks=otst_chunk.data.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
    )
    # Override types for orientation
    prop.property_control_type = Aep.PropertyControlType.angle
    prop.property_value_type = Aep.PropertyValueType.orientation

    # otky_chunk = find_by_list_type(
    #     chunks=otst_chunk.data.chunks,
    #     list_type="otky"
    # )
    # otda_chunks = filter_by_type(
    #     chunks=otky_chunk.data.chunks,
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
    tdbs_chunk = find_by_list_type(chunks=btds_chunk.data.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
    )

    # btdk_chunk = find_by_list_type(
    #     chunks=btds_chunk.data.chunks,
    #     list_type="btdk"
    # )
    # parser = CosParser(
    #     io.BytesIO(btdk_chunk.data.binary_data),
    #     len(btdk_chunk.data.binary_data)
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
    tdbs_child_chunks = tdbs_chunk.data.chunks

    # Get property settings from tdsb chunk
    tdsb_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="tdsb")
    tdsb_data = tdsb_chunk.data
    locked_ratio = tdsb_data.locked_ratio
    enabled = tdsb_data.enabled
    dimensions_separated = tdsb_data.dimensions_separated

    # Get nice name if user-defined
    nice_name = _get_nice_name(tdbs_chunk)
    name = nice_name or MATCH_NAME_TO_NICE_NAME.get(match_name, match_name)

    # Get property type info from tdb4 chunk
    tdb4_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="tdb4")
    tdb4_data = tdb4_chunk.data
    is_spatial = tdb4_data.is_spatial
    expression_enabled = tdb4_data.expression_enabled
    animated = tdb4_data.animated
    dimensions = tdb4_data.dimensions
    integer = tdb4_data.integer
    vector = tdb4_data.vector
    no_value = tdb4_data.no_value
    color = tdb4_data.color

    # Determine property control and value types
    property_control_type = Aep.PropertyControlType.unknown
    property_value_type = Aep.PropertyValueType.unknown

    if no_value:
        property_value_type = Aep.PropertyValueType.no_value
    if color:
        property_control_type = Aep.PropertyControlType.color
        property_value_type = Aep.PropertyValueType.color
    elif integer:
        property_control_type = Aep.PropertyControlType.boolean
        property_value_type = Aep.PropertyValueType.one_d
    elif vector:
        if dimensions == 1:
            property_control_type = Aep.PropertyControlType.scalar
            property_value_type = Aep.PropertyValueType.one_d
        elif dimensions == 2:
            property_control_type = Aep.PropertyControlType.two_d
            property_value_type = (
                Aep.PropertyValueType.two_d_spatial
                if is_spatial
                else Aep.PropertyValueType.two_d
            )
        elif dimensions == 3:
            property_control_type = Aep.PropertyControlType.three_d
            property_value_type = (
                Aep.PropertyValueType.three_d_spatial
                if is_spatial
                else Aep.PropertyValueType.three_d
            )

    if property_control_type == Aep.PropertyControlType.unknown:
        print(
            f"Could not determine type for property {match_name}"
            f" | nice_name: {nice_name}"
            f" | dimensions: {dimensions}"
            f" | animated: {animated}"
            f" | integer: {integer}"
            f" | is_spatial: {is_spatial}"
            f" | vector: {vector}"
            f" | no_value: {no_value}"
            f" | color: {color}"
        )

    # Get property value
    value = None
    cdat_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="cdat")
    if cdat_chunk is not None:
        value = cdat_chunk.data.value[:dimensions]

    # Get property expression
    expression = None
    utf8_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="Utf8")
    if utf8_chunk is not None:
        expression = str_contents(utf8_chunk).splitlines()

    # Get property keyframes
    keyframes = _parse_keyframes(tdbs_child_chunks, time_scale, is_spatial)

    return Property(
        match_name=match_name,
        name=name,
        enabled=enabled,
        property_control_type=property_control_type,
        expression=expression,
        expression_enabled=expression_enabled,
        property_value_type=property_value_type,
        value=value,
        dimensions_separated=dimensions_separated,
        is_spatial=is_spatial,
        locked_ratio=locked_ratio,
        keyframes=keyframes,
        animated=animated,
        dimensions=dimensions,
        integer=integer,
        vector=vector,
        no_value=no_value,
        color=color,
    )


def _parse_keyframes(
    tdbs_child_chunks: list[Aep.Chunk], time_scale: float, is_spatial: bool
) -> list[Keyframe]:
    """Parse keyframes from a property's child chunks."""
    keyframes: list[Keyframe] = []
    list_chunk = find_by_list_type(chunks=tdbs_child_chunks, list_type="list")
    if list_chunk is None:
        return keyframes

    list_child_chunks = list_chunk.data.chunks
    lhd3_chunk = find_by_type(chunks=list_child_chunks, chunk_type="lhd3")
    lhd3_data = lhd3_chunk.data
    nb_keyframes = lhd3_data.nb_keyframes
    if not nb_keyframes:
        return keyframes

    len_keyframe = lhd3_data.len_keyframe
    keyframes_type = lhd3_data.keyframes_type
    if keyframes_type == Aep.PropertyValueType.three_d and is_spatial:
        keyframes_type = Aep.PropertyValueType.three_d_spatial

    ldat_chunk = find_by_type(chunks=list_child_chunks, chunk_type="ldat")
    ldat_data = ldat_chunk.data.keyframes
    for keyframe_data in split_in_chunks(ldat_data, len_keyframe):
        kf_chunk = Aep.Keyframe(
            key_type=keyframes_type,
            _io=KaitaiStream(BytesIO(keyframe_data)),
        )
        keyframes.append(
            Keyframe(
                frame_time=int(round(kf_chunk.time_raw / time_scale)),
                keyframe_interpolation_type=map_keyframe_interpolation_type(
                    get_enum_value(kf_chunk.keyframe_interpolation_type)
                ),
                label=kf_chunk.label,
                continuous_bezier=kf_chunk.continuous_bezier,
                auto_bezier=kf_chunk.auto_bezier,
                roving_across_time=kf_chunk.roving_across_time,
            )
        )
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
            localized. An indexed group (PropertyBase.propertyType ==
            Aep.PropertyType.indexed_group) may not have a name value, but
            always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
    """
    sspc_child_chunks = sspc_chunk.data.chunks
    fnam_chunk = find_by_type(chunks=sspc_child_chunks, chunk_type="fnam")
    utf8_chunk = fnam_chunk.data.chunk
    tdgp_chunk = find_by_list_type(chunks=sspc_child_chunks, list_type="tdgp")
    nice_name = _get_nice_name(tdgp_chunk) or str_contents(utf8_chunk)

    # Get effect parameter definitions from parT chunk
    param_defs: dict[str, dict] = {}
    part_chunk = find_by_list_type(chunks=sspc_child_chunks, list_type="parT")
    if part_chunk:
        chunks_by_parameter = get_chunks_by_match_name(part_chunk)
        for index, (match_name, parameter_chunks) in enumerate(
            chunks_by_parameter.items()
        ):
            # Skip first, it describes parent
            if index == 0:
                continue
            param_defs[match_name] = _parse_effect_parameter_def(parameter_chunks)

    # Parse properties and merge with parameter definitions
    properties: list[Property] = []
    chunks_by_property = get_chunks_by_match_name(tdgp_chunk)
    for match_name, prop_chunks in chunks_by_property.items():
        first_chunk = prop_chunks[0]
        if first_chunk.data.list_type == "tdbs":
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
        elif first_chunk.data.list_type == "tdgp":
            # Encountered with "ADBE FreePin3" effect (Obsolete > Puppet)
            pass
        else:
            raise NotImplementedError(
                f"Cannot parse parameter value : {first_chunk.data.list_type}"
            )

    return PropertyGroup(
        match_name=group_match_name,
        name=nice_name,
        is_effect=True,
        properties=properties,
    )


def _parse_effect_parameter_def(parameter_chunks: list[Aep.Chunk]) -> dict:
    """Parse effect parameter definition from pard chunk, returning a dict of values."""
    pard_chunk = find_by_type(chunks=parameter_chunks, chunk_type="pard")
    pard_data = pard_chunk.data

    result: dict = {
        "name": pard_data.name,
        "property_control_type": pard_data.property_control_type,
    }
    control_type = pard_data.property_control_type

    if control_type == Aep.PropertyControlType.angle:
        result["last_value"] = pard_data.last_value
        result["property_value_type"] = Aep.PropertyValueType.orientation

    elif control_type == Aep.PropertyControlType.boolean:
        result["last_value"] = pard_data.last_value
        result["default_value"] = pard_data.default

    elif control_type == Aep.PropertyControlType.color:
        result["last_value"] = pard_data.last_color
        result["default_value"] = pard_data.default_color
        result["max_value"] = pard_data.max_color
        result["property_value_type"] = Aep.PropertyValueType.color

    elif control_type == Aep.PropertyControlType.enum:
        result["last_value"] = pard_data.last_value
        result["nb_options"] = pard_data.nb_options
        result["default_value"] = pard_data.default

    elif control_type == Aep.PropertyControlType.scalar:
        result["last_value"] = pard_data.last_value
        result["min_value"] = pard_data.min_value
        result["max_value"] = pard_data.max_value

    elif control_type == Aep.PropertyControlType.slider:
        result["last_value"] = pard_data.last_value
        result["max_value"] = pard_data.max_value

    elif control_type == Aep.PropertyControlType.three_d:
        result["last_value"] = [
            pard_data.last_value_x,
            pard_data.last_value_y,
            pard_data.last_value_z,
        ]

    elif control_type == Aep.PropertyControlType.two_d:
        result["last_value"] = [pard_data.last_value_x, pard_data.last_value_y]

    # Check for display name override or enum options
    pdnm_chunk = find_by_type(chunks=parameter_chunks, chunk_type="pdnm")
    if pdnm_chunk is not None:
        utf8_chunk = pdnm_chunk.data.chunk
        pdnm_data = str_contents(utf8_chunk)
        if control_type == Aep.PropertyControlType.enum:
            result["property_parameters"] = pdnm_data.split("|")
        elif pdnm_data:
            result["name"] = pdnm_data

    return result


def parse_markers(
    mrst_chunk: Aep.Chunk, group_match_name: str, time_scale: float, frame_rate: float
) -> list[Marker]:
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
            localized. An indexed group (PropertyBase.propertyType ==
            Aep.PropertyType.indexed_group) may not have a name value, but
            always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        frame_rate: The frame rate of the parent composition, used to compute
            marker duration in seconds.
    """
    tdbs_chunk = find_by_list_type(chunks=mrst_chunk.data.chunks, list_type="tdbs")
    # Get keyframes (markers time)
    marker_group = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=group_match_name,
        time_scale=time_scale,
    )
    mrky_chunk = find_by_list_type(chunks=mrst_chunk.data.chunks, list_type="mrky")
    # Get each marker with its frame_time
    nmrd_chunks = filter_by_list_type(chunks=mrky_chunk.data.chunks, list_type="Nmrd")
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


def parse_marker(nmrd_chunk: Aep.Chunk, frame_rate: float, frame_time: int) -> Marker:
    """
    Parse a marker.

    Args:
        nmrd_chunk: The NMRD chunk to parse.
        frame_rate: The frame rate of the parent composition (unused but kept
            for API consistency).
        frame_time: The time of the marker, in frames.
    """
    nmhd_chunk = find_by_type(chunks=nmrd_chunk.data.chunks, chunk_type="NmHd")
    nmhd_data = nmhd_chunk.data
    utf8_chunks = filter_by_type(chunks=nmrd_chunk.data.chunks, chunk_type="Utf8")

    # FIXME Marker duration is stored in 600ths of a second
    # It is hardcoded here until we have a better time representation
    duration = nmhd_data.frame_duration / 600

    # Parse cue point params
    params = {}
    for param_name, param_value in split_in_chunks(utf8_chunks[5:], 2):
        params[str_contents(param_name)] = str_contents(param_value)

    return Marker(
        chapter=str_contents(utf8_chunks[1]),
        comment=str_contents(utf8_chunks[0]),
        cue_point_name=str_contents(utf8_chunks[4]),
        duration=duration,
        navigation=nmhd_data.navigation,
        frame_target=str_contents(utf8_chunks[3]),
        url=str_contents(utf8_chunks[2]),
        label=nmhd_data.label,
        protected_region=nmhd_data.protected_region,
        params=params,
        frame_duration=nmhd_data.frame_duration,
        frame_time=frame_time,
    )


def _get_nice_name(root_chunk: Aep.Chunk) -> str | None:
    """Get the user defined name of the property if there is one, else None.

    Args:
        root_chunk (Aep.Chunk): The LIST chunk to parse.
    """
    # Look for a tdsn which specifies the user-defined name of the property
    tdsn_chunk = find_by_type(chunks=root_chunk.data.chunks, chunk_type="tdsn")
    utf8_chunk = tdsn_chunk.data.chunk
    nice_name = str_contents(utf8_chunk)

    # Check if there is a custom user defined name added.
    # The default if there is not is "-_0_/-".
    if nice_name != "-_0_/-":
        return nice_name
    return None
