"""Output module settings model for AEP projects.

Output module settings define how a composition is encoded/exported.
These correspond to the "Output Module Settings" dialog in After Effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class OutputChannels(IntEnum):
    """Output channels setting.

    See: Output Module Settings > Channels
    """

    RGB = 0
    RGBA = 1
    ALPHA = 2


class OutputColorDepth(IntEnum):
    """Output color depth in bits per channel.

    See: Output Module Settings > Depth
    """

    MILLIONS_OF_COLORS = 0  # 8 bpc
    TRILLIONS_OF_COLORS = 1  # 16 bpc
    FLOATING_POINT = 2  # 32 bpc


class OutputColorMode(IntEnum):
    """Output color mode (premultiplied vs straight).

    See: Output Module Settings > Color
    """

    STRAIGHT_UNMATTED = 0
    PREMULTIPLIED = 1


class AudioBitDepth(IntEnum):
    """Audio bit depth.

    See: Output Module Settings > Audio > Format
    """

    EIGHT_BIT = 1
    SIXTEEN_BIT = 2
    TWENTY_FOUR_BIT = 3
    THIRTY_TWO_BIT = 4


class AudioChannels(IntEnum):
    """Audio channels.

    See: Output Module Settings > Audio > Channels
    """

    MONO = 1
    STEREO = 2


class ResizeQuality(IntEnum):
    """Resize quality setting.

    See: Output Module Settings > Stretch > Quality
    """

    LOW = 0
    HIGH = 1


@dataclass
class OutputModuleSettings:
    """Output module settings for a render queue item.

    These settings define how the rendered output is encoded and correspond
    to the "Output Module Settings" dialog in After Effects.

    Note: Not all settings from the Roou chunk have been reverse-engineered.
    This model contains the fields that have been identified so far.

    Attributes:
        video_codec: The four-character code of the video codec.
        has_video: Whether video output is enabled.
        has_audio: Whether audio output is enabled.
        width: Output width in pixels (0 = match render settings).
        height: Output height in pixels (0 = match render settings).
        frame_rate: Output frame rate in fps.
        color_premultiplied: Whether color is premultiplied with alpha.
        color_matted: Whether color is matted.
        audio_bit_depth: Audio bit depth (8, 16, 24, or 32 bit).
        audio_channels: Number of audio channels (1=mono, 2=stereo).
    """

    video_codec: str | None = None
    has_video: bool = True
    has_audio: bool = True
    width: int = 0
    height: int = 0
    frame_rate: float = 30.0
    color_premultiplied: bool = True
    color_matted: bool = True
    audio_bit_depth: AudioBitDepth = AudioBitDepth.SIXTEEN_BIT
    audio_channels: AudioChannels = AudioChannels.STEREO
