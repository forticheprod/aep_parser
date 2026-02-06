"""Render settings model for AEP projects.

Render settings define how a composition is rendered in the render queue.
These correspond to the "Render Settings" dialog in After Effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class RenderQuality(IntEnum):
    """Quality setting for rendering.

    See: Render Settings > Quality
    """

    WIREFRAME = 0
    DRAFT = 1
    BEST = 2


class FieldRender(IntEnum):
    """Field rendering option.

    See: Render Settings > Field Render
    """

    OFF = 0
    UPPER_FIELD_FIRST = 1
    LOWER_FIELD_FIRST = 2


class Pulldown(IntEnum):
    """3:2 Pulldown phase for field rendering.

    See: Render Settings > 3:2 Pulldown
    """

    OFF = 0
    WSSWW = 1
    SSWWW = 2
    SWWWS = 3
    WWWSS = 4
    WWSSW = 5


class MotionBlurSetting(IntEnum):
    """Motion blur render setting.

    See: Render Settings > Motion Blur
    """

    OFF_FOR_ALL_LAYERS = 0
    ON_FOR_CHECKED_LAYERS = 1
    ON_FOR_ALL_LAYERS = 2


class FrameBlendingSetting(IntEnum):
    """Frame blending render setting.

    See: Render Settings > Frame Blending
    """

    OFF_FOR_ALL_LAYERS = 0
    ON_FOR_CHECKED_LAYERS = 1
    ON_FOR_ALL_LAYERS = 2


class EffectsSetting(IntEnum):
    """Effects render setting.

    See: Render Settings > Effects
    """

    ALL_OFF = 0
    ALL_ON = 1
    CURRENT_SETTINGS = 2


class ProxyUseSetting(IntEnum):
    """Proxy usage render setting.

    See: Render Settings > Proxy Use
    """

    USE_NO_PROXIES = 0
    USE_ALL_PROXIES = 1
    USE_COMP_PROXIES_ONLY = 3


class SoloSwitchesSetting(IntEnum):
    """Solo switches render setting.

    See: Render Settings > Solo Switches
    """

    ALL_OFF = 0
    CURRENT_SETTINGS = 2


class GuideLayers(IntEnum):
    """Guide layers render setting.

    See: Render Settings > Guide Layers
    """

    ALL_OFF = 0
    CURRENT_SETTINGS = 2


class ColorDepthSetting(IntEnum):
    """Color depth render setting.

    See: Render Settings > Color Depth
    """

    CURRENT_SETTINGS = -1  # 0xFFFF
    EIGHT_BITS_PER_CHANNEL = 0
    SIXTEEN_BITS_PER_CHANNEL = 1
    THIRTY_TWO_BITS_PER_CHANNEL = 2


class TimeSpanSource(IntEnum):
    """Time span source setting.

    See: Render Settings > Time Span
    """

    WORK_AREA_ONLY = 0
    LENGTH_OF_COMP = 1
    CUSTOM = 2


@dataclass
class RenderSettings:
    """Render settings for a render queue item.

    These settings define how the composition is rendered and correspond
    to the "Render Settings" dialog in After Effects.

    Attributes:
        template_name: The name of the render settings template being used.
        quality: The render quality (Best, Draft, Wireframe).
        resolution_x: Horizontal resolution divisor (1=Full, 2=Half, etc.).
        resolution_y: Vertical resolution divisor (1=Full, 2=Half, etc.).
        field_render: Field rendering option.
        pulldown: 3:2 Pulldown phase when field rendering is enabled.
        motion_blur: Motion blur render setting.
        frame_blending: Frame blending render setting.
        effects: Effects render setting.
        proxy_use: Proxy usage render setting.
        solo_switches: Solo switches render setting.
        guide_layers: Guide layers render setting.
        color_depth: Color depth render setting.
        time_span_source: Source for the time span to render.
        frame_rate: Frame rate in frames per second.
        use_this_frame_rate: If True, use the custom frame_rate instead of comp.
    """

    template_name: str | None = None
    quality: RenderQuality = RenderQuality.BEST
    resolution_x: int = 1
    resolution_y: int = 1
    field_render: FieldRender = FieldRender.OFF
    pulldown: Pulldown = Pulldown.OFF
    motion_blur: MotionBlurSetting = MotionBlurSetting.ON_FOR_CHECKED_LAYERS
    frame_blending: FrameBlendingSetting = FrameBlendingSetting.ON_FOR_CHECKED_LAYERS
    effects: EffectsSetting = EffectsSetting.CURRENT_SETTINGS
    proxy_use: ProxyUseSetting = ProxyUseSetting.USE_NO_PROXIES
    solo_switches: SoloSwitchesSetting = SoloSwitchesSetting.CURRENT_SETTINGS
    guide_layers: GuideLayers = GuideLayers.ALL_OFF
    color_depth: ColorDepthSetting = ColorDepthSetting.CURRENT_SETTINGS
    time_span_source: TimeSpanSource = TimeSpanSource.WORK_AREA_ONLY
    frame_rate: float = 30.0
    use_this_frame_rate: bool = False

    @property
    def resolution_factor(self) -> tuple[int, int]:
        """Resolution as a tuple (x_divisor, y_divisor).

        Returns:
            Tuple of (horizontal divisor, vertical divisor).
            (1, 1) = Full, (2, 2) = Half, (4, 4) = Quarter, etc.
        """
        return (self.resolution_x, self.resolution_y)

    @property
    def resolution_name(self) -> str:
        """Human-readable resolution name.

        Returns:
            "Full", "Half", "Third", "Quarter", or "Custom (X×Y)".
        """
        if self.resolution_x == self.resolution_y:
            names = {1: "Full", 2: "Half", 3: "Third", 4: "Quarter"}
            if self.resolution_x in names:
                return names[self.resolution_x]
        return f"Custom ({self.resolution_x}×{self.resolution_y})"
