# Render Settings

Render settings are stored as a [RenderSettings][aep_parser.models.settings.RenderSettings] `TypedDict` on the `RenderQueueItem.settings` attribute, with ExtendScript-compatible keys matching the format from `RenderQueueItem.getSettings(GetSettingsFormat.NUMBER)`.

::: aep_parser.models.settings.RenderSettings
    options:
      show_root_heading: true
      show_bases: false

## Available Keys

| Key | Type | Description |
|-----|------|-------------|
| `"3:2 Pulldown"` | [PulldownSetting][aep_parser.models.enums.PulldownSetting] | Pulldown phase setting |
| `"Color Depth"` | [ColorDepthSetting][aep_parser.models.enums.ColorDepthSetting] | Color depth (CURRENT, EIGHT_BPC, SIXTEEN_BPC, THIRTY_TWO_BPC) |
| `"Disk Cache"` | [DiskCacheSetting][aep_parser.models.enums.DiskCacheSetting] | Disk cache setting (READ_ONLY, CURRENT_SETTINGS) |
| `"Effects"` | [EffectsSetting][aep_parser.models.enums.EffectsSetting] | Effects (ALL_OFF, ALL_ON, CURRENT_SETTINGS) |
| `"Field Render"` | [FieldRender][aep_parser.models.enums.FieldRender] | Field render (OFF, UPPER_FIELD_FIRST, LOWER_FIELD_FIRST) |
| `"Frame Blending"` | [FrameBlendingSetting][aep_parser.models.enums.FrameBlendingSetting] | Frame blending (OFF, ON_FOR_CHECKED_LAYERS, CURRENT_SETTINGS) |
| `"Frame Rate"` | [FrameRateSetting][aep_parser.models.enums.FrameRateSetting] | Frame rate source (USE_COMP_FRAME_RATE or USE_THIS_FRAME_RATE) |
| `"Guide Layers"` | [GuideLayers][aep_parser.models.enums.GuideLayers] | Guide layers (ALL_OFF, CURRENT_SETTINGS) |
| `"Motion Blur"` | [MotionBlurSetting][aep_parser.models.enums.MotionBlurSetting] | Motion blur (OFF, ON_FOR_CHECKED_LAYERS, CURRENT_SETTINGS) |
| `"Proxy Use"` | [ProxyUseSetting][aep_parser.models.enums.ProxyUseSetting] | Proxy use (USE_NO_PROXIES, USE_ALL_PROXIES, CURRENT_SETTINGS, USE_COMP_PROXIES_ONLY) |
| `"Quality"` | [RenderQuality][aep_parser.models.enums.RenderQuality] | Quality setting (CURRENT, WIREFRAME, DRAFT, BEST) |
| `"Resolution"` | `list` | Resolution factor [x, y] (e.g., [1, 1] = full, [2, 2] = half) |
| `"Skip Existing Files"` | `bool` | Whether to skip rendering if output file exists |
| `"Solo Switches"` | [SoloSwitchesSetting][aep_parser.models.enums.SoloSwitchesSetting] | Solo switches (ALL_OFF, CURRENT_SETTINGS) |
| `"Time Span Duration"` | `float` | Duration in seconds |
| `"Time Span End"` | `float` | End time in seconds |
| `"Time Span Start"` | `float` | Start time in seconds |
| `"Time Span"` | [TimeSpanSource][aep_parser.models.enums.TimeSpanSource] | Time span source (WORK_AREA, LENGTH_OF_COMP, CUSTOM) |
| `"Use comp's frame rate"` | `float` | The composition's frame rate |
| `"Use this frame rate"` | `float` | Custom frame rate value (when `"Frame Rate"` is `USE_THIS_FRAME_RATE`) |
