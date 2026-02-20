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
| `"Color Depth"` | [ColorDepthSetting][aep_parser.models.enums.ColorDepthSetting] | Color depth setting |
| `"Disk Cache"` | [DiskCacheSetting][aep_parser.models.enums.DiskCacheSetting] | Disk cache setting |
| `"Effects"` | [EffectsSetting][aep_parser.models.enums.EffectsSetting] | Effects setting |
| `"Field Render"` | [FieldRender][aep_parser.models.enums.FieldRender] | Field render setting |
| `"Frame Blending"` | [FrameBlendingSetting][aep_parser.models.enums.FrameBlendingSetting] | Frame blending setting |
| `"Frame Rate"` | [FrameRateSetting][aep_parser.models.enums.FrameRateSetting] | Frame rate source |
| `"Guide Layers"` | [GuideLayers][aep_parser.models.enums.GuideLayers] | Guide layers setting |
| `"Motion Blur"` | [MotionBlurSetting][aep_parser.models.enums.MotionBlurSetting] | Motion blur setting |
| `"Proxy Use"` | [ProxyUseSetting][aep_parser.models.enums.ProxyUseSetting] | Proxy use setting |
| `"Quality"` | [RenderQuality][aep_parser.models.enums.RenderQuality] | Quality setting |
| `"Resolution"` | `list[int]` | Resolution factor `[x, y]` (e.g. `[1, 1]` = Full, `[2, 2]` = Half, `[3, 3]` = Third, `[4, 4]` = Quarter) |
| `"Skip Existing Files"` | `bool` | Whether to skip rendering if output file exists |
| `"Solo Switches"` | [SoloSwitchesSetting][aep_parser.models.enums.SoloSwitchesSetting] | Solo switches setting |
| `"Time Span Duration"` | `float` | Duration in seconds |
| `"Time Span End"` | `float` | End time in seconds |
| `"Time Span Start"` | `float` | Start time in seconds |
| `"Time Span"` | [TimeSpanSource][aep_parser.models.enums.TimeSpanSource] | Time span source |
| `"Use comp's frame rate"` | `float` | The composition's frame rate |
| `"Use this frame rate"` | `float` | Custom frame rate value (when `"Frame Rate"` is `USE_THIS_FRAME_RATE`) |

## Enum Values

### PulldownSetting

| Member | Value | Label |
|--------|-------|-------|
| `OFF` | 0 | `"Off"` |
| `WSSWW` | 1 | `"WSSWW"` |
| `SSWWW` | 2 | `"SSWWW"` |
| `SWWWS` | 3 | `"SWWWS"` |
| `WWWSS` | 4 | `"WWWSS"` |
| `WWSSW` | 5 | `"WWSSW"` |

### ColorDepthSetting

| Member | Value | Label |
|--------|-------|-------|
| `CURRENT_SETTINGS` | -1 | `"Current Settings"` |
| `EIGHT_BITS_PER_CHANNEL` | 0 | `"8 bits per channel"` |
| `SIXTEEN_BITS_PER_CHANNEL` | 1 | `"16 bits per channel"` |
| `THIRTY_TWO_BITS_PER_CHANNEL` | 2 | `"32 bits per channel"` |

### FieldRender

| Member | Value | Label |
|--------|-------|-------|
| `OFF` | 0 | `"Off"` |
| `UPPER_FIELD_FIRST` | 1 | `"Upper Field First"` |
| `LOWER_FIELD_FIRST` | 2 | `"Lower Field First"` |

### FrameRateSetting

| Member | Value | Label |
|--------|-------|-------|
| `USE_COMP_FRAME_RATE` | 0 | `"Use comp's frame rate"` |
| `USE_THIS_FRAME_RATE` | 1 | `"Use this frame rate"` |

### RenderQuality

| Member | Value | Label |
|--------|-------|-------|
| `CURRENT_SETTINGS` | -1 | `"Current Settings"` |
| `WIREFRAME` | 0 | `"Wireframe"` |
| `DRAFT` | 1 | `"Draft"` |
| `BEST` | 2 | `"Best"` |

### MotionBlurSetting

| Member | Value | Label |
|--------|-------|-------|
| `OFF_FOR_ALL_LAYERS` | 0 | `"Off for All Layers"` |
| `ON_FOR_CHECKED_LAYERS` | 1 | `"On for Checked Layers"` |
| `CURRENT_SETTINGS` | 2 | `"Current Settings"` |

### FrameBlendingSetting

| Member | Value | Label |
|--------|-------|-------|
| `OFF_FOR_ALL_LAYERS` | 0 | `"Off for All Layers"` |
| `ON_FOR_CHECKED_LAYERS` | 1 | `"On for Checked Layers"` |
| `CURRENT_SETTINGS` | 2 | `"Current Settings"` |

### EffectsSetting

| Member | Value | Label |
|--------|-------|-------|
| `ALL_OFF` | 0 | `"All Off"` |
| `ALL_ON` | 1 | `"All On"` |
| `CURRENT_SETTINGS` | 2 | `"Current Settings"` |

### ProxyUseSetting

| Member | Value | Label |
|--------|-------|-------|
| `USE_NO_PROXIES` | 0 | `"Use No Proxies"` |
| `USE_ALL_PROXIES` | 1 | `"Use All Proxies"` |
| `CURRENT_SETTINGS` | 2 | `"Current Settings"` |
| `USE_COMP_PROXIES_ONLY` | 3 | `"Use Comp Proxies Only"` |

### SoloSwitchesSetting

| Member | Value | Label |
|--------|-------|-------|
| `ALL_OFF` | 0 | `"All Off"` |
| `CURRENT_SETTINGS` | 2 | `"Current Settings"` |

### GuideLayers

| Member | Value | Label |
|--------|-------|-------|
| `ALL_OFF` | 0 | `"All Off"` |
| `CURRENT_SETTINGS` | 2 | `"Current Settings"` |

### DiskCacheSetting

| Member | Value | Label |
|--------|-------|-------|
| `READ_ONLY` | 0 | `"Read Only"` |
| `CURRENT_SETTINGS` | 2 | `"Current Settings"` |

### TimeSpanSource

| Member | Value | Label |
|--------|-------|-------|
| `LENGTH_OF_COMP` | 0 | `"Length of Comp"` |
| `WORK_AREA_ONLY` | 1 | `"Work Area Only"` |
| `CUSTOM` | 2 | `"Custom"` |
