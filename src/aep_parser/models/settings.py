"""Typed dictionaries for render queue settings.

These TypedDicts replace ``dict[str, Any]`` for render settings and
output module settings, giving type-checking for the
ExtendScript-compatible key names used throughout the render queue code.

The functional TypedDict syntax is used because keys like ``"3:2 Pulldown"``
and ``"Time Span Duration"`` are not valid Python identifiers.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Any, Mapping

try:
    from typing import TypedDict  # Python 3.8+
except ImportError:
    from typing_extensions import TypedDict  # type: ignore[assignment]

from .enums import (
    AudioBitDepth,
    AudioChannels,
    AudioSampleRate,
    ColorDepthSetting,
    DiskCacheSetting,
    EffectsSetting,
    FieldRender,
    FrameBlendingSetting,
    FrameRateSetting,
    GuideLayers,
    MotionBlurSetting,
    OutputAudio,
    OutputChannels,
    OutputColorDepth,
    OutputColorMode,
    OutputFormat,
    PostRenderAction,
    ProxyUseSetting,
    PulldownSetting,
    RenderQuality,
    ResizeQuality,
    SoloSwitchesSetting,
    TimeSpanSource,
)

RenderSettings = TypedDict("RenderSettings", {
    "3:2 Pulldown": PulldownSetting,
    "Color Depth": ColorDepthSetting,
    "Disk Cache": DiskCacheSetting,
    "Effects": EffectsSetting,
    "Field Render": FieldRender,
    "Frame Blending": FrameBlendingSetting,
    "Frame Rate": FrameRateSetting,
    "Guide Layers": GuideLayers,
    "Motion Blur": MotionBlurSetting,
    "Proxy Use": ProxyUseSetting,
    "Quality": RenderQuality,
    "Resolution": list,
    "Skip Existing Files": bool,
    "Solo Switches": SoloSwitchesSetting,
    "Time Span Duration": float,
    "Time Span End": float,
    "Time Span Start": float,
    "Time Span": TimeSpanSource,
    "Use comp's frame rate": float,
    "Use this frame rate": float,
})
"""Render settings for a render queue item.

Keys match the ExtendScript
``RenderQueueItem.getSettings(GetSettingsFormat.NUMBER)`` output.

Example:
    ```python
    from aep_parser import parse

    project = parse("project.aep").project
    for rq_item in project.render_queue.items:
        for output_module in rq_item.output_modules:
            settings = output_module.settings
            print(f"Video Output: {settings['Video Output']}")
            print(f"Dimensions: {output_module.width}x{output_module.height}")
            print(f"Color Mode: {settings['Color'].name}")
            print(f"Output Frame Rate: {output_module.frame_rate}")
    ```
"""


OutputModuleSettings = TypedDict("OutputModuleSettings", {
    "Audio Bit Depth": AudioBitDepth,
    "Audio Channels": AudioChannels,
    "Audio Sample Rate": AudioSampleRate,
    "Channels": OutputChannels,
    "Color": OutputColorMode,
    "Crop Bottom": int,
    "Crop Left": int,
    "Crop Right": int,
    "Crop Top": int,
    "Crop": bool,
    "Depth": OutputColorDepth,
    "Format": OutputFormat,
    "Include Project Link": bool,
    "Include Source XMP Metadata": bool,
    "Lock Aspect Ratio": bool,
    "Output Audio": OutputAudio,
    "Output File Info": dict,
    "Post-Render Action": PostRenderAction,
    "Resize Quality": ResizeQuality,
    "Resize to": list,
    "Resize": bool,
    "Starting #": int,
    "Use Comp Frame Number": bool,
    "Use Region of Interest": bool,
    "Video Output": bool,
})
"""Output module settings for a render queue item.

Keys match the ExtendScript
``OutputModule.getSettings(GetSettingsFormat.NUMBER)`` output.

Example:
    ```python
    from aep_parser import parse

    project = parse("project.aep").project
    for rq_item in project.render_queue.items:
        for output_module in rq_item.output_modules:
            settings = output_module.settings
            print(f"Video Output: {settings['Video Output']}")
            print(f"Dimensions: {output_module.width}x{output_module.height}")
            print(f"Color Mode: {settings['Color'].name}")
            print(f"Output Frame Rate: {output_module.frame_rate}")
    ```
"""


_RESOLUTION_STRINGS: dict[tuple[int, int], str] = {
    (1, 1): "Full",
    (2, 2): "Half",
    (3, 3): "Third",
    (4, 4): "Quarter",
}

_RESIZE_TO_STRINGS: dict[tuple[int, int], str] = {
    (3656, 2664): "Cineon Full  •  3656x2664 • 24 fps",
    (1828, 1332): "Cineon Half  •  1828x1332 • 24 fps",
    (1280, 1080): "DVCPRO HD  •  1280x1080 (1.5) • 29.97 fps",
    (1440, 1080): "HDV  •  1440x1080 (1.33) • 29.97 fps",
    (960, 720): "DVCPRO HD  •  960x720 (1.33) • 29.97 fps",
    (2048, 1556): "Film (2K)  •  2048x1556 • 24 fps",
    (4096, 3112): "Film (4K)  •  4096x3112 • 24 fps",
    (1920, 1080): "Social Media Landscape HD  •  1920x1080 • 30 fps",
    (1280, 720): "Social Media Landscape  •  1280x720 • 30 fps",
    (720, 1280): "Social Media Portrait  •  720x1280 • 30 fps",
    (1080, 1920): "Social Media Portrait HD  •  1080x1920 • 30 fps",
    (1080, 1080): "Social Media Square  •  1080x1080 • 30 fps",
    (3840, 2160): "UHD (4K)  •  3840x2160 • 29.97 fps",
    (7680, 4320): "UHD (8K)  •  7680x4320 • 23.976 fps",
}


def _to_number_value(value: Any) -> Any:
    """Convert a settings value to NUMBER format.

    IntEnum values are unwrapped to their integer value.
    All other types pass through unchanged.
    """
    if isinstance(value, IntEnum):
        return int(value)
    return value


def _to_string_value(key: str, value: Any) -> str:
    """Convert a settings value to STRING format.

    Args:
        key: The settings key name.
        value: The settings value.
    """
    if isinstance(value, dict):
        return {
            k: _to_string_value(k, v)
            for k, v in value.items()
        }  # type: ignore[return-value]
    if isinstance(value, IntEnum):
        return value.label  # type: ignore[attr-defined,no-any-return]
    if key == "Resolution":
        return _RESOLUTION_STRINGS.get(tuple(value), "Custom")
    if key == "Resize to":
        return _RESIZE_TO_STRINGS.get(tuple(value), "Custom")
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def settings_to_number(
    settings: Mapping[str, Any],
) -> dict[str, Any]:
    """Convert settings to NUMBER format.

    IntEnum values are unwrapped to plain integers. Other values
    (bool, float, int, list) pass through unchanged.

    Args:
        settings: The typed settings dict.
    """
    return {k: _to_number_value(v) for k, v in settings.items()}


def settings_to_string(
    settings: Mapping[str, Any],
) -> dict[str, str]:
    """Convert settings to STRING format.

    All values are converted to their ExtendScript STRING representation.

    Args:
        settings: The typed settings dict.
    """
    return {
        k: _to_string_value(k, v)
        for k, v in settings.items()
    }
