# Output Module Settings

Output module settings are stored as an [OutputModuleSettings][aep_parser.models.settings.OutputModuleSettings] `TypedDict` on the `OutputModule.settings` attribute, with ExtendScript-compatible keys matching the format from `OutputModule.getSettings(GetSettingsFormat.NUMBER)`.

::: aep_parser.models.settings.OutputModuleSettings
    options:
      show_root_heading: true
      show_bases: false

## Available Keys

| Key | Type | Description |
|-----|------|-------------|
| `"Audio Bit Depth"` | [AudioBitDepth][aep_parser.models.enums.AudioBitDepth] | Audio bit depth |
| `"Audio Channels"` | [AudioChannels][aep_parser.models.enums.AudioChannels] | Audio channel configuration |
| `"Audio Sample Rate"` | [AudioSampleRate][aep_parser.models.enums.AudioSampleRate] | Audio sample rate in Hz |
| `"Channels"` | [OutputChannels][aep_parser.models.enums.OutputChannels] | Output channels configuration |
| `"Color"` | [OutputColorMode][aep_parser.models.enums.OutputColorMode] | Color mode (straight or premultiplied alpha) |
| `"Crop Bottom"` | `int` | Crop pixels from the bottom |
| `"Crop Left"` | `int` | Crop pixels from the left |
| `"Crop Right"` | `int` | Crop pixels from the right |
| `"Crop Top"` | `int` | Crop pixels from the top |
| `"Crop"` | `bool` | Whether the Crop checkbox is enabled |
| `"Depth"` | [OutputColorDepth][aep_parser.models.enums.OutputColorDepth] | Output color depth |
| `"Format"` | [OutputFormat][aep_parser.models.enums.OutputFormat] | Output format |
| `"Include Project Link"` | `bool` | Whether to include a project link in the output |
| `"Include Source XMP Metadata"` | `bool` | Whether to include source XMP metadata |
| `"Lock Aspect Ratio"` | `bool` | Whether the aspect ratio is locked when resizing |
| `"Output Audio"` | [OutputAudio][aep_parser.models.enums.OutputAudio] | Audio output mode (Off, On, or Auto) |
| `"Output File Info"` | `dict[str, str]` | Output file path info (Full Flat Path, Base Path, Subfolder Path, File Name, File Template) |
| `"Post-Render Action"` | [PostRenderAction][aep_parser.models.enums.PostRenderAction] | Action to perform after rendering |
| `"Resize Quality"` | [ResizeQuality][aep_parser.models.enums.ResizeQuality] | Resize quality level |
| `"Resize to"` | `list[int]` | Target resize dimensions `[width, height]` |
| `"Resize"` | `bool` | Whether resizing is enabled |
| `"Starting #"` | `int` | Starting frame number for file sequences |
| `"Use Comp Frame Number"` | `bool` | Whether to use composition frame numbers |
| `"Use Region of Interest"` | `bool` | Whether to use the region of interest |
| `"Video Output"` | `bool` | Whether video output is enabled |
