# Output Module Settings

Output module settings are stored as a `dict[str, Any]` on the `OutputModule.settings` attribute, with ExtendScript-compatible keys matching the format from `OutputModule.getSettings(GetSettingsFormat.NUMBER)`.

## Available Keys

| Key | Type | Description |
|-----|------|-------------|
| `"Video Output"` | `bool` | Whether video output is enabled |
| `"Output Audio"` | `bool` | Whether audio output is enabled |
| `"Video Codec"` | `str | None` | Video codec four-character code (e.g., "avc1", "ap4h") |
| `"Width"` | `int` | Output width in pixels |
| `"Height"` | `int` | Output height in pixels |
| `"Color"` | `OutputColorMode` | Color mode (straight or premultiplied alpha) |
| `"Audio Bit Depth"` | `AudioBitDepth` | Audio bit depth |
| `"Audio Channels"` | `AudioChannels` | Audio channel configuration |
| `"Frame Rate"` | `float` | Output frame rate |
| `"Crop Top"` | `int` | Crop pixels from the top |
| `"Crop Left"` | `int` | Crop pixels from the left |
| `"Crop Bottom"` | `int` | Crop pixels from the bottom |
| `"Crop Right"` | `int` | Crop pixels from the right |

## Enumerations

Some values use enums from `aep_parser.models.enums`. See the [Enums](../enums.md) page for full documentation:

- [`OutputColorMode`](../enums.md#aep_parser.models.enums.OutputColorMode)
- [`AudioBitDepth`](../enums.md#aep_parser.models.enums.AudioBitDepth)
- [`AudioChannels`](../enums.md#aep_parser.models.enums.AudioChannels)

## Example Usage

```python
from aep_parser import parse_project

project = parse_project("project.aep")
for rq_item in project.render_queue.items:
    for output_module in rq_item.output_modules:
        settings = output_module.settings
        print(f"Video Output: {settings['Video Output']}")
        print(f"Video Codec: {settings['Video Codec']}")
        print(f"Dimensions: {settings['Width']}x{settings['Height']}")
        print(f"Color Mode: {settings['Color'].name}")
        print(f"Output Frame Rate: {settings['Frame Rate']}")
```
