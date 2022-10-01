from enum import Enum


class PropertyType(Enum):
    """
    value/type of a property
    """
    PROPERTY_TYPE_BOOLEAN = 0x04  # boolean checkbox property
    PROPERTY_TYPE_ONE_D = 0x02  # one-dimensional slider property
    PROPERTY_TYPE_TWO_D = 0x06  # two-dimensional point property
    PROPERTY_TYPE_THREE_D = 0x12  # three-dimensional point property
    PROPERTY_TYPE_COLOR = 0x05  # four-dimensional color property
    PROPERTY_TYPE_ANGLE = 0x03  # one-dimensional angle property
    PROPERTY_TYPE_LAYER_SELECT = 0x00  # single-valued layer selection property
    PROPERTY_TYPE_SELECT = 0x07  # single-valued selection property
    PROPERTY_TYPE_GROUP = 0x0d  # collection/group property
    PROPERTY_TYPE_CUSTOM = 0x0f  # unknown/custom property type (default)


class PropertyTypeName(Enum):
    """
    value/type of a property
    """
    PROPERTY_TYPE_BOOLEAN = "Boolean"  # boolean checkbox property
    PROPERTY_TYPE_ONE_D = "OneD"  # one-dimensional slider property
    PROPERTY_TYPE_TWO_D = "TwoD"  # two-dimensional point property
    PROPERTY_TYPE_THREE_D = "ThreeD"  # three-dimensional point property
    PROPERTY_TYPE_COLOR = "Color"  # four-dimensional color property
    PROPERTY_TYPE_ANGLE = "Angle"  # one-dimensional angle property
    PROPERTY_TYPE_LAYER_SELECT = "LayerSelect"  # single-valued layer selection property
    PROPERTY_TYPE_SELECT = "Select"  # single-valued selection property
    PROPERTY_TYPE_GROUP = "Group"  # collection/group property
    PROPERTY_TYPE_CUSTOM ="Custom"  # unknown/custom property type (default)
