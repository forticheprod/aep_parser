# Render Settings

Render settings are stored as a `dict[str, Any]` on the `RenderQueueItem.settings` attribute, with ExtendScript-compatible keys matching the format from `RenderQueueItem.getSettings(GetSettingsFormat.NUMBER)`.

## Available Keys

| Key | Type | Description |
|-----|------|-------------|
| `"Quality"` | `RenderQuality` | Quality setting (CURRENT, WIREFRAME, DRAFT, BEST) |
| `"Resolution"` | `list[int]` | Resolution factor [x, y] (e.g., [1, 1] = full, [2, 2] = half) |
| `"Field Render"` | `int` | Field render (0=Off, 1=Upper First, 2=Lower First) |
| `"3:2 Pulldown"` | `int` | Pulldown phase setting |
| `"Motion Blur"` | `MotionBlurSetting` | Motion blur (OFF, ON_FOR_CHECKED_LAYERS, CURRENT_SETTINGS) |
| `"Frame Blending"` | `FrameBlendingSetting` | Frame blending (OFF, ON_FOR_CHECKED_LAYERS, CURRENT_SETTINGS) |
| `"Effects"` | `EffectsSetting` | Effects (ALL_OFF, ALL_ON, CURRENT_SETTINGS) |
| `"Proxy Use"` | `ProxyUseSetting` | Proxy use (USE_NO_PROXIES, USE_ALL_PROXIES, CURRENT_SETTINGS, USE_COMP_PROXIES_ONLY) |
| `"Solo Switches"` | `SoloSwitchesSetting` | Solo switches (ALL_OFF, CURRENT_SETTINGS) |
| `"Guide Layers"` | `GuideLayers` | Guide layers (ALL_OFF, CURRENT_SETTINGS) |
| `"Disk Cache"` | `DiskCacheSetting` | Disk cache setting (READ_ONLY, CURRENT_SETTINGS) |
| `"Color Depth"` | `ColorDepthSetting` | Color depth (CURRENT, EIGHT_BPC, SIXTEEN_BPC, THIRTY_TWO_BPC) |
| `"Time Span"` | `TimeSpanSource` | Time span source (WORK_AREA, LENGTH_OF_COMP, CUSTOM) |
| `"Time Span Start"` | `float` | Start time in seconds |
| `"Time Span Duration"` | `float` | Duration in seconds |
| `"Time Span End"` | `float` | End time in seconds |
| `"Frame Rate"` | `bool` | Whether to use a custom frame rate |
| `"Use this frame rate"` | `float` | Custom frame rate value (when `"Frame Rate"` is True) |
| `"Use comp's frame rate"` | `float` | The composition's frame rate |
| `"Skip Existing Files"` | `bool` | Whether to skip rendering if output file exists |

## Enumerations

Most settings use enums from `aep_parser.models.enums`. See the [Enums](../enums.md) page for full documentation:

- [`RenderQuality`](../enums.md#aep_parser.models.enums.RenderQuality)
- [`MotionBlurSetting`](../enums.md#aep_parser.models.enums.MotionBlurSetting)
- [`FrameBlendingSetting`](../enums.md#aep_parser.models.enums.FrameBlendingSetting)
- [`EffectsSetting`](../enums.md#aep_parser.models.enums.EffectsSetting)
- [`ProxyUseSetting`](../enums.md#aep_parser.models.enums.ProxyUseSetting)
- [`TimeSpanSource`](../enums.md#aep_parser.models.enums.TimeSpanSource)
- [`ColorDepthSetting`](../enums.md#aep_parser.models.enums.ColorDepthSetting)
- [`LogType`](../enums.md#aep_parser.models.enums.LogType)
- [`SoloSwitchesSetting`](../enums.md#aep_parser.models.enums.SoloSwitchesSetting)
- [`GuideLayers`](../enums.md#aep_parser.models.enums.GuideLayers)
- [`DiskCacheSetting`](../enums.md#aep_parser.models.enums.DiskCacheSetting)

## Example Usage

```python
from aep_parser import parse_project

project = parse_project("project.aep")
for rq_item in project.render_queue.items:
    settings = rq_item.settings
    print(f"Quality: {settings['Quality'].name}")
    print(f"Resolution: {settings['Resolution']}")
    print(f"Motion Blur: {settings['Motion Blur'].name}")
    print(f"Time Span: {settings['Time Span'].name}")
    print(f"Template: {rq_item.name}")
```
