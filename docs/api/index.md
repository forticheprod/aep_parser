# API Reference

Welcome to the AEP Parser API reference. This section provides detailed documentation for all modules, classes, and functions in the library.

## Main Entry Point

The primary function you'll use is:

::: aep_parser.parsers.project.parse_project

## Core Modules

### [Project](project.md)
The main `Project` dataclass containing all project information.

### Items
Project items represent different types of content in the project panel:

- [Base Item](items/item.md) - Base class for all items
- [Composition](items/composition.md) - Composition items
- [Footage](items/footage.md) - Footage items
- [Folder](items/folder.md) - Folder items

### Layers
Layers are the building blocks of compositions:

- [Base Layer](layers/layer.md) - Base class for all layers
- [AV Layer](layers/av_layer.md) - Audio/Video layers
- [Text Layer](layers/text_layer.md) - Text layers
- [Shape Layer](layers/shape_layer.md) - Shape layers
- [Camera Layer](layers/camera_layer.md) - Camera layers
- [Light Layer](layers/light_layer.md) - Light layers

### Properties
Properties control layer appearance and behavior:

- [Property](properties/property.md) - Individual properties
- [Property Group](properties/property_group.md) - Property containers
- [Keyframe](properties/keyframe.md) - Animation keyframes
- [Marker](properties/marker.md) - Timeline markers

### Sources
Sources provide the content for footage items:

- [File Source](sources/file_source.md) - File-based sources
- [Solid Source](sources/solid_source.md) - Solid color sources
- [Placeholder Source](sources/placeholder_source.md) - Placeholder sources

### [Enums](enums.md)
Enumerations for various After Effects settings and modes.

### [Parsers](parsers.md)
Internal parsing functions for converting binary data to Python objects.

## Quick Example

```python
from aep_parser import parse_project

# Parse a project
project = parse_project("myproject.aep")

# Access compositions
for item in project:
    if hasattr(item, 'layers'):  # It's a CompItem
        print(f"Composition: {item.name}")
        for layer in item:
            print(f"  Layer: {layer.name}")
```
