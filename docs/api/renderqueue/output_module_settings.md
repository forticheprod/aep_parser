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
| `"Depth"` | [OutputColorDepth][aep_parser.models.enums.OutputColorDepth] | Output color depth in total bits per pixel |
| `"Format"` | [OutputFormat][aep_parser.models.enums.OutputFormat] | Output format |
| `"Include Project Link"` | `bool` | Whether to include a project link in the output |
| `"Include Source XMP Metadata"` | `bool` | Whether to include source XMP metadata |
| `"Lock Aspect Ratio"` | `bool` | Whether the aspect ratio is locked when resizing |
| `"Output Audio"` | [OutputAudio][aep_parser.models.enums.OutputAudio] | Audio output mode |
| `"Output File Info"` | `dict[str, str]` | Output file path info (see [sub-keys](#output-file-info-sub-keys) below) |
| `"Post-Render Action"` | [PostRenderAction][aep_parser.models.enums.PostRenderAction] | Action after rendering |
| `"Resize Quality"` | [ResizeQuality][aep_parser.models.enums.ResizeQuality] | Resize quality |
| `"Resize to"` | `list[int]` | Target resize dimensions `[width, height]` |
| `"Resize"` | `bool` | Whether resizing is enabled |
| `"Starting #"` | `int` | Starting frame number for file sequences |
| `"Use Comp Frame Number"` | `bool` | Whether to use composition frame numbers |
| `"Use Region of Interest"` | `bool` | Whether to use the region of interest |
| `"Video Output"` | `bool` | Whether video output is enabled |

### Output File Info Sub-Keys

The `"Output File Info"` value is a `dict[str, str]` with the following keys:

| Key | Description |
|-----|-------------|
| `"Full Flat Path"` | The fully resolved output file template path |
| `"Base Path"` | The output folder path from the alas data |
| `"Subfolder Path"` | Subfolder relative to the base path (empty string if none) |
| `"File Name"` | The file name portion of the template (e.g. `Comp 1.[fileExtension]`) |
| `"File Template"` | The raw file name template including any subfolder prefix |

## Enum Values

### OutputChannels

| Member | Value | Label |
|--------|-------|-------|
| `RGB` | 0 | `"RGB"` |
| `RGBA` | 1 | `"RGB + Alpha"` |
| `ALPHA` | 2 | `"Alpha"` |

### OutputColorDepth

| Member | Value | Label |
|--------|-------|-------|
| `FLOATING_POINT_GRAY` | -32 | `"Floating Point Gray"` |
| `COLORS_256` | 8 | `"256 Colors"` |
| `MILLIONS_OF_COLORS` | 24 | `"Millions of Colors"` |
| `MILLIONS_OF_COLORS_PLUS` | 32 | `"Millions of Colors+"` |
| `GRAYS_256` | 40 | `"256 Grays"` |
| `TRILLIONS_OF_COLORS` | 48 | `"Trillions of Colors"` |
| `TRILLIONS_OF_COLORS_PLUS` | 64 | `"Trillions of Colors+"` |
| `FLOATING_POINT` | 96 | `"Floating Point"` |
| `FLOATING_POINT_PLUS` | 128 | `"Floating Point+"` |

### OutputColorMode

| Member | Value | Label |
|--------|-------|-------|
| `STRAIGHT_UNMATTED` | 0 | `"Straight (Unmatted)"` |
| `PREMULTIPLIED` | 1 | `"Premultiplied (Matted)"` |

### OutputAudio

| Member | Value | Label |
|--------|-------|-------|
| `OFF` | 1 | `"Off"` |
| `ON` | 2 | `"On"` |
| `AUTO` | 3 | `"Auto"` |

### OutputFormat

| Member | Value | Label |
|--------|-------|-------|
| `AIFF` | 0 | `"AIFF"` |
| `AVI` | 1 | `"AVI"` |
| `DPX_CINEON_SEQUENCE` | 2 | `"DPX/Cineon Sequence"` |
| `H264` | 3 | `"H.264"` |
| `IFF_SEQUENCE` | 4 | `"IFF Sequence"` |
| `JPEG_SEQUENCE` | 5 | `"JPEG Sequence"` |
| `MP3` | 6 | `"MP3"` |
| `OPENEXR_SEQUENCE` | 7 | `"OpenEXR Sequence"` |
| `PNG_SEQUENCE` | 8 | `"PNG Sequence"` |
| `PHOTOSHOP_SEQUENCE` | 9 | `"Photoshop Sequence"` |
| `QUICKTIME` | 10 | `"QuickTime"` |
| `RADIANCE_SEQUENCE` | 11 | `"Radiance Sequence"` |
| `SGI_SEQUENCE` | 12 | `"SGI Sequence"` |
| `TIFF_SEQUENCE` | 13 | `"TIFF Sequence"` |
| `TARGA_SEQUENCE` | 14 | `"Targa Sequence"` |
| `WAV` | 15 | `"WAV"` |

### AudioBitDepth

| Member | Value | Label |
|--------|-------|-------|
| `EIGHT_BIT` | 1 | `"8 Bit"` |
| `SIXTEEN_BIT` | 2 | `"16 Bit"` |
| `TWENTY_FOUR_BIT` | 3 | `"24 Bit"` |
| `THIRTY_TWO_BIT` | 4 | `"32 Bit"` |

### AudioChannels

| Member | Value | Label |
|--------|-------|-------|
| `MONO` | 1 | `"Mono"` |
| `STEREO` | 2 | `"Stereo"` |

### AudioSampleRate

| Member | Value | Label |
|--------|-------|-------|
| `OFF` | 0 | `""` |
| `RATE_8000` | 8000 | `"8.000 kHz"` |
| `RATE_11025` | 11025 | `"11.025 kHz"` |
| `RATE_16000` | 16000 | `"16.000 kHz"` |
| `RATE_22050` | 22050 | `"22.050 kHz"` |
| `RATE_24000` | 24000 | `"24.000 kHz"` |
| `RATE_32000` | 32000 | `"32.000 kHz"` |
| `RATE_44100` | 44100 | `"44.100 kHz"` |
| `RATE_48000` | 48000 | `"48.000 kHz"` |
| `RATE_88200` | 88200 | `"88.200 kHz"` |
| `RATE_96000` | 96000 | `"96.000 kHz"` |

### PostRenderAction

| Member | Value | Label |
|--------|-------|-------|
| `NONE` | 3612 | `"None"` |
| `IMPORT` | 3613 | `"Import"` |
| `IMPORT_AND_REPLACE_USAGE` | 3614 | `"Import & Replace Usage"` |
| `SET_PROXY` | 3615 | `"Set Proxy"` |

### ResizeQuality

| Member | Value | Label |
|--------|-------|-------|
| `LOW` | 0 | `"Low"` |
| `HIGH` | 1 | `"High"` |
