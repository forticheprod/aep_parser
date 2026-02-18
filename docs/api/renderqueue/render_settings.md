# Render Settings

Render settings are stored as a [RenderSettings][aep_parser.models.settings.RenderSettings] `TypedDict` on the `RenderQueueItem.settings` attribute, with ExtendScript-compatible keys matching the format from `RenderQueueItem.getSettings(GetSettingsFormat.NUMBER)`.

::: aep_parser.models.settings.RenderSettings
    options:
      show_root_heading: true
      show_bases: false

## Available Keys

| Key | Type | Description |
|-----|------|-------------|
| `"3:2 Pulldown"` | `int` | Pulldown phase setting |
| `"Color Depth"` | `ColorDepthSetting` | Color depth (CURRENT, EIGHT_BPC, SIXTEEN_BPC, THIRTY_TWO_BPC) |
| `"Disk Cache"` | `DiskCacheSetting` | Disk cache setting (READ_ONLY, CURRENT_SETTINGS) |
| `"Effects"` | `EffectsSetting` | Effects (ALL_OFF, ALL_ON, CURRENT_SETTINGS) |
| `"Field Render"` | `int` | Field render (0=Off, 1=Upper First, 2=Lower First) |
| `"Frame Blending"` | `FrameBlendingSetting` | Frame blending (OFF, ON_FOR_CHECKED_LAYERS, CURRENT_SETTINGS) |
| `"Frame Rate"` | `bool` | Whether to use a custom frame rate |
| `"Guide Layers"` | `GuideLayers` | Guide layers (ALL_OFF, CURRENT_SETTINGS) |
| `"Motion Blur"` | `MotionBlurSetting` | Motion blur (OFF, ON_FOR_CHECKED_LAYERS, CURRENT_SETTINGS) |
| `"Proxy Use"` | `ProxyUseSetting` | Proxy use (USE_NO_PROXIES, USE_ALL_PROXIES, CURRENT_SETTINGS, USE_COMP_PROXIES_ONLY) |
| `"Quality"` | `RenderQuality` | Quality setting (CURRENT, WIREFRAME, DRAFT, BEST) |
| `"Resolution"` | `list[int]` | Resolution factor [x, y] (e.g., [1, 1] = full, [2, 2] = half) |
| `"Skip Existing Files"` | `bool` | Whether to skip rendering if output file exists |
| `"Solo Switches"` | `SoloSwitchesSetting` | Solo switches (ALL_OFF, CURRENT_SETTINGS) |
| `"Time Span Duration"` | `float` | Duration in seconds |
| `"Time Span End"` | `float` | End time in seconds |
| `"Time Span Start"` | `float` | Start time in seconds |
| `"Time Span"` | `TimeSpanSource` | Time span source (WORK_AREA, LENGTH_OF_COMP, CUSTOM) |
| `"Use comp's frame rate"` | `float` | The composition's frame rate |
| `"Use this frame rate"` | `float` | Custom frame rate value (when `"Frame Rate"` is True) |
