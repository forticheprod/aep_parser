from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from aep_parser.layer_parser import parse_layer
from aep_parser.models.cdta import CDTA
from aep_parser.models.footage_type_name import FootageTypeName
from aep_parser.models.idta import IDTA
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
    is_root = item_block.identifier == "Fold"

    # Parse item metadata
    if is_root:
        item.id_ = 0
        item.name = "root"
        item.item_type = ItemTypeName.ITEM_TYPE_FOLDER
    else:
        name_block = find_by_type([item_block], "Utf8")
        if name_block is None:
            return None
        item.name = name_block  # TODO .data ? str() ?

        idta_block = item_block.FindByType("idta")
        if idta_block is None:
            return None
        item_descriptor = IDTA(
            type_=idta_block.type_,
            unknown01=idta_block.unknown01,
            id_=idta_block.id_,
        )

        item.id_ = item_descriptor.id_
        if item_descriptor.Type == ItemType.ITEM_TYPE_FOLDER:
            item.item_type = ItemTypeName.ITEM_TYPE_FOLDER
        elif item_descriptor.Type == ItemType.ITEM_TYPE_COMPOSITION:
            item.item_type = ItemTypeName.ITEM_TYPE_COMPOSITION
        elif item_descriptor.Type == ItemType.ITEM_TYPE_FOOTAGE:
            item.item_type = ItemTypeName.ITEM_TYPE_FOOTAGE

    # Parse unique item type information
    if item.item_type == ItemTypeName.ITEM_TYPE_FOLDER:
        child_item_lists = (
            sublist_filter(item_block, "Item")
            + sublist_filter(sublist_merge(item_block, "Sfdr"), "Item")
        )
        for child_item_list in child_item_lists:
            child_item = parse_item(child_item_list, project)
            if child_item is None:
                return None

            item.folder_contents += child_item

    elif item.item_type == ItemTypeName.ITEM_TYPE_FOOTAGE:
        pin_list = sublist_find(item_block, "Pin ")
        if pin_list is None:
            return None

        sspcBlock = pin_list.FindByType("sspc")
        if sspcBlock is None:
            return None

        sspc_desc = SSPC(
            toto=sspcBlock  # TODO complete
        )
        item.footage_dimensions = [sspc_desc.Width, sspc_desc.Height]
        item.footage_framerate = sspc_desc.Framerate + sspc_desc.FramerateDividend / (1 << 16)  # TODO check if float() needed
        item.footage_seconds = sspc_desc.SecondsDividend / sspc_desc.SecondsDivisor  # TODO check if float() needed

        optiBlock = pin_list.FindByType("opti")
        if optiBlock is None:
            return None

        optiData = optiBlock.data
        item.footage_type = FootageTypeName(optiData[4:6])  # TODO check this
        if item.footage_type == FootageTypeName.FOOTAGE_TYPE_SOLID:
            item.name = optiData[26:255]  # TODO check this
        elif item.footage_type == FootageTypeName.FOOTAGE_TYPE_PLACEHOLDER:
            item.name = optiData[10:]  # TODO check this

    elif item.item_type == ItemTypeName.ITEM_TYPE_COMPOSITION:
        compDesc = CDTA()
        cdata_block = item_block.FindByType("cdta")
        if cdata_block is None:
            return None

        cdata_block.ToStruct(compDesc)
        item.footage_dimensions = [compDesc.Width, compDesc.Height]
        item.footage_framerate = compDesc.FramerateDividend / compDesc.FramerateDivisor  # TODO check if float() needed
        item.footage_seconds = compDesc.SecondsDividend / compDesc.SecondsDivisor  # TODO check if float() needed
        item.background_color = compDesc.background_color

        # Parse composition's layers
        for index, layer_list_head in enumerate(sublist_filter(item_block, "Layr")):
            layer = parse_layer(layer_list_head)
            if layer is None:
                return None
            layer.index = index + 1
            item.composition_layers.append(layer)

    # Insert item into project items map
    project.items[item.id_] = item

    return item
