from __future__ import absolute_import
from __future__ import unicode_literals

import io
import collections

from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO

from .cos.cos import CosParser
from .kaitai.aep import Aep
from .kaitai.utils import (
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from .models.properties.effect import Effect
from .models.properties.keyframe import Keyframe
from .models.properties.marker import Marker
from .models.properties.parameter import Parameter
from .models.properties.property import Property
from .models.properties.property_group import PropertyGroup


def parse_property_group(tdgp_chunk, group_match_name, time_scale):
    if group_match_name == "ADBE Effect Parade":
        prop_name = "Effects"
    elif group_match_name == "ADBE Transform Group":
        prop_name = "Transform"
    else:
        prop_name = group_match_name

    prop_group = PropertyGroup(
        property_type=Aep.PropertyType.group,
        match_name=group_match_name,
        name=prop_name,
        properties=[],
    )

    chunks_by_sub_prop = get_properties_by_match_name(tdgp_chunk)
    for index, (match_name, sub_prop_chunks) in enumerate(chunks_by_sub_prop.items(), 1):
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
            # TODO check how to parse om-s, GCst, mrst, btds, OvG2
            raise NotImplementedError(
                "Cannot parse property : {}".format(
                    first_chunk.data.list_type
                )
            )
        sub_prop.index = index
        prop_group.properties.append(sub_prop)

    return prop_group


def parse_orientation(otst_chunk, match_name, time_scale, prop=None):
    tdbs_chunk = find_by_list_type(
        chunks=otst_chunk.data.chunks,
        list_type="tdbs"
    )
    prop = Property(
        property_type=Aep.PropertyType.angle,
        match_name=match_name,
        name=match_name,
        select_options=[],
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
            property_type=Aep.PropertyType.unknown,
            match_name=match_name,
            name=match_name,
            select_options=[],
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

    label = get_label(tdbs_chunk)
    if label:
        prop.label = label

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

    if prop.property_type == Aep.PropertyType.unknown:
        if prop.color:
            prop.property_type = Aep.PropertyType.color
        elif prop.integer:
            prop.property_type = Aep.PropertyType.boolean
        elif prop.vector:
            if prop.components == 1:
                if prop.no_value:
                    # TODO could be shapes, gradient, ...
                    pass
                else:
                    prop.property_type = Aep.PropertyType.scalar  # not sure, could be slider
            elif prop.components == 2:
                prop.property_type = Aep.PropertyType.two_d
            elif prop.components == 3:
                prop.property_type = Aep.PropertyType.three_d
            else:
                print (
                    "Could not determine type for property {match_name}" 
                    " | label: {label}"
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
                        label=label,
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
                " | label: {label}"
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
                    label=label,
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
                    label_color=kf_chunk.label_color,
                    continuous_bezier=kf_chunk.continuous_bezier,
                    auto_bezier=kf_chunk.auto_bezier,
                    roving_across_time=kf_chunk.roving_across_time,
                )
                kf_data = kf_chunk.kf_data
                # TODO implement extra data for each type of keyframe
                prop.keyframes[index] = keyframe

    return prop


def parse_effect(sspc_chunk, group_match_name, time_scale):
    sspc_child_chunks = sspc_chunk.data.chunks
    fnam_chunk = find_by_type(
        chunks=sspc_child_chunks,
        chunk_type="fnam"
    )
    utf8_chunk = fnam_chunk.data.chunk

    effect = Effect(
        match_name=group_match_name,
        name=str_contents(utf8_chunk),
        parameters=[],
    )

    part_chunk = find_by_list_type(
        chunks=sspc_child_chunks,
        list_type="parT"
    )
    if part_chunk:
        # Get effect parameters
        chunks_by_parameter = get_properties_by_match_name(part_chunk)
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
    label = get_label(tdgp_chunk)
    if label:
        effect.label = label

    # Get parameters values
    chunks_by_property = get_properties_by_match_name(tdgp_chunk)
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

    parameter = Parameter(
        match_name=match_name,
        name=pard_data.name.rstrip("\x00"),
        property_type=pard_data.property_type,
        select_options=[],
        keyframes=dict(),
    )

    if parameter.property_type == Aep.PropertyType.angle:
        parameter.last_value = pard_data.last_value

    elif parameter.property_type == Aep.PropertyType.boolean:
        parameter.last_value = pard_data.last_value
        parameter.default = pard_data.default

    elif parameter.property_type == Aep.PropertyType.color:
        parameter.last_color = pard_data.last_color
        parameter.default_color = pard_data.default_color
        parameter.max_color = pard_data.max_color

    elif parameter.property_type == Aep.PropertyType.enum:
        parameter.last_value = pard_data.last_value
        parameter.nb_options = pard_data.nb_options
        parameter.default = pard_data.default

    elif parameter.property_type == Aep.PropertyType.scalar:
        parameter.last_value = pard_data.last_value
        parameter.min_value = pard_data.min_value
        parameter.max_value = pard_data.max_value

    elif parameter.property_type == Aep.PropertyType.slider:
        parameter.last_value = pard_data.last_value
        parameter.max_value = pard_data.max_value

    elif parameter.property_type == Aep.PropertyType.three_d:
        parameter.last_value_x_raw = pard_data.last_value_x_raw
        parameter.last_value_y_raw = pard_data.last_value_y_raw
        parameter.last_value_z_raw = pard_data.last_value_z_raw
        parameter.last_value_x = pard_data.last_value_x
        parameter.last_value_y = pard_data.last_value_y
        parameter.last_value_z = pard_data.last_value_z

    elif parameter.property_type == Aep.PropertyType.two_d:
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
        if parameter.property_type == Aep.PropertyType.enum:
            parameter.select_options = pdnm_data.split("|")
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
        marker.index = index
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
        name=str_contents(utf8_chunks[0]),
        chapter=str_contents(utf8_chunks[1]),
        url=str_contents(utf8_chunks[2]),
        frame_target=str_contents(utf8_chunks[3]),
        flash_cue_point_name=str_contents(utf8_chunks[4]),
        duration_frames=nmhd_data.duration_frames,
        label_color=nmhd_data.label_color,
        protected=nmhd_data.protected,
        navigation=nmhd_data.navigation,
        flash_cue_point_parameters=dict(),
    )
    for (param_name, param_value) in chunks(utf8_chunks[5:], 2):
        marker.flash_cue_point_parameters[str_contents(param_name)] = str_contents(param_value)

    return marker

def get_properties_by_match_name(root_chunk):
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


def get_label(root_chunk):
    # Look for a tdsn which specifies the user-defined label of the property
    tdsn_chunk = find_by_type(
        chunks=root_chunk.data.chunks,
        chunk_type="tdsn"
    )
    utf8_chunk = tdsn_chunk.data.chunk
    label = str_contents(utf8_chunk)

    # Check if there is a custom user defined label added. The default if there
    # is not is "-_0_/-".
    if label != "-_0_/-":
        return label
    return None


def chunks(iterable, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]
