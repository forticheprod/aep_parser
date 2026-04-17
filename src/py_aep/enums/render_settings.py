"""Render settings enumerations for After Effects render queue items.

These enums match the values used in After Effects ExtendScript.
"""

from __future__ import annotations

from enum import IntEnum


class FrameRateSetting(IntEnum):
    """Frame rate source setting for rendering.

    Determines whether the render uses the composition's own frame rate
    or a custom frame rate specified in the render settings.

    Used in RenderQueueItem Settings > Frame Rate

    Not documented in AE scripting reference.
    """

    USE_COMP_FRAME_RATE = 0
    USE_THIS_FRAME_RATE = 1

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _FRAME_RATE_SETTING_LABELS[self.value]


_FRAME_RATE_SETTING_LABELS: dict[int, str] = {
    0: "Use comp's frame rate",
    1: "Use this frame rate",
}


class RenderQuality(IntEnum):
    """Quality setting for rendering.

    Used in RenderQueueItem Settings > Quality

    Not documented in AE scripting reference.
    """

    CURRENT_SETTINGS = -1
    WIREFRAME = 0
    DRAFT = 1
    BEST = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _RENDER_QUALITY_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> RenderQuality:
        """Convert binary value to RenderQuality (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)

    def to_binary(self) -> int:
        """Convert to binary value (CURRENT_SETTINGS -> 0xFFFF)."""
        return int(self) & 0xFFFF


_RENDER_QUALITY_LABELS: dict[int, str] = {
    -1: "Current Settings",
    0: "Wireframe",
    1: "Draft",
    2: "Best",
}


class FieldRender(IntEnum):
    """Field rendering option.

    Used in RenderQueueItem Settings > Field Render

    Not documented in AE scripting reference.
    """

    OFF = 0
    UPPER_FIELD_FIRST = 1
    LOWER_FIELD_FIRST = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _FIELD_RENDER_LABELS[self.value]


_FIELD_RENDER_LABELS: dict[int, str] = {
    0: "Off",
    1: "Upper Field First",
    2: "Lower Field First",
}


class PulldownSetting(IntEnum):
    """3:2 Pulldown phase for field rendering.

    Used in RenderQueueItem Settings > 3:2 Pulldown

    Not documented in AE scripting reference.
    """

    OFF = 0
    WSSWW = 1
    SSWWW = 2
    SWWWS = 3
    WWWSS = 4
    WWSSW = 5

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _PULLDOWN_SETTING_LABELS[self.value]


_PULLDOWN_SETTING_LABELS: dict[int, str] = {
    0: "Off",
    1: "WSSWW",
    2: "SSWWW",
    3: "SWWWS",
    4: "WWWSS",
    5: "WWSSW",
}


class MotionBlurSetting(IntEnum):
    """Motion blur render setting.

    Used in RenderQueueItem Settings > Motion Blur

    Not documented in AE scripting reference.
    """

    OFF_FOR_ALL_LAYERS = 0
    ON_FOR_CHECKED_LAYERS = 1
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _MOTION_BLUR_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> MotionBlurSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_MOTION_BLUR_SETTING_LABELS: dict[int, str] = {
    0: "Off for All Layers",
    1: "On for Checked Layers",
    2: "Current Settings",
}


class FrameBlendingSetting(IntEnum):
    """Frame blending render setting.

    Used in RenderQueueItem Settings > Frame Blending

    Not documented in AE scripting reference.
    """

    OFF_FOR_ALL_LAYERS = 0
    ON_FOR_CHECKED_LAYERS = 1
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _FRAME_BLENDING_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> FrameBlendingSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_FRAME_BLENDING_SETTING_LABELS: dict[int, str] = {
    0: "Off for All Layers",
    1: "On for Checked Layers",
    2: "Current Settings",
}


class EffectsSetting(IntEnum):
    """Effects render setting.

    Used in RenderQueueItem Settings > Effects

    Not documented in AE scripting reference.
    """

    ALL_OFF = 0
    ALL_ON = 1
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _EFFECTS_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> EffectsSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_EFFECTS_SETTING_LABELS: dict[int, str] = {
    0: "All Off",
    1: "All On",
    2: "Current Settings",
}


class ProxyUseSetting(IntEnum):
    """Proxy usage render setting.

    Used in RenderQueueItem Settings > Proxy Use

    Not documented in AE scripting reference.
    """

    USE_NO_PROXIES = 0
    USE_ALL_PROXIES = 1
    CURRENT_SETTINGS = 2
    USE_COMP_PROXIES_ONLY = 3

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _PROXY_USE_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> ProxyUseSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_PROXY_USE_SETTING_LABELS: dict[int, str] = {
    0: "Use No Proxies",
    1: "Use All Proxies",
    2: "Current Settings",
    3: "Use Comp Proxies Only",
}


class SoloSwitchesSetting(IntEnum):
    """Solo switches render setting.

    Used in RenderQueueItem Settings > Solo Switches

    Not documented in AE scripting reference.
    """

    ALL_OFF = 0
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _SOLO_SWITCHES_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> SoloSwitchesSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_SOLO_SWITCHES_SETTING_LABELS: dict[int, str] = {
    0: "All Off",
    2: "Current Settings",
}


class GuideLayers(IntEnum):
    """Guide layers render setting.

    Used in RenderQueueItem Settings > Guide Layers

    Not documented in AE scripting reference.
    """

    ALL_OFF = 0
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _GUIDE_LAYERS_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> GuideLayers:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_GUIDE_LAYERS_LABELS: dict[int, str] = {
    0: "All Off",
    2: "Current Settings",
}


class DiskCacheSetting(IntEnum):
    """Disk cache render setting.

    Used in RenderQueueItem Settings > Disk Cache

    Not documented in AE scripting reference.
    """

    READ_ONLY = 0
    CURRENT_SETTINGS = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _DISK_CACHE_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> DiskCacheSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)


_DISK_CACHE_SETTING_LABELS: dict[int, str] = {
    0: "Read Only",
    2: "Current Settings",
}


class ColorDepthSetting(IntEnum):
    """Color depth render setting.

    Used in RenderQueueItem Settings > Color Depth

    Not documented in AE scripting reference.
    """

    CURRENT_SETTINGS = -1
    EIGHT_BITS_PER_CHANNEL = 0
    SIXTEEN_BITS_PER_CHANNEL = 1
    THIRTY_TWO_BITS_PER_CHANNEL = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _COLOR_DEPTH_SETTING_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> ColorDepthSetting:
        """Convert binary value (0xFFFF = CURRENT_SETTINGS)."""
        return cls.CURRENT_SETTINGS if value == 0xFFFF else cls(value)

    def to_binary(self) -> int:
        """Convert to binary value (CURRENT_SETTINGS -> 0xFFFF)."""
        return int(self) & 0xFFFF


_COLOR_DEPTH_SETTING_LABELS: dict[int, str] = {
    -1: "Current Settings",
    0: "8 bits per channel",
    1: "16 bits per channel",
    2: "32 bits per channel",
}


class TimeSpanSource(IntEnum):
    """Time span source setting.

    Used in RenderQueueItem Settings > Time Span

    Not documented in AE scripting reference.
    """

    LENGTH_OF_COMP = 0
    WORK_AREA_ONLY = 1
    CUSTOM = 2

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _TIME_SPAN_SOURCE_LABELS[self.value]

    @classmethod
    def from_binary(cls, value: int) -> TimeSpanSource:
        """Convert binary value (0xFFFF = CUSTOM)."""
        return cls.CUSTOM if value == 0xFFFF else cls(value)


_TIME_SPAN_SOURCE_LABELS: dict[int, str] = {
    0: "Length of Comp",
    1: "Work Area Only",
    2: "Custom",
}


class PostRenderActionSetting(IntEnum):
    """Post-render action for the output module settings dict.

    Used in OutputModule Settings > Post-Render Action

    Not documented in AE scripting reference.
    """

    NONE = 0
    IMPORT = 1
    IMPORT_AND_REPLACE_USAGE = 2
    SET_PROXY = 3

    @property
    def label(self) -> str:
        """ExtendScript STRING format label."""
        return _POST_RENDER_ACTION_SETTING_LABELS[self.value]


_POST_RENDER_ACTION_SETTING_LABELS: dict[int, str] = {
    0: "None",
    1: "Import",
    2: "Import & Replace Usage",
    3: "Set Proxy",
}
