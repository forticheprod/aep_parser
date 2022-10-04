from enum import Enum


class LayerSamplingMode(Enum):
    """
    Sampling mode of a layer (eg: Bilinear, Bicubic)
    """
    BILINEAR = 0x00  # Bilinear Sampling
    BICUBIC = 0x01  # Bicubic Sampling
