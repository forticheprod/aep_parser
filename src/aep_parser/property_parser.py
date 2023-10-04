from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict

from .kaitai.aep import Aep
from .kaitai.utils import (
    filter_by_type,
    find_by_identifier,
    find_by_type,
    str_contents,
)
from .models.properties.property import Property


def parse_property_group(tdgp_chunk, group_match_name):
    if group_match_name == "ADBE Effect Parade":
        prop_name = "Effects"
    elif group_match_name == "ADBE Transform Group":
        prop_name = "Transform"
    else:
        prop_name = group_match_name

    prop_group = Property(
        property_type=Aep.PropertyType.group,
        match_name=group_match_name,
        name=prop_name,
        properties=[],
    )

    chunks_by_sub_prop = get_properties(tdgp_chunk)
    for i, (match_name, sub_prop_chunks) in enumerate(chunks_by_sub_prop.items(), 1):
        first_chunk = sub_prop_chunks[0]
        if first_chunk.data.identifier == "tdgp":
            sub_prop = parse_property_group(
                tdgp_chunk=first_chunk,
                group_match_name=match_name,
            )
        elif first_chunk.data.identifier == "sspc":
            sub_prop = parse_effect(
                sspc_chunk=first_chunk,
                group_match_name=match_name,
            )
        elif first_chunk.data.identifier == "tdbs":
            sub_prop = parse_property(
                tdbs_chunk=first_chunk,
                match_name=match_name,
                prop=None,
            )
        elif first_chunk.data.identifier == "otst":
            sub_prop = parse_orientation(
                otst_chunk=first_chunk,
                match_name=match_name,
                prop=None,
            )
        else:
            # TODO check how to parse om-s, GCst, mrst, btds, OvG2
            raise NotImplementedError(
                "Cannot parse property : {}".format(
                    first_chunk.data.identifier
                )
            )
        sub_prop.index = i
        prop_group.properties.append(sub_prop)

    return prop_group

def parse_orientation(otst_chunk, match_name, prop=None):
    tdbs_chunk = find_by_identifier(
        chunks=otst_chunk.data.chunks,
        identifier="tdbs"
    )
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        prop=prop,
    )

    otky_chunk = find_by_identifier(
        chunks=otst_chunk.data.chunks,
        identifier="otky"
    )
    otda_chunks = filter_by_type(
        chunks=otky_chunk.data.chunks,
        chunk_type="otda"
    )
    # TODO parse otda_chunks
    return prop

def parse_property(tdbs_chunk, match_name, prop=None):
    if prop is None:
        prop = Property(
            property_type=Aep.PropertyType.unknown,
            match_name=match_name,
            name=match_name,
            properties=[],
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
    # TODO deduce prop.property_type ?

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
    list_chunk = find_by_identifier(
        chunks=tdbs_child_chunks,
        identifier="list"
    )
    if list_chunk is not None:
        list_child_chunks = list_chunk.data.chunks
        lhd3_chunk = find_by_type(
            chunks=list_child_chunks,
            chunk_type="lhd3"
        )  # TODO number of keyframes (implement in ksy)
        ldat_chunk = find_by_type(
            chunks=list_child_chunks,
            chunk_type="ldat"
        )  # TODO Keyframe data and values (implement in ksy)

    return prop

def parse_effect(sspc_chunk, group_match_name):
    # TODO create Effect class
    effect = Property(
        property_type=Aep.PropertyType.group,
        match_name=group_match_name,
        name=group_match_name,
        properties=[],
    )

    sspc_child_chunks = sspc_chunk.data.chunks
    fnam_chunk = find_by_type(
        chunks=sspc_child_chunks,
        chunk_type="fnam"
    )
    utf8_chunk = fnam_chunk.data.chunk
    effect.name = str_contents(utf8_chunk)

    part_chunk = find_by_identifier(
        chunks=sspc_child_chunks,
        identifier="parT"
    )
    if part_chunk:
        chunks_by_parameter = get_properties(part_chunk)
        for i, (match_name, parameter_chunks) in enumerate(chunks_by_parameter.items()):
            # Skip first, it describes parent
            if i == 0:
                continue
            parameter = parse_effect_parameter(parameter_chunks, match_name)
            parameter.index = i
            effect.properties.append(parameter)

    tdgp_chunk = find_by_identifier(
        chunks=sspc_child_chunks,
        identifier="tdgp"
    )
    label = get_label(tdgp_chunk)
    if label:
        effect.label = label

    chunks_by_property = get_properties(tdgp_chunk)
    for i, (match_name, prop_chunks) in enumerate(chunks_by_property.items(), 1):
        first_chunk = prop_chunks[0]
        if first_chunk.data.identifier == "tdbs":
            for parameter in effect.properties:
                if parameter.match_name == match_name:
                    parameter = parse_property(
                        tdbs_chunk=first_chunk,
                        match_name=match_name,
                        prop=parameter,
                    )
        else:
            raise NotImplementedError(
                "Cannot parse parameter value : {}".format(
                    first_chunk.data.identifier
                )
            )

    return effect


def parse_effect_parameter(parameter_chunks, match_name):
    # TODO create Parameter class (inherits from property)
    parameter = Property(
        match_name=match_name,
        name=match_name,
        properties=[],
    )
    pard_chunk = find_by_type(
        chunks=parameter_chunks,
        chunk_type="pard"
    )
    pard_data = pard_chunk.data
    parameter.property_type = pard_data.property_type
    parameter.name = pard_data.name.rstrip("\x00")

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
        parameter.option_count = pard_data.option_count
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


def get_properties(root_chunk):
    properties = OrderedDict()
    if root_chunk:
        match_name = None
        skip_to_next_tdmn_flag = False
        for chunk in root_chunk.data.chunks:
            if chunk.chunk_type == "tdmn":
                match_name = str_contents(chunk)
                if match_name in ("ADBE Group End", "ADBE Effect Built In Params"):
                    skip_to_next_tdmn_flag = True
                else:
                    skip_to_next_tdmn_flag = False
            elif match_name and not skip_to_next_tdmn_flag:
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
