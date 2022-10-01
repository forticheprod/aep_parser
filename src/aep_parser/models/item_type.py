from enum import Enum


class ItemType(Enum):
    """
    Denotes the type of item. See: http://docs.aenhancers.com/items/item/#item-item_type
    """
    ITEM_TYPE_FOLDER = "Folder"  # Folder item which may contain additional items
    ITEM_TYPE_COMPOSITION = "Composition"  # Composition item which has a dimension, length, framerate and child layers
    ITEM_TYPE_FOOTAGE = "Footage"  # AVItem that has a source (eg: an image or video file)


class ItemTypeName(Enum):
    """
    Denotes the type of item. See: http://docs.aenhancers.com/items/item/#item-item_type
    """
    ITEM_TYPE_FOLDER = 0x01  # Folder item which may contain additional items
    ITEM_TYPE_COMPOSITION = 0x04  # Composition item which has a dimension, length, framerate and child layers
    ITEM_TYPE_FOOTAGE = 0x07  # AVItem that has a source (eg: an image or video file)
