from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict

from .kaitai.aep import Aep
from .models.property import Property
from .rifx.utils import (
    filter_by_identifier,
    find_by_identifier,
    find_by_type,
    str_contents,
)


def parse_property(property_chunk, match_name):
    if match_name == "ADBE Effect Parade":
        prop_name = "Effects"
    elif match_name == "ADBE Transform Group":
        prop_name = "Transform"
    else:
        prop_name = match_name

    prop = Property(
        property_type=Aep.PropertyType.unknown,
        match_name=match_name,
        name=prop_name,
        properties=[],
    )

    if property_chunk.chunk_type == "pdnm":
        property_child_chunks = property_chunk.data.chunk
    else:
        property_child_chunks = property_chunk.data.chunks

    # Handle different types of property data
    if property_chunk.chunk_type == "LIST":
        # Parse sub-properties
        tdgp_map = get_properties(property_chunk)
        for i, (mn, tdgp) in enumerate(tdgp_map.items(), 1):
            sub_prop = parse_property(tdgp, mn)
            if sub_prop is not None:
                sub_prop.index = i
                prop.properties.append(sub_prop)

        # Parse effect sub-properties
        if property_chunk.data.identifier == "sspc":
            prop.property_type = Aep.PropertyType.group
            fnam_chunk = find_by_type(
                chunks=property_child_chunks,
                chunk_type="fnam"
            )
            if fnam_chunk is not None:
                utf8_chunk = fnam_chunk.data.chunk
                prop.name = str_contents(utf8_chunk)

            tdgp_chunk = find_by_identifier(
                chunks=property_child_chunks,
                identifier="tdgp"
            )
            label = get_label(tdgp_chunk)
            if label:
                prop.label = label

            part_chunk = find_by_identifier(
                chunks=property_child_chunks,
                identifier="parT"
            )
            if part_chunk:
                # TODO sort this shit out
                sub_prop_chunks = get_properties(part_chunk)
                # for i, (mn, sub_prop_chunk) in enumerate(sub_prop_chunks.items()):
                #     # Skip first pard entry (describes parent)
                #     if i == 0:
                #         continue
                #     # Skip pdnm (Parameter control strings) as they have a different structure
                #     sub_prop = parse_property(sub_prop_chunk, mn)
                #     if sub_prop is not None:
                #         sub_prop.index = i
                #         prop.properties.append(sub_prop)
        elif property_chunk.data.identifier == "tdbs":
            tdbs_child_chunks = property_chunk.data.chunks

            tdsb_chunk = find_by_type(
                chunks=tdbs_child_chunks,
                chunk_type="tdsb"
            )
            tdsb_data = tdsb_chunk.data
            prop.locked_ratio = tdsb_data.locked_ratio
            prop.visible = tdsb_data.visible
            prop.split_position = tdsb_data.split_position

            label = get_label(property_chunk)
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
            # TODO prop.property_type ?

            cdat_chunk = find_by_type(
                chunks=tdbs_child_chunks,
                chunk_type="cdat"
            )
            if cdat_chunk is not None:
                cdat_data = cdat_chunk.data
                prop.value = cdat_data.value[:prop.components]
    else:  # TODO check all this, including this "else" condition
        for chunk in property_child_chunks:
            if chunk.chunk_type == "pdnm":
                contents = str_contents(chunk)  # TODO check this
                if prop.property_type == Aep.PropertyType.enum:
                    prop.select_options = contents.split("|")
                elif contents:
                    prop.name = contents
            elif chunk.chunk_type == "pard":
                prop.property_type = Aep.PropertyType(chunk.data.property_type)  # TODO check this
                if prop.property_type == 0x0a:  # FIXME
                    prop.property_type = Aep.PropertyType.scalar
                pard_name = chunk.data.name.rstrip("\x00")  # TODO check this
                if pard_name:
                    prop.name = pard_name

    return prop


def get_properties(root_chunk):
    properties = OrderedDict()
    match_name = None
    if root_chunk:
        skip_to_next_tdmn_flag = False
        for chunk in root_chunk.data.chunks:
            if chunk.chunk_type == "tdmn":
                match_name = str_contents(chunk)
                if match_name in ("ADBE Group End", "ADBE Effect Built In Params"):
                    skip_to_next_tdmn_flag = True
                    continue
                skip_to_next_tdmn_flag = False
            elif match_name and not skip_to_next_tdmn_flag and match_name not in properties:
                properties[match_name] = chunk
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
