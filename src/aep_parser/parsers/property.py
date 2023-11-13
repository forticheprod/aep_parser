# coding: utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
    division
)

import io
import sys

from kaitaistruct import KaitaiStream, BytesIO

from ..cos.cos import CosParser
from ..kaitai.aep import Aep
from ..kaitai.utils import (
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.properties.keyframe import Keyframe
from ..models.properties.marker import Marker
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from .utils import (
    get_chunks_by_match_name,
    split_in_chunks,
)


MATCH_NAME_TO_NICE_NAME = {
    "ADBE Marker": "Marker",
    "ADBE Time Remapping": "Time Remap",
    "ADBE MTrackers": "Motion Trackers",
    "ADBE Mask Parade": "Masks",
    "ADBE Effect Parade": "Effects",
    "ADBE Layer Overrides": "Essential Properties",
    "ADBE Transform Group": "Transform",
    "ADBE Anchor Point": "Anchor Point",
    "ADBE Position": "Position",
    "ADBE Position_0": "X Position",
    "ADBE Position_1": "Y Position",
    "ADBE Position_2": "Z Position",
    "ADBE Scale": "Scale",
    "ADBE Orientation": "Orientation",
    "ADBE Rotate X": "X Rotation",
    "ADBE Rotate Y": "Y Rotation",
    "ADBE Rotate Z": "Z Rotation",
    "ADBE Opacity": "Opacity",
    "ADBE Audio Group": "Audio",
    "ADBE Audio Levels": "Audio Levels",
}


def parse_property_group(tdgp_chunk, group_match_name, time_scale):
    """
    Args:
        tdgp_chunk (Aep.Chunk): The TDGP chunk to parse.
        group_match_name (str): A special name for the property used to build unique
                                naming paths. The match name is not displayed, but you
                                can refer to it in scripts. Every property has a unique
                                match-name identifier. Match names are stable from
                                version to version regardless of the display name (the
                                name attribute value) or any changes to the application.
                                Unlike the display name, it is not localized. An indexed
                                group (PropertyBase.propertyType ==
                                Aep.PropertyType.indexed_group) may not have a name
                                value, but always has a match_name value.
        time_scale (float): The time scale of the parent composition, used as a divisor
                            for some frame values.
    Returns:
        PropertyGroup: The parsed property group.
    """
    nice_name = MATCH_NAME_TO_NICE_NAME.get(group_match_name, group_match_name)

    prop_group = PropertyGroup(
        match_name=group_match_name,
        name=nice_name,
        is_effect=False,
    )

    chunks_by_sub_prop = get_chunks_by_match_name(tdgp_chunk)
    for (match_name, sub_prop_chunks) in chunks_by_sub_prop.items():
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
            # TODO Parse om-s, GCst, mrst, btds, OvG2
            raise NotImplementedError(
                "Cannot parse {} property".format(
                    first_chunk.data.list_type
                )
            )
        prop_group.properties.append(sub_prop)

    return prop_group


def parse_orientation(otst_chunk, match_name, time_scale):
    """
    Args:
        otst_chunk (Aep.Chunk): The OTST chunk to parse.
        match_name (str): A special name for the property used to build unique naming
                          paths. The match name is not displayed, but you can refer to
                          it in scripts. Every property has a unique match-name
                          identifier. Match names are stable from version to version
                          regardless of the display name (the name attribute value) or
                          any changes to the application. Unlike the display name, it is
                          not localized.
        time_scale (float): The time scale of the parent composition, used as a divisor
                            for some frame values.
    Returns:
        Property: The parsed orientation property.
    """
    tdbs_chunk = find_by_list_type(
        chunks=otst_chunk.data.chunks,
        list_type="tdbs"
    )
    prop_name = MATCH_NAME_TO_NICE_NAME.get(match_name, match_name)
    prop = Property(
        match_name=match_name,
        name=prop_name,
        property_control_type=Aep.PropertyControlType.angle,
        property_value_type=Aep.PropertyValueType.orientation,
    )
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
        prop=prop,
    )

    # otky_chunk = find_by_list_type(
    #     chunks=otst_chunk.data.chunks,
    #     list_type="otky"
    # )
    # otda_chunks = filter_by_type(
    #     chunks=otky_chunk.data.chunks,
    #     chunk_type="otda"
    # )
    # TODO parse otda_chunks
    return prop


def parse_text_document(btds_chunk, match_name, time_scale):
    """
    Args:
        btds_chunk (Aep.Chunk): The BTDS chunk to parse.
        match_name (str): A special name for the property used to build unique naming
                          paths. The match name is not displayed, but you can refer to
                          it in scripts. Every property has a unique match-name
                          identifier. Match names are stable from version to version
                          regardless of the display name (the name attribute value) or
                          any changes to the application. Unlike the display name, it is
                          not localized.
        time_scale (float): The time scale of the parent composition, used as a divisor
                            for some frame values.
    Returns:
        Property: The parsed text document property.
    """
    tdbs_chunk = find_by_list_type(
        chunks=btds_chunk.data.chunks,
        list_type="tdbs"
    )
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
    # FIXME does not work in PY2 as cos.py uses b-strings
    # if sys.version_info >= (3, 0):
    #     content_as_dict = parser.parse()
    #     # TODO get rid of "\ufeff" in string values
    #     # TODO convert resulting dict into readable data
    return prop


def parse_property(tdbs_chunk, match_name, time_scale, prop=None):
    """
    Args:
        tdbs_chunk (Aep.Chunk): The TDBS chunk to parse.
        match_name (str): A special name for the property used to build unique naming
                          paths. The match name is not displayed, but you can refer to
                          it in scripts. Every property has a unique match-name
                          identifier. Match names are stable from version to version
                          regardless of the display name (the name attribute value) or
                          any changes to the application. Unlike the display name, it is
                          not localized.
        time_scale (float): The time scale of the parent composition, used as a divisor
                            for some frame values.
    Returns:
        Property: The parsed property.
    """
    if prop is None:
        prop_name = MATCH_NAME_TO_NICE_NAME.get(match_name, match_name)
        prop = Property(
            match_name=match_name,
            name=prop_name,
        )

    tdbs_child_chunks = tdbs_chunk.data.chunks

    tdsb_chunk = find_by_type(
        chunks=tdbs_child_chunks,
        chunk_type="tdsb"
    )
    tdsb_data = tdsb_chunk.data
    prop.locked_ratio = tdsb_data.locked_ratio
    prop.enabled = tdsb_data.enabled
    prop.dimensions_separated = tdsb_data.dimensions_separated

    nice_name = _get_nice_name(tdbs_chunk)
    if nice_name:
        prop.name = nice_name

    tdb4_chunk = find_by_type(
        chunks=tdbs_child_chunks,
        chunk_type="tdb4"
    )
    tdb4_data = tdb4_chunk.data
    prop.is_spatial = tdb4_data.is_spatial
    prop.expression_enabled = tdb4_data.expression_enabled
    # TODO make better use of this data, then remove it from property class
    prop.animated = tdb4_data.animated
    prop.dimensions = tdb4_data.dimensions
    prop.integer = tdb4_data.integer
    prop.vector = tdb4_data.vector
    prop.no_value = tdb4_data.no_value
    prop.color = tdb4_data.color

    # This needs some work
    if prop.property_control_type == Aep.PropertyControlType.unknown:
        if prop.no_value:
            # TODO could be shapes, gradient, ...
            prop.property_value_type = Aep.PropertyValueType.no_value
        if prop.color:
            prop.property_control_type = Aep.PropertyControlType.color
            prop.property_value_type = Aep.PropertyValueType.color
        elif prop.integer:
            prop.property_control_type = Aep.PropertyControlType.boolean
            prop.property_value_type = Aep.PropertyValueType.one_d
        elif prop.vector:
            if prop.dimensions == 1:
                prop.property_control_type = Aep.PropertyControlType.scalar  # not sure, could be slider
                prop.property_control_type = Aep.PropertyValueType.one_d  # not sure
            elif prop.dimensions == 2:
                prop.property_control_type = Aep.PropertyControlType.two_d
                if prop.is_spatial:
                    prop.property_value_type = Aep.PropertyValueType.two_d_spatial
                else:
                    prop.property_value_type = Aep.PropertyValueType.two_d
            elif prop.dimensions == 3:
                prop.property_control_type = Aep.PropertyControlType.three_d
                if prop.is_spatial:
                    prop.property_value_type = Aep.PropertyValueType.three_d_spatial
                else:
                    prop.property_value_type = Aep.PropertyValueType.three_d
    if prop.property_control_type == Aep.PropertyControlType.unknown:
        print (
            "Could not determine type for property {match_name}" 
            " | nice_name: {nice_name}"
            " | dimensions: {dimensions}"
            " | animated: {animated}"
            " | integer: {integer}"
            " | is_spatial: {is_spatial}"
            " | vector: {vector}"
            " | static: {static}"
            " | no_value: {no_value}"
            " | color: {color}"
            .format(
                match_name=match_name,
                nice_name=nice_name,
                dimensions=prop.dimensions,
                animated=prop.animated,
                integer=prop.integer,
                is_spatial=prop.is_spatial,
                vector=prop.vector,
                static=prop.static,
                no_value=prop.no_value,
                color=prop.color,
            )
        )

    # Get property value
    cdat_chunk = find_by_type(
        chunks=tdbs_child_chunks,
        chunk_type="cdat"
    )
    if cdat_chunk is not None:
        cdat_data = cdat_chunk.data
        prop.value = cdat_data.value[:prop.dimensions]

    # Get property expression
    utf8_chunk = find_by_type(
        chunks=tdbs_child_chunks,
        chunk_type="Utf8"
    )
    if utf8_chunk is not None:
        prop.expression = str_contents(utf8_chunk).splitlines()

    # Get property keyframes
    list_chunk = find_by_list_type(
        chunks=tdbs_child_chunks,
        list_type="list"
    )
    if list_chunk is not None:
        list_child_chunks = list_chunk.data.chunks
        lhd3_chunk = find_by_type(
            chunks=list_child_chunks,
            chunk_type="lhd3"
        )
        lhd3_data = lhd3_chunk.data
        nb_keyframes = lhd3_data.nb_keyframes
        len_keyframe = lhd3_data.len_keyframe
        keyframes_type = lhd3_data.keyframes_type
        if keyframes_type == Aep.PropertyValueType.three_d and prop.is_spatial:
            keyframes_type = Aep.PropertyValueType.three_d_spatial
        if nb_keyframes:
            ldat_chunk = find_by_type(
                chunks=list_child_chunks,
                chunk_type="ldat"
            )
            ldat_data = ldat_chunk.data.keyframes
            for keyframe_data in split_in_chunks(ldat_data, len_keyframe):
                kf_chunk = Aep.Keyframe(
                    key_type=keyframes_type,
                    _io=KaitaiStream(BytesIO(keyframe_data)),
                )
                keyframe = Keyframe(
                    frame_time=int(round(kf_chunk.time_raw / time_scale)),
                    keyframe_interpolation_type=kf_chunk.keyframe_interpolation_type,
                    label=kf_chunk.label,
                    continuous_bezier=kf_chunk.continuous_bezier,
                    auto_bezier=kf_chunk.auto_bezier,
                    roving_across_time=kf_chunk.roving_across_time,
                )
                # TODO implement extra data for each type of keyframe
                # kf_data = kf_chunk.kf_data
                prop.keyframes.append(keyframe)

    return prop


def parse_effect(sspc_chunk, group_match_name, time_scale):
    """
    Args:
        sspc_chunk (Aep.Chunk): The SSPC chunk to parse.
        group_match_name (str): A special name for the property used to build unique
                                naming paths. The match name is not displayed, but you
                                can refer to it in scripts. Every property has a unique
                                match-name identifier. Match names are stable from
                                version to version regardless of the display name (the
                                name attribute value) or any changes to the application.
                                Unlike the display name, it is not localized. An indexed
                                group (PropertyBase.propertyType ==
                                Aep.PropertyType.indexed_group) may not have a name
                                value, but always has a match_name value.
        time_scale (float): The time scale of the parent composition, used as a divisor
                            for some frame values.
    Returns:
        PropertyGroup: The parsed effect.
    """
    sspc_child_chunks = sspc_chunk.data.chunks
    fnam_chunk = find_by_type(
        chunks=sspc_child_chunks,
        chunk_type="fnam"
    )
    utf8_chunk = fnam_chunk.data.chunk
    nice_name = str_contents(utf8_chunk)

    effect = PropertyGroup(
        match_name=group_match_name,
        name=nice_name,
        is_effect=True,
    )

    part_chunk = find_by_list_type(
        chunks=sspc_child_chunks,
        list_type="parT"
    )
    if part_chunk:
        # Get effect parameters
        chunks_by_parameter = get_chunks_by_match_name(part_chunk)
        for index, (match_name, parameter_chunks) in enumerate(chunks_by_parameter.items()):
            # Skip first, it describes parent
            if index == 0:
                continue
            parameter = parse_effect_parameter(
                parameter_chunks=parameter_chunks,
                match_name=match_name,
                time_scale=time_scale,
            )
            effect.properties.append(parameter)

    tdgp_chunk = find_by_list_type(
        chunks=sspc_child_chunks,
        list_type="tdgp"
    )
    nice_name = _get_nice_name(tdgp_chunk)
    if nice_name:
        effect.name = nice_name

    # Get parameters values
    chunks_by_property = get_chunks_by_match_name(tdgp_chunk)
    for (match_name, prop_chunks) in chunks_by_property.items():
        first_chunk = prop_chunks[0]
        if first_chunk.data.list_type == "tdbs":
            for parameter in effect.properties:
                if parameter.match_name == match_name:
                    # add value
                    parameter = parse_property(
                        tdbs_chunk=first_chunk,
                        match_name=match_name,
                        time_scale=time_scale,
                        prop=parameter,
                    )
                    break
        elif first_chunk.data.list_type == "tdgp":
            # TODO implement this.
            # Encountered with "ADBE FreePin3" effect (Obsolete > Puppet)
            pass
        else:
            raise NotImplementedError(
                "Cannot parse parameter value : {}".format(
                    first_chunk.data.list_type
                )
            )

    return effect


def parse_effect_parameter(parameter_chunks, match_name, time_scale):
    """
    Args:
        parameter_chunks (list[Aep.Chunk]): The parameter's chunks.
        match_name (str): A special name for the property used to build unique naming
                          paths. The match name is not displayed, but you can refer to
                          it in scripts. Every property has a unique match-name
                          identifier. Match names are stable from version to version
                          regardless of the display name (the name attribute value) or
                          any changes to the application. Unlike the display name, it is
                          not localized.
        time_scale (float): The time scale of the parent composition, used as a divisor
                            for some frame values.
    Returns:
        Property: The parsed effect parameter.
    """
    pard_chunk = find_by_type(
        chunks=parameter_chunks,
        chunk_type="pard"
    )
    pard_data = pard_chunk.data

    parameter = Property(
        match_name=match_name,
        name=pard_data.name,
        property_control_type=pard_data.property_control_type,
    )

    if parameter.property_control_type == Aep.PropertyControlType.angle:
        parameter.last_value = pard_data.last_value
        parameter.property_value_type = Aep.PropertyValueType.orientation

    elif parameter.property_control_type == Aep.PropertyControlType.boolean:
        parameter.last_value = pard_data.last_value
        parameter.default_value = pard_data.default

    elif parameter.property_control_type == Aep.PropertyControlType.color:
        parameter.last_value = pard_data.last_color
        parameter.default_value = pard_data.default_color
        parameter.max_value = pard_data.max_color
        parameter.property_value_type = Aep.PropertyValueType.color

    elif parameter.property_control_type == Aep.PropertyControlType.enum:
        parameter.last_value = pard_data.last_value
        parameter.nb_options = pard_data.nb_options
        parameter.default_value = pard_data.default

    elif parameter.property_control_type == Aep.PropertyControlType.scalar:
        parameter.last_value = pard_data.last_value
        parameter.min_value = pard_data.min_value
        parameter.max_value = pard_data.max_value

    elif parameter.property_control_type == Aep.PropertyControlType.slider:
        parameter.last_value = pard_data.last_value
        parameter.max_value = pard_data.max_value

    elif parameter.property_control_type == Aep.PropertyControlType.three_d:
        parameter.last_value = [
            pard_data.last_value_x,
            pard_data.last_value_y,
            pard_data.last_value_z
        ]

    elif parameter.property_control_type == Aep.PropertyControlType.two_d:
        parameter.last_value = [
            pard_data.last_value_x,
            pard_data.last_value_y
        ]

    pdnm_chunk = find_by_type(
        chunks=parameter_chunks,
        chunk_type="pdnm"
    )
    if pdnm_chunk is not None:
        utf8_chunk = pdnm_chunk.data.chunk
        pdnm_data = str_contents(utf8_chunk)
        if parameter.property_control_type == Aep.PropertyControlType.enum:
            parameter.property_parameters = pdnm_data.split("|")
        elif pdnm_data:
            parameter.name = pdnm_data

    return parameter


def parse_markers(mrst_chunk, group_match_name, time_scale):
    """
    Args:
        mrst_chunk (Aep.Chunk): The MRST chunk to parse.
        group_match_name (str): A special name for the property used to build unique
                                naming paths. The match name is not displayed, but you
                                can refer to it in scripts. Every property has a unique
                                match-name identifier. Match names are stable from
                                version to version regardless of the display name (the
                                name attribute value) or any changes to the application.
                                Unlike the display name, it is not localized.
        time_scale (float): The time scale of the parent composition, used as a divisor
                            for some frame values.
    """
    tdbs_chunk = find_by_list_type(
        chunks=mrst_chunk.data.chunks,
        list_type="tdbs"
    )
    # get keyframes (markers time)
    marker_group = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=group_match_name,
        time_scale=time_scale,
    )
    mrky_chunk = find_by_list_type(
        chunks=mrst_chunk.data.chunks,
        list_type="mrky"
    )
    # Get each marker
    nmrd_chunks = filter_by_list_type(
        chunks=mrky_chunk.data.chunks,
        list_type="Nmrd"
    )
    markers = []
    for i, nmrd_chunk in enumerate(nmrd_chunks):
        marker = parse_marker(
            nmrd_chunk=nmrd_chunk
        )
        marker.frame_time = marker_group.keyframes[i].frame_time
        markers.append(marker)
    return markers


def parse_marker(nmrd_chunk):
    """
    Args:
        nmrd_chunk (Aep.Chunk): The NMRD chunk to parse.
    Returns:
        Marker: The parsed marker.
    """
    nmhd_chunk = find_by_type(
        chunks=nmrd_chunk.data.chunks,
        chunk_type="NmHd"
    )
    nmhd_data = nmhd_chunk.data
    utf8_chunks = filter_by_type(
        chunks=nmrd_chunk.data.chunks,
        chunk_type="Utf8"
    )
    marker = Marker(
        chapter=str_contents(utf8_chunks[1]),
        comment=str_contents(utf8_chunks[0]),
        cue_point_name=str_contents(utf8_chunks[4]),
        duration=None,
        navigation=nmhd_data.navigation,
        frame_target=str_contents(utf8_chunks[3]),
        url=str_contents(utf8_chunks[2]),
        label=nmhd_data.label,
        protected_region=nmhd_data.protected_region,
        params=dict(),
        frame_duration=nmhd_data.frame_duration,
    )
    for (param_name, param_value) in split_in_chunks(utf8_chunks[5:], 2):
        marker.params[str_contents(param_name)] = str_contents(param_value)

    return marker


def _get_nice_name(root_chunk):
    """
    Args:
        root_chunk (Aep.Chunk): The LIST chunk to parse.
    Returns:
        str: The user defined name of the property if there is one, else None.
    """
    # Look for a tdsn which specifies the user-defined name of the property
    tdsn_chunk = find_by_type(
        chunks=root_chunk.data.chunks,
        chunk_type="tdsn"
    )
    utf8_chunk = tdsn_chunk.data.chunk
    nice_name = str_contents(utf8_chunk)

    # Check if there is a custom user defined name added.
    # The default if there is not is "-_0_/-".
    if nice_name != "-_0_/-":
        return nice_name
    return None
