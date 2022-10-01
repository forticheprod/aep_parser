from enum import Enum


class LayerSamplingMode(Enum):
    """
    Sampling mode of a layer (eg: Bilinear, Bicubic)
    """
    LAYER_SAMPLING_MODE_BILINEAR = 0x00  # Bilinear Sampling
    LAYER_SAMPLING_MODE_BICUBIC = 0x01  # Bicubic Sampling
