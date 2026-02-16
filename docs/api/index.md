# API Reference

Welcome to the AEP Parser API reference. This section provides detailed documentation for all modules, classes, and functions in the library.

## Main Entry Point

The primary function you'll use is [`parse()`](parsers.md#main-parser).

## Core Modules

### [Parsers](parsers.md)

Internal parsing functions for converting binary data to Python objects.

### [App](app.md)

The top-level `App` dataclass representing the After Effects application.

### [Project](project.md)

The `Project` dataclass containing all project information.

### Items

Project items represent different types of content in the project panel:

- [Item](items/item.md) - Base class for all items
- [AV Item](items/av_item.md) - Base class for Audio/Video items
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

- [Property Base](properties/property_base.md) - Base class for properties
- [Property](properties/property.md) - Individual properties
- [Property Group](properties/property_group.md) - Property containers
- [Keyframe](properties/keyframe.md) - Animation keyframes
- [MarkerValue](properties/marker.md) - Timeline markers

### Sources

Sources provide the content for footage items:

- [Footage Source](sources/file_source.md) - Base class for sources
- [File Source](sources/file_source.md) - File-based sources
- [Solid Source](sources/solid_source.md) - Solid color sources
- [Placeholder Source](sources/placeholder_source.md) - Placeholder sources

### Render Queue

Render queue management and output settings:

- [Render Queue](renderqueue/render_queue.md) - The render queue container
- [Render Queue Item](renderqueue/render_queue_item.md) - Individual render items
- [Render Settings](renderqueue/render_settings.md) - Render settings reference
- [Output Module](renderqueue/output_module.md) - Output module configuration
- [Output Module Settings](renderqueue/output_module_settings.md) - Output settings reference

### [Enums](enums.md)
Enumerations for various After Effects settings and modes.

## Quick Example

```python
import aep_parser

# Parse a project
app = aep_parser.parse("myproject.aep")
project = app.project

# Access compositions
for item in project:
    if hasattr(item, 'layers'):  # It's a CompItem
        print(f"Composition: {item.name}")
        for layer in item:
            print(f"  Layer: {layer.name}")
```
