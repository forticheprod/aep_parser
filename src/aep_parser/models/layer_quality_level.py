from enum import Enum


class LayerQualityLevel(Enum):
    """
    Quality level of a layer (eg: Best, Draft, Wireframe)
    """
    LAYER_QUALITY_BEST = 0x0002  # Best Quality
    LAYER_QUALITY_DRAFT = 0x0001  # Draft Quality
    LAYER_QUALITY_WIREFRAME = 0x0000  # Wireframe Quality
