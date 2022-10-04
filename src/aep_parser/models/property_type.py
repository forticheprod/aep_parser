from enum import Enum


class PropertyType(Enum):
    """
    value/type of a property
    """
    BOOLEAN = 0x04  # boolean checkbox property
    ONE_D = 0x02  # one-dimensional slider property
    TWO_D = 0x06  # two-dimensional point property
    THREE_D = 0x12  # three-dimensional point property
    COLOR = 0x05  # four-dimensional color property
    ANGLE = 0x03  # one-dimensional angle property
    LAYER_SELECT = 0x00  # single-valued layer selection property
    SELECT = 0x07  # single-valued selection property
    GROUP = 0x0d  # collection/group property
    CUSTOM = 0x0f  # unknown/custom property type (default)
