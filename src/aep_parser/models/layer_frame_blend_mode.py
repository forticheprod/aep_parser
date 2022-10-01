from enum import Enum


class LayerFrameBlendMode(Enum):
    """
    Frame blending mode of a layer (eg: Frame mix, Pixel motion)
    """
    LAYER_FRAME_BLEND_MODE_FRAME_MIX = 0x00  # Frame Mix
    LAYER_FRAME_BLEND_MODE_PIXEL_MOTION = 0x01  # Pixel Motion
