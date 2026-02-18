# Output Module Settings

Output module settings are stored as an [OutputModuleSettings][aep_parser.models.settings.OutputModuleSettings] `TypedDict` on the `OutputModule.settings` attribute, with ExtendScript-compatible keys matching the format from `OutputModule.getSettings(GetSettingsFormat.NUMBER)`.

::: aep_parser.models.settings.OutputModuleSettings
    options:
      show_root_heading: true
      show_bases: false

## Available Keys

| Key | Type | Description |
|-----|------|-------------|
| `"Audio Bit Depth"` | `AudioBitDepth` | Audio bit depth |
| `"Audio Channels"` | `AudioChannels` | Audio channel configuration |
| `"Audio Sample Rate"` | `int` | Audio sample rate in Hz |
| `"Channels"` | `OutputChannels` | Output channels configuration |
| `"Color"` | `OutputColorMode` | Color mode (straight or premultiplied alpha) |
| `"Crop Bottom"` | `int` | Crop pixels from the bottom |
| `"Crop Left"` | `int` | Crop pixels from the left |
| `"Crop Right"` | `int` | Crop pixels from the right |
| `"Crop Top"` | `int` | Crop pixels from the top |
| `"Crop"` | `bool` | Whether the Crop checkbox is enabled |
| `"Depth"` | `OutputColorDepth` | Output color depth |
| `"Format"` | `int` | Output format numeric ID |
| `"Include Project Link"` | `bool` | Whether to include a project link in the output |
| `"Include Source XMP Metadata"` | `bool` | Whether to include source XMP metadata |
| `"Lock Aspect Ratio"` | `bool` | Whether the aspect ratio is locked when resizing |
| `"Output Audio"` | `bool` | Whether audio output is enabled |
| `"Post-Render Action"` | `PostRenderAction` | Action to perform after rendering |
| `"Resize Quality"` | `int` | Resize quality level |
| `"Resize"` | `bool` | Whether resizing is enabled |
| `"Starting #"` | `int` | Starting frame number for file sequences |
| `"Use Comp Frame Number"` | `int` | Whether to use composition frame numbers |
| `"Use Region of Interest"` | `int` | Whether to use the region of interest |
| `"Video Output"` | `bool` | Whether video output is enabled |
