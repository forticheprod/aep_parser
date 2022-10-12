from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division

from aep_parser.kaitai.aep import Aep
from aep_parser.layer_parser import parse_layer
from aep_parser.models.item import Item
from aep_parser.rifx.utils import (
    find_by_type,
    filter_by_identifier,
    filter_by_type,
    str_contents,
)


def parse_item(item_block, project):
    item = Item()
    is_root = item_block.data.identifier == "Fold"

    # Parse item metadata
    if is_root:
        item.item_id = 0
        item.name = "root"
        item.item_type = Aep.ItemType.folder
    else:
        name_block = find_by_type(
            item_block.data.blocks.blocks,
            Aep.ChunkType.utf8
        )
        if name_block is None:
            # TODO add warning
            return
        item.name = str_contents(name_block)  # TODO check this

        idta_block = find_by_type(
            item_block.data.blocks.blocks,
            Aep.ChunkType.idta
        )
        if idta_block is None:
            # TODO add warning
            return

        item.item_id = idta_block.data.item_id
        item.item_type = Aep.ItemType(idta_block.data.item_type)

    # Parse unique item type information
    if item.item_type == Aep.ItemType.folder:
        child_sfdr_blocks = filter_by_identifier(
            item_block.data.blocks.blocks,
            "Sfdr"
        )
        child_item_list_blocks = filter_by_identifier(
            item_block.data.blocks.blocks + child_sfdr_blocks,
            "Item"
        )
        for child_item_list_block in child_item_list_blocks:
            child_item = parse_item(child_item_list_block, project)
            if child_item is None:
                # TODO add warning
                continue

            item.folder_contents.append(child_item)

    elif item.item_type == Aep.ItemType.footage:
        pin_block = find_by_identifier(
            item_block.data.blocks.blocks,
            "Pin "
        )
        if not pin_block:
            # TODO add warning
            return

        sspc_block = find_by_type(
            pin_block.data.blocks.blocks,
            Aep.ChunkType.sspc
        )
        if sspc_block is None:
            # TODO add warning
            return
        sspc_data = sspc_block.data

        item.footage_dimensions = [sspc_data.width, sspc_data.height]
        item.footage_framerate = float(sspc_data.framerate + sspc_data.framerate_dividend) / (1 << 16)
        item.footage_seconds = float(sspc_data.seconds_dividend) / sspc_data.seconds_divisor

        opti_block = find_by_type(
            pin_blockdata.blocks.blocks,
            Aep.ChunkType.opti
        )
        if opti_block is None:
            # TODO add warning
            return

        opti_data = opti_block.data
        item.footage_type = opti_data.footage_type  # TODO check this
        item.name = opti_data.name.rstrip("\x00")  # TODO check this

    elif item.item_type == Aep.ItemType.composition:
        cdta_block = find_by_type(
            item_block.data.blocks.blocks,
            Aep.ChunkType.cdta
        )
        if cdta_block is None:
            # TODO add warning
            return
        cdta_data = cdta_block.data

        item.footage_dimensions = [cdta_data.width, cdta_data.height]
        item.footage_framerate = cdta_data.framerate_dividend / cdta_data.framerate_divisor
        item.footage_seconds = cdta_data.seconds_dividend / cdta_data.seconds_divisor
        item.background_color = cdta_data.background_color

        # Parse composition's layers
        layer_sub_blocks = filter_by_identifier(item_block.data.blocks.blocks, "Layr")
        for index, layer_block in enumerate(layer_sub_blocks, start=1):
            layer = parse_layer(layer_block)
            if layer is None:
                # TODO add warning
                return
            layer.index = index
            item.composition_layers.append(layer)

    project.items[item.item_id] = item

    return item
