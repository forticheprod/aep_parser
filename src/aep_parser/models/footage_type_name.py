from enum import Enum


class FootageTypeName(Enum):
    """
    Denotes the type of footage of an AVItem (eg: Solid, Placeholder, ...)
    """
    FOOTAGE_TYPE_SOLID = 0x09  # a Solid source
    FOOTAGE_TYPE_PLACEHOLDER = 0x02  # a Placeholder source
