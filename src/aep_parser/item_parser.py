from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from aep_parser.layer_parser import parse_layer
from aep_parser.models.cdta import CDTA
from aep_parser.models.footage_type_name import FootageTypeName
from aep_parser.models.item import Item
from aep_parser.models.item_type import (
    ItemType,
    ItemTypeName,
)
from aep_parser.models.sspc import SSPC
from aep_parser.rifx.utils import (
    find_by_type,
    sublist_filter,
    sublist_find,
    sublist_merge,
)


def parse_item(item_block, project):
    item = Item()
    is_root = item_block.data.identifier == "Fold"

    # Parse item metadata
    if is_root:
        item.id_ = 0
        item.name = "root"
        item.item_type = ItemTypeName.ITEM_TYPE_FOLDER
    else:
        name_block = find_by_type([item_block], "utf8")
        if name_block is None:
            # TODO add warning
            return None
        item.name = name_block  # TODO .data ? str() ?

        idta_block = find_by_type([item_block], "idta")
        if idta_block is None:
            # TODO add warning
            return None

        item.id_ = idta_block.id_
        if idta_block.type_ == ItemType.ITEM_TYPE_FOLDER:
            item.item_type = ItemTypeName.ITEM_TYPE_FOLDER
        elif idta_block.type_ == ItemType.ITEM_TYPE_COMPOSITION:
            item.item_type = ItemTypeName.ITEM_TYPE_COMPOSITION
        elif idta_block.type_ == ItemType.ITEM_TYPE_FOOTAGE:
            item.item_type = ItemTypeName.ITEM_TYPE_FOOTAGE

    # Parse unique item type information
    if item.item_type == ItemTypeName.ITEM_TYPE_FOLDER:
        print('sublist_filter([item_block], "Item"): ', sublist_filter([item_block], "Item"))
        print('sublist_merge([item_block], "Sfdr"): ', sublist_merge([item_block], "Sfdr"))
        child_item_lists = (
            sublist_filter([item_block], "Item")
            + sublist_filter(sublist_merge([item_block], "Sfdr"), "Item")
        )
        print('child_item_lists: ', child_item_lists)
        for child_item_list in child_item_lists:
            child_item = parse_item(child_item_list, project)
            if child_item is None:
                # TODO add warning
                continue

            item.folder_contents.append(child_item)

    elif item.item_type == ItemTypeName.ITEM_TYPE_FOOTAGE:
        pin_list = sublist_find(item_block, "Pin ")
        if pin_list is None:
            # TODO add warning
            return None

        sspc_block = find_by_type([pin_list], "sspc")
        if sspc_block is None:
            # TODO add warning
            return None

        sspc_desc = SSPC(
            unknown01=sspc_block.unknown01,
            width=sspc_block.width,
            height=sspc_block.height,
            seconds_dividend=sspc_block.seconds_dividend,
            seconds_divisor=sspc_block.seconds_divisor,
            unknown02=sspc_block.unknown02,
            framerate=sspc_block.framerate,
            framerate_dividend=sspc_block.framerate_dividend,
        )

        item.footage_dimensions = [sspc_desc.width, sspc_desc.height]
        item.footage_framerate = sspc_desc.Framerate + sspc_desc.framerate_dividend / (1 << 16)  # TODO check if float() needed
        item.footage_seconds = sspc_desc.seconds_dividend / sspc_desc.seconds_divisor  # TODO check if float() needed

        optiBlock = find_by_type([pin_list], "opti")
        if optiBlock is None:
            # TODO add warning
            return None

        optiData = optiBlock.data
        item.footage_type = FootageTypeName(optiData[4:6])  # TODO check this
        if item.footage_type == FootageTypeName.FOOTAGE_TYPE_SOLID:
            item.name = optiData[26:255]  # TODO check this
        elif item.footage_type == FootageTypeName.FOOTAGE_TYPE_PLACEHOLDER:
            item.name = optiData[10:]  # TODO check this

    elif item.item_type == ItemTypeName.ITEM_TYPE_COMPOSITION:
        cdata_block = find_by_type([item_block], "cdta")
        if cdata_block is None:
            # TODO add warning
            return None

        comp_desc = CDTA(
            unknown01=cdata_block.unknown01,
            framerate_divisor=cdata_block.framerate_divisor,
            framerate_dividend=cdata_block.framerate_dividend,
            unknown02=cdata_block.unknown02,
            seconds_dividend=cdata_block.seconds_dividend,
            seconds_divisor=cdata_block.seconds_divisor,
            background_color=cdata_block.background_color,
            unknown03=cdata_block.unknown03,
            width=cdata_block.width,
            height=cdata_block.height,
            unknown04=cdata_block.unknown04,
            framerate=cdata_block.framerate,
        )

        item.footage_dimensions = [comp_desc.width, comp_desc.height]
        item.footage_framerate = comp_desc.framerate_dividend / comp_desc.framerate_divisor  # TODO check if float() needed
        item.footage_seconds = comp_desc.seconds_dividend / comp_desc.seconds_divisor  # TODO check if float() needed
        item.background_color = comp_desc.background_color

        # Parse composition's layers
        for index, layer_list_head in enumerate(sublist_filter(item_block, "Layr")):
            layer = parse_layer(layer_list_head)
            if layer is None:
                # TODO add warning
                return None
            layer.index = index + 1
            item.composition_layers.append(layer)

    project.items[item.id_] = item

    return item
