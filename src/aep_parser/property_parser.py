from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from aep_parser.kaitai.aep import Aep
from aep_parser.models.property import Property
from aep_parser.models.property_type import PropertyType
from aep_parser.rifx.utils import (
    find_by_type,
    sublist_filter_by_identifier,
)


def parse_property(prop_data, match_name):
    prop = Property(
        property_type=PropertyType.CUSTOM,
        match_name=match_name,
        name=match_name,
    )

    # Apply some sensible default values
    if match_name == "ADBE Effect Parade":
        prop.name = "Effects"

    # Handle different types of property data
    if isinstance(prop_data, Aep.ChunkType.lst):
        prop_head = prop_data
        # Parse sub-properties
        tdgp_map, ordered_match_names = indexed_group_to_map(prop_head)
        for i, mn in enumerate(ordered_match_names):
            sub_prop = parse_property(tdgp_map[mn], mn)
            if sub_prop is not None:
                sub_prop.index = i + 1
                prop.properties.append(sub_prop)

        # Parse effect sub-properties
        if prop_head.identifier == "sspc":
            prop.property_type = PropertyType.GROUP
            fnam_block = find_by_type(prop_head, "fnam")
            if fnam_block is not None:
                prop.name = fnam_block.ToString()
            tdgp_block = prop_head.SublistFind("tdgp")
            if tdgp_block is not None:

                # Look for a tdsn which specifies the user-defined label of the property
                tdsn_block = find_by_type(tdgp_block, "tdsn")
                if tdsn_block is not None:
                    label = tdsn_block.ToString()

                    # Check if there is a custom user defined label added. The default if there
                    # is not is "-_0_/-" for some unknown reason.
                    if label != "-_0_/-":
                        prop.label = label
            par_t_list = sublist_filter_by_identifier([prop_head], "parT")
            sub_prop_match_names, sub_prop_pards = pair_match_names(par_t_list)
            for i, mn in enumerate(sub_prop_match_names):
                # Skip first pard entry (describes parent)
                if i == 0:
                    continue
                sub_prop = parse_property(sub_prop_pards[i], mn)
                if sub_prop is not None:
                    sub_prop.index = i
                    prop.properties.append(sub_prop)
    elif isinstance(prop_data, interface):  # FIXME I don't understand this one...
        for entry in prop_data:
            block = entry.block
            if block:
                if block.block_type == "pdnm":
                    str_content = str(block.data)  # bytes.Trim(data, "\x00"))
                    if prop.property_type == PropertyType.SELECT:
                        prop.select_options = str_content.split("|")
                    elif str_content != "":
                        prop.name = str_content
                if block.block_type == "pard":
                    prop.property_type = PropertyType(int(block.data[14:16]))  # binary.BigEndian.Uint16
                    if prop.property_type == 0x0a:
                        prop.property_type = PropertyType.ONE_D
                    pard_name = block.data[16:48]  # bytes.Trim(block.data[16:48], "\x00")
                    if pard_name != "":
                        prop.name = pard_name

    return prop


def pair_match_names(head):
    match_names = []
    datum = [[]]
    if head is not None:
        group_idx = -1
        skip_to_next_tdmn_flag = False
        for block in head.blocks:
            if block.block_type == "tdmn":
                match_name = block.data  # trim(block.data, "\x00")
                if match_name in ("ADBE Group End", "ADBE Effect Built In Params"):
                    skip_to_next_tdmn_flag = True
                    continue
                match_names.append(match_name)
                skip_to_next_tdmn_flag = False
                group_idx += 1
            elif group_idx >= 0 and not skip_to_next_tdmn_flag:
                if group_idx >= len(datum):
                    datum.append([])
                if isinstance(block.data, Aep.ChunkType.lst):
                    datum[group_idx].append(block.data)
                else:
                    datum[group_idx].append(block)
    return match_names, datum


def indexed_group_to_map(tdgp_head):
    tdgp_map = dict()
    match_names, contents = pair_match_names(tdgp_head)
    for i, match_name in enumerate(match_names):
        tdgp_map[match_name] = contents[i][0]
    return tdgp_map, match_names
