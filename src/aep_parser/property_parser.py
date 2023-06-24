from __future__ import absolute_import
from __future__ import unicode_literals

from aep_parser.kaitai.aep import Aep
from aep_parser.models.property import Property
from aep_parser.rifx.utils import (
    filter_by_identifier,
    find_by_identifier,
    find_by_type,
    str_contents,
)


def parse_property(property_chunk, match_name):
    prop = Property(
        property_type=Aep.PropertyType.unknown,
        match_name=match_name,
        name=match_name,
    )

    if match_name == "ADBE Effect Parade":
        prop.name = "Effects"

    property_child_chunks = property_chunk.data.chunks.chunks

    # Handle different types of property data
    if property_chunk.chunk_type == "LIST":
        # Parse sub-properties
        tdgp_map, ordered_match_names = indexed_group_to_map(property_chunk)
        for i, mn in enumerate(ordered_match_names, start=1):
            sub_prop = parse_property(tdgp_map[mn], mn)
            if sub_prop is not None:
                sub_prop.index = i
                prop.properties.append(sub_prop)

        # Parse effect sub-properties
        if property_chunk.identifier == "sspc":
            prop.property_type = Aep.PropertyType.group
            fnam_chunk = find_by_type(
                chunks=property_child_chunks,
                chunk_type="fnam"
            )
            if fnam_chunk is not None:
                prop.name = str_contents(fnam_chunk)  # FIXME
            tdgp_chunk = find_by_identifier(
                chunks=property_child_chunks,
                identifier="tdgp"
            )
            if tdgp_chunk is not None:
                # Look for a tdsn which specifies the user-defined label of the property
                tdsn_chunk = find_by_type(
                    chunks=tdgp_chunk.data.chunks.chunks,
                    chunk_type="tdsn"
                )
                if tdsn_chunk is not None:
                    label = str_contents(tdsn_chunk)  # FIXME

                    # Check if there is a custom user defined label added. The default if there
                    # is not is "-_0_/-" for some unknown reason.
                    if label != "-_0_/-":
                        prop.label = label
            part_chunks = filter_by_identifier(
                chunks=property_child_chunks,
                identifier="parT"
            )
            sub_prop_match_names, sub_prop_pards = pair_match_names(part_chunks)
            for i, mn in enumerate(sub_prop_match_names):
                # Skip first pard entry (describes parent)
                if i == 0:
                    continue
                sub_prop = parse_property(sub_prop_pards[i], mn)
                if sub_prop is not None:
                    sub_prop.index = i
                    prop.properties.append(sub_prop)
    elif isinstance(property_chunk, interface):  # FIXME I don't understand this... interface ??
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


def pair_match_names(root_chunk):
    match_names = []
    contents = [[]]
    if root_chunk is not None:
        group_id = -1
        skip_to_next_tdmn_flag = False
        for chunk in root_chunk.data.chunks.chunks:
            if chunk.chunk_type == "tdmn":
                match_name = str_contents(chunk)
                if match_name in ("ADBE Group End", "ADBE Effect Built In Params"):
                    skip_to_next_tdmn_flag = True
                    continue
                match_names.append(match_name)
                skip_to_next_tdmn_flag = False
                group_id += 1
            elif group_id >= 0 and not skip_to_next_tdmn_flag:
                if group_id >= len(contents):
                    contents.append([])
                if chunk.chunk_type == "LIST":
                    contents[group_id].append(chunk.data)  # TODO check this
                else:
                    contents[group_id].append(chunk)  # TODO check this
    return match_names, contents


def indexed_group_to_map(tdgp_root_chunk):
    tdgp_map = dict()
    match_names, contents = pair_match_names(tdgp_root_chunk)
    for match_name, content in zip(match_names, contents):
        tdgp_map[match_name] = content[0]
    return tdgp_map, match_names
