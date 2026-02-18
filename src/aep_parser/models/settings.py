"""Typed dictionaries for render queue settings.

These TypedDicts replace ``dict[str, Any]`` for render settings and
output module settings, giving type-checking for the
ExtendScript-compatible key names used throughout the render queue code.

The functional TypedDict syntax is used because keys like ``"3:2 Pulldown"``
and ``"Time Span Duration"`` are not valid Python identifiers.
"""

from __future__ import annotations

try:
    from typing import TypedDict  # Python 3.8+
except ImportError:
    from typing_extensions import TypedDict  # type: ignore[assignment]

from .enums import (
    AudioBitDepth,
    AudioChannels,
    ColorDepthSetting,
    DiskCacheSetting,
    EffectsSetting,
    FrameBlendingSetting,
    GuideLayers,
    MotionBlurSetting,
    OutputChannels,
    OutputColorDepth,
    OutputColorMode,
    PostRenderAction,
    ProxyUseSetting,
    RenderQuality,
    SoloSwitchesSetting,
    TimeSpanSource,
)

RenderSettings = TypedDict("RenderSettings", {
    "3:2 Pulldown": int,
    "Color Depth": ColorDepthSetting,
    "Disk Cache": DiskCacheSetting,
    "Effects": EffectsSetting,
    "Field Render": int,
    "Frame Blending": FrameBlendingSetting,
    "Frame Rate": bool,
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
    "Audio Sample Rate": int,
    "Channels": OutputChannels,
    "Color": OutputColorMode,
    "Crop Bottom": int,
    "Crop Left": int,
    "Crop Right": int,
    "Crop Top": int,
    "Crop": bool,
    "Depth": OutputColorDepth,
    "Format": int,
    "Include Project Link": bool,
    "Include Source XMP Metadata": bool,
    "Lock Aspect Ratio": bool,
    "Output Audio": bool,
    "Post-Render Action": PostRenderAction,
    "Resize Quality": int,
    "Resize": bool,
    "Starting #": int,
    "Use Comp Frame Number": int,
    "Use Region of Interest": int,
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
