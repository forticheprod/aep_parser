from __future__ import (
    absolute_import,
    unicode_literals,
    division
)

import io
import collections

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


MATCH_NAME_TO_DISPLAY_NAME = {
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


def parse_property_group(tdgp_chunk, group_match_name, time_scale, parent_property):
    prop_name = MATCH_NAME_TO_DISPLAY_NAME.get(group_match_name, group_match_name)

    prop_group = PropertyGroup(
        enabled=True,
        is_effect=False,
        match_name=group_match_name,
        name=prop_name,
        parent_property=parent_property,
        property_type=Aep.PropertyType.indexed_group,
        properties=[]
    )

    chunks_by_sub_prop = get_chunks_by_match_name(tdgp_chunk)
    for (match_name, sub_prop_chunks) in chunks_by_sub_prop.items():
        first_chunk = sub_prop_chunks[0]
        if first_chunk.data.list_type == "tdgp":
            sub_prop = parse_property_group(
                tdgp_chunk=first_chunk,
                group_match_name=match_name,
                time_scale=time_scale,
                parent_property=prop_group,
            )
        elif first_chunk.data.list_type == "sspc":
            sub_prop = parse_effect(
                sspc_chunk=first_chunk,
                group_match_name=match_name,
                time_scale=time_scale,
                parent_property=prop_group,
            )
        elif first_chunk.data.list_type == "tdbs":
            sub_prop = parse_property(
                tdbs_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                prop=None,
            )
        elif first_chunk.data.list_type == "otst":
            sub_prop = parse_orientation(
                otst_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                prop=None,
            )
        elif first_chunk.data.list_type == "btds":
            sub_prop = parse_text_document(
                btds_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                prop=None,
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


def parse_orientation(otst_chunk, match_name, time_scale, prop=None):
    tdbs_chunk = find_by_list_type(
        chunks=otst_chunk.data.chunks,
        list_type="tdbs"
    )
    prop = Property(
        property_control_type=Aep.PropertyControlType.angle,
        match_name=match_name,
        name=match_name,
        property_parameters=[],
        keyframes=dict(),
    )
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
        prop=prop,
    )

    otky_chunk = find_by_list_type(
        chunks=otst_chunk.data.chunks,
        list_type="otky"
    )
    otda_chunks = filter_by_type(
        chunks=otky_chunk.data.chunks,
        chunk_type="otda"
    )
    # TODO parse otda_chunks
    return prop


def parse_text_document(btds_chunk, match_name, time_scale, prop=None):
    tdbs_chunk = find_by_list_type(
        chunks=btds_chunk.data.chunks,
        list_type="tdbs"
    )
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
        prop=None,
    )

    btdk_chunk = find_by_list_type(
        chunks=btds_chunk.data.chunks,
        list_type="btdk"
    )
    data_stream = io.BytesIO(btdk_chunk.data.binary_data)
    parser = CosParser(data_stream, len(btdk_chunk.data.binary_data))
    content_as_dict = parser.parse()
    # TODO get rid of "\ufeff" in string values
    # TODO convert resulting dict into readable data
    return prop


def parse_property(tdbs_chunk, match_name, time_scale, prop=None):
    if prop is None:
        prop = Property(
            property_control_type=Aep.PropertyControlType.unknown,
            match_name=match_name,
            name=match_name,
            property_parameters=[],
            keyframes=dict(),
        )

    tdbs_child_chunks = tdbs_chunk.data.chunks

    tdsb_chunk = find_by_type(
        chunks=tdbs_child_chunks,
        chunk_type="tdsb"
    )
    tdsb_data = tdsb_chunk.data
    prop.locked_ratio = tdsb_data.locked_ratio
    prop.visible = tdsb_data.visible
    prop.split_position = tdsb_data.split_position

    user_defined_name = get_user_defined_name(tdbs_chunk)
    if user_defined_name:
        prop.user_defined_name = user_defined_name

    tdb4_chunk = find_by_type(
        chunks=tdbs_child_chunks,
        chunk_type="tdb4"
    )
    tdb4_data = tdb4_chunk.data
    prop.components = tdb4_data.components
    prop.animated = tdb4_data.animated
    prop.integer = tdb4_data.integer
    prop.position = tdb4_data.position
    prop.vector = tdb4_data.vector
    prop.static = tdb4_data.static
    prop.no_value = tdb4_data.no_value
    prop.color = tdb4_data.color

    if prop.property_control_type == Aep.PropertyControlType.unknown:
        if prop.color:
            prop.property_control_type = Aep.PropertyControlType.color
        elif prop.integer:
            prop.property_control_type = Aep.PropertyControlType.boolean
        elif prop.vector:
            if prop.components == 1:
                if prop.no_value:
                    # TODO could be shapes, gradient, ...
                    pass
                else:
                    prop.property_control_type = Aep.PropertyControlType.scalar  # not sure, could be slider
            elif prop.components == 2:
                prop.property_control_type = Aep.PropertyControlType.two_d
            elif prop.components == 3:
                prop.property_control_type = Aep.PropertyControlType.three_d
            else:
                print (
                    "Could not determine type for property {match_name}" 
                    " | user_defined_name: {user_defined_name}"
                    " | components: {components}"
                    " | animated: {animated}"
                    " | integer: {integer}"
                    " | position: {position}"
                    " | vector: {vector}"
                    " | static: {static}"
                    " | no_value: {no_value}"
                    " | color: {color}"
                    .format(
                        match_name=match_name,
                        user_defined_name=user_defined_name,
                        components=prop.components,
                        animated=prop.animated,
                        integer=prop.integer,
                        position=prop.position,
                        vector=prop.vector,
                        static=prop.static,
                        no_value=prop.no_value,
                        color=prop.color,
                    )
                )
        else:
            print (
                "Could not determine type for property {match_name}" 
                " | user_defined_name: {user_defined_name}"
                " | components: {components}"
                " | animated: {animated}"
                " | integer: {integer}"
                " | position: {position}"
                " | vector: {vector}"
                " | static: {static}"
                " | no_value: {no_value}"
                " | color: {color}"
                .format(
                    match_name=match_name,
                    user_defined_name=user_defined_name,
                    components=prop.components,
                    animated=prop.animated,
                    integer=prop.integer,
                    position=prop.position,
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
        prop.value = cdat_data.value[:prop.components]

    # Get property expression
    utf8_chunk = find_by_type(
        chunks=tdbs_child_chunks,
        chunk_type="Utf8"
    )
    if utf8_chunk is not None:
        prop.expression = str_contents(utf8_chunk)

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
        if nb_keyframes:
            ldat_chunk = find_by_type(
                chunks=list_child_chunks,
                chunk_type="ldat"
            )
            ldat_data = ldat_chunk.data.keyframes
            for index, keyframe_data in enumerate(chunks(ldat_data, len_keyframe), 1):
                kf_chunk = Aep.Keyframe(
                    key_type=keyframes_type,
                    _io=KaitaiStream(BytesIO(keyframe_data)),
                )
                keyframe = Keyframe(
                    index=index,
                    time=kf_chunk.time_raw / time_scale,
                    ease_mode=kf_chunk.ease_mode,
                    label=kf_chunk.label,
                    continuous_bezier=kf_chunk.continuous_bezier,
                    auto_bezier=kf_chunk.auto_bezier,
                    roving_across_time=kf_chunk.roving_across_time,
                )
                # TODO implement extra data for each type of keyframe
                # kf_data = kf_chunk.kf_data
                prop.keyframes[index] = keyframe

    return prop


def parse_effect(sspc_chunk, group_match_name, time_scale, parent_property):
    sspc_child_chunks = sspc_chunk.data.chunks
    fnam_chunk = find_by_type(
        chunks=sspc_child_chunks,
        chunk_type="fnam"
    )
    utf8_chunk = fnam_chunk.data.chunk

    effect = PropertyGroup(
        enabled=True,
        is_effect=False,
        match_name=group_match_name,
        name=str_contents(utf8_chunk),
        parent_property=parent_property,
        property_type=Aep.PropertyType.indexed_group,
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
            parameter.index = index
            effect.parameters.append(parameter)

    tdgp_chunk = find_by_list_type(
        chunks=sspc_child_chunks,
        list_type="tdgp"
    )
    user_defined_name = get_user_defined_name(tdgp_chunk)
    if user_defined_name:
        effect.user_defined_name = user_defined_name

    # Get parameters values
    chunks_by_property = get_chunks_by_match_name(tdgp_chunk)
    for (match_name, prop_chunks) in chunks_by_property.items():
        first_chunk = prop_chunks[0]
        if first_chunk.data.list_type == "tdbs":
            for parameter in effect.parameters:
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
    pard_chunk = find_by_type(
        chunks=parameter_chunks,
        chunk_type="pard"
    )
    pard_data = pard_chunk.data

    parameter = Property(
        match_name=match_name,
        name=pard_data.name.rstrip("\x00"),
        property_control_type=pard_data.property_control_type,
        property_parameters=[],
        keyframes=dict(),
    )

    if parameter.property_control_type == Aep.PropertyControlType.angle:
        parameter.last_value = pard_data.last_value

    elif parameter.property_control_type == Aep.PropertyControlType.boolean:
        parameter.last_value = pard_data.last_value
        parameter.default = pard_data.default

    elif parameter.property_control_type == Aep.PropertyControlType.color:
        parameter.last_color = pard_data.last_color
        parameter.default_color = pard_data.default_color
        parameter.max_color = pard_data.max_color

    elif parameter.property_control_type == Aep.PropertyControlType.enum:
        parameter.last_value = pard_data.last_value
        parameter.nb_options = pard_data.nb_options
        parameter.default = pard_data.default

    elif parameter.property_control_type == Aep.PropertyControlType.scalar:
        parameter.last_value = pard_data.last_value
        parameter.min_value = pard_data.min_value
        parameter.max_value = pard_data.max_value

    elif parameter.property_control_type == Aep.PropertyControlType.slider:
        parameter.last_value = pard_data.last_value
        parameter.max_value = pard_data.max_value

    elif parameter.property_control_type == Aep.PropertyControlType.three_d:
        parameter.last_value_x_raw = pard_data.last_value_x_raw
        parameter.last_value_y_raw = pard_data.last_value_y_raw
        parameter.last_value_z_raw = pard_data.last_value_z_raw
        parameter.last_value_x = pard_data.last_value_x
        parameter.last_value_y = pard_data.last_value_y
        parameter.last_value_z = pard_data.last_value_z

    elif parameter.property_control_type == Aep.PropertyControlType.two_d:
        parameter.last_value_x_raw = pard_data.last_value_x_raw
        parameter.last_value_y_raw = pard_data.last_value_y_raw
        parameter.last_value_x = pard_data.last_value_x
        parameter.last_value_y = pard_data.last_value_y

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
    tdbs_chunk = find_by_list_type(
        chunks=mrst_chunk.data.chunks,
        list_type="tdbs"
    )
    # get keyframes (markers time)
    marker_group = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=group_match_name,
        time_scale=time_scale,
        prop=None,
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
    marker_group.markers = []
    for index, nmrd_chunk in enumerate(nmrd_chunks, 1):
        marker = parse_marker(
            nmrd_chunk=nmrd_chunk
        )
        marker.time = marker_group.keyframes[index].time
        marker_group.markers.append(marker)
    return marker_group


def parse_marker(nmrd_chunk):
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
    for (param_name, param_value) in chunks(utf8_chunks[5:], 2):
        marker.params[str_contents(param_name)] = str_contents(param_value)

    return marker


def get_chunks_by_match_name(root_chunk):
    """
    Returns a dictionary of chunks, grouped by their match name.
    Args:
        root_chunk (Aep.Chunk): The LIST chunk to parse.
    Returns:
        dict: The chunks, grouped by their match name.
    """
    SKIP_CHUNK_TYPES = (
        "engv",
        "aRbs",
    )
    properties = collections.OrderedDict()
    if root_chunk:
        skip_to_next_tdmn_flag = True
        for chunk in root_chunk.data.chunks:
            if chunk.chunk_type == "tdmn":
                match_name = str_contents(chunk)
                if match_name in ("ADBE Group End", "ADBE Effect Built In Params"):
                    skip_to_next_tdmn_flag = True
                else:
                    skip_to_next_tdmn_flag = False
            elif (not skip_to_next_tdmn_flag) and chunk.chunk_type not in SKIP_CHUNK_TYPES:
                properties.setdefault(match_name, []).append(chunk)
    return properties


def get_user_defined_name(root_chunk):
    """
    Returns the user defined name of a property.
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
    user_defined_name = str_contents(utf8_chunk)

    # Check if there is a custom user defined name added.
    # The default if there is not is "-_0_/-".
    if user_defined_name != "-_0_/-":
        return user_defined_name
    return None


def chunks(iterable, n):
    """
    Yield successive n-sized chunks from lst.
    Args:
        iterable (list): The list to chunk.
        n (int): The size of the chunks.
    Returns:
        list: The chunks.
    """
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]
