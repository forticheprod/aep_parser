from __future__ import absolute_import
from __future__ import unicode_literals

from aep_parser.kaitai.aep import Aep
from aep_parser.models.property import Property
from aep_parser.models.property_type import PropertyType
from aep_parser.rifx.utils import (
    filter_by_identifier,
    find_by_identifier,
    find_by_type,
    str_contents,
)


def parse_property(property_block, match_name):
    prop = Property(
        property_type=PropertyType.CUSTOM,
        match_name=match_name,
        name=match_name,
    )

    if match_name == "ADBE Effect Parade":
        prop.name = "Effects"

    # Handle different types of property data
    if property_block.block_type == Aep.ChunkType.lst:
        # Parse sub-properties
        tdgp_map, ordered_match_names = indexed_group_to_map(property_block)
        for i, mn in enumerate(ordered_match_names, start=1):
            sub_prop = parse_property(tdgp_map[mn], mn)
            if sub_prop is not None:
                sub_prop.index = i
                prop.properties.append(sub_prop)

        # Parse effect sub-properties
        if property_block.identifier == "sspc":
            prop.property_type = PropertyType.GROUP
            fnam_block = find_by_type(
                property_block.data.blocks.blocks,
                Aep.ChunkType.fnam
            )
            if fnam_block is not None:
                prop.name = str_contents(fnam_block)  # FIXME
            tdgp_block = find_by_identifier(
                property_block.data.blocks.blocks,
                "tdgp"
            )
            if tdgp_block is not None:
                # Look for a tdsn which specifies the user-defined label of the property
                tdsn_block = find_by_type(
                    tdgp_block.data.blocks.blocks,
                    Aep.ChunkType.tdsn
                )
                if tdsn_block is not None:
                    label = str_contents(tdsn_block)  # FIXME

                    # Check if there is a custom user defined label added. The default if there
                    # is not is "-_0_/-" for some unknown reason.
                    if label != "-_0_/-":
                        prop.label = label
            par_t_blocks = filter_by_identifier(
                property_block.data.blocks.blocks,
                "parT"
            )
            sub_prop_match_names, sub_prop_pards = pair_match_names(par_t_blocks)
            for i, mn in enumerate(sub_prop_match_names):
                # Skip first pard entry (describes parent)
                if i == 0:
                    continue
                sub_prop = parse_property(sub_prop_pards[i], mn)
                if sub_prop is not None:
                    sub_prop.index = i
                    prop.properties.append(sub_prop)
    elif isinstance(property_block, interface):  # FIXME I don't understand this... interface ??
        for block in property_block.data.blocks.blocks:
            if block.block_type == Aep.ChunkType.pdnm:
                contents = str_contents(block)  # TODO check this
                if prop.property_type == PropertyType.SELECT:
                    prop.select_options = contents.split("|")
                elif contents:
                    prop.name = contents
            elif block.block_type == Aep.ChunkType.pard:
                prop.property_type = PropertyType(block.data.property_type)  # TODO check this
                if prop.property_type == 0x0a:  # FIXME
                    prop.property_type = PropertyType.ONE_D
                pard_name = block.data.name.rstrip("\x00")  # TODO check this
                if pard_name:
                    prop.name = pard_name

    return prop


def pair_match_names(root_block):
    match_names = []
    contents = [[]]
    if root_block is not None:
        group_id = -1
        skip_to_next_tdmn_flag = False
        for block in root_block.data.blocks.blocks:
            if block.block_type == Aep.ChunkType.tdmn:
                match_name = str_contents(block)
                if match_name in ("ADBE Group End", "ADBE Effect Built In Params"):
                    skip_to_next_tdmn_flag = True
                    continue
                match_names.append(match_name)
                skip_to_next_tdmn_flag = False
                group_id += 1
            elif group_id >= 0 and not skip_to_next_tdmn_flag:
                if group_id >= len(contents):
                    contents.append([])
                if block.block_type == Aep.ChunkType.lst:
                    contents[group_id].append(block.data)  # TODO check this
                else:
                    contents[group_id].append(block)  # TODO check this
    return match_names, contents


def indexed_group_to_map(tdgp_root_block):
    tdgp_map = dict()
    match_names, contents = pair_match_names(tdgp_root_block)
    for match_name, content in zip(match_names, contents):
        tdgp_map[match_name] = content[0]
    return tdgp_map, match_names
