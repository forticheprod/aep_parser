from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from aep_parser.kaitai.aep import Aep
from aep_parser.layer_parser import parse_layer
from aep_parser.models.item import Item
from aep_parser.rifx.utils import (
    find_by_type,
    sublist_find_by_type,
    sublist_filter_by_identifier,
)


def parse_item(item_block, project):
    item = Item()
    print('item_block.data.identifier: ', item_block.data.identifier)
    is_root = item_block.data.identifier == "Fold"

    # Parse item metadata
    if is_root:
        item.item_id = 0
        item.name = "root"
        item.item_type = Aep.ItemType.folder
    else:
        name_block = sublist_find_by_type([item_block], Aep.ChunkType.utf8)
        if name_block is None:
            # TODO add warning
            return
        item.name = name_block.data.data

        idta_block = sublist_find_by_type([item_block], Aep.ChunkType.idta)
        if idta_block is None:
            # TODO add warning
            return

        item.item_id = idta_block.data.item_id
        item.item_type = Aep.ItemType(idta_block.data.item_type)

    # Parse unique item type information
    if item.item_type == Aep.ItemType.folder:
        child_item_list_blocks = sublist_filter_by_identifier(
            [item_block] + sublist_filter_by_identifier([item_block], "Sfdr"),
            "Item"
        )
        for child_item_list_block in child_item_list_blocks:
            child_item = parse_item(child_item_list_block, project)
            if child_item is None:
                # TODO add warning
                continue

            item.folder_contents.append(child_item)

    elif item.item_type == Aep.ItemType.footage:
        pin_blocks = sublist_filter_by_identifier([item_block], "Pin ")
        if not pin_blocks:
            # TODO add warning
            return

        sspc_block = sublist_filter_by_type(pin_blocks, "sspc")
        if sspc_block is None:
            # TODO add warning
            return
        sspec_data = sspc_block.data

        item.footage_dimensions = [sspec_data.width, sspec_data.height]
        item.footage_framerate = sspec_data.Framerate + sspec_data.framerate_dividend / (1 << 16)  # TODO check if float() needed
        item.footage_seconds = sspec_data.seconds_dividend / sspec_data.seconds_divisor  # TODO check if float() needed

        opti_block = find_by_type(pin_blocks, Aep.ChunkType.opti)
        if opti_block is None:
            # TODO add warning
            return

        opti_data = opti_block.data
        item.footage_type = opti_data.footage_type  # TODO check this
        item.name = opti_data.name  # TODO check this

    elif item.item_type == Aep.ItemType.composition:
        cdta_block = sublist_find_by_type([item_block], Aep.ChunkType.cdta)
        if cdta_block is None:
            # TODO add warning
            return
        cdta_data = cdta_block.data

        item.footage_dimensions = [cdta_data.width, cdta_data.height]
        item.footage_framerate = cdta_data.framerate_dividend / cdta_data.framerate_divisor
        item.footage_seconds = cdta_data.seconds_dividend / cdta_data.seconds_divisor
        item.background_color = cdta_data.background_color

        # Parse composition's layers
        layer_sub_blocks = sublist_filter_by_identifier([item_block], "Layr")
        print('layer_sub_blocks: ', layer_sub_blocks)
        for index, layer_block in enumerate(layer_sub_blocks, start=1):
            layer = parse_layer(layer_block)
            if layer is None:
                # TODO add warning
                return
            layer.index = index
            item.composition_layers.append(layer)

    project.items[item.item_id] = item

    return item
