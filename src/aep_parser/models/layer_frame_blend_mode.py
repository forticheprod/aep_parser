from enum import Enum


class LayerFrameBlendMode(Enum):
    """
    Frame blending mode of a layer (eg: Frame mix, Pixel motion)
    """
    FRAME_MIX = 0x00  # Frame Mix
    PIXEL_MOTION = 0x01  # Pixel Motion
