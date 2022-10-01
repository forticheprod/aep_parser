from enum import Enum


class Depth(Enum):
    """
    Denotes the type of footage of an AVItem (eg: Solid, Placeholder, ...)
    """
    BPC_8 = 0x00
    BPC_16 = 0x01
    BPC_32 = 0x02
