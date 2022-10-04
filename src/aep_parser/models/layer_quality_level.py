from enum import Enum


class LayerQualityLevel(Enum):
    """
    Quality level of a layer (eg: Best, Draft, Wireframe)
    """
    BEST = 0x0002  # Best Quality
    DRAFT = 0x0001  # Draft Quality
    WIREFRAME = 0x0000  # Wireframe Quality
