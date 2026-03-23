# AEP Parser Documentation

Welcome to the AEP Parser documentation! This library provides a Python interface for parsing Adobe After Effects project files (.aep).

## About

AEP Parser is a Python library that parses Adobe After Effects project files (.aep), which are binary files encoded in RIFX format. The library uses [Kaitai Struct](https://kaitai.io/) to parse the binary format and provides a clean, typed Python API to access project data.

## Installation

=== "uv"

    ```bash
    uv add aep-parser
    ```

=== "pip"

    ```bash
    pip install aep-parser
    ```

## Quick Start

```python
import aep_parser

# Parse an After Effects project file
app = aep_parser.parse("path/to/your/project.aep")
project = app.project

# Access application-level information
print(f"AE Version: {app.version}")

# Access project information
print(f"Frame Rate: {project.bits_per_channel}")
print(f"Bits per Channel: {project.bits_per_channel}")

# Access project items
for item in project:
    print(f"Item: {item.name} ({type(item).__name__})")
```

## Features

- **Full Project Parsing**: Parse complete After Effects projects including compositions, footage, layers, and effects
- **Render Queue**: Access render queue items, render settings, and output module configurations
- **Type Safety**: Fully typed Python dataclasses for all AE objects
- **Comprehensive**: Support for layers, properties, effects, keyframes, markers, and more
- **Python 3.7+**: Compatible with Python 3.7 and above

## Key Concepts

### Project Structure

An After Effects project has a hierarchical structure:

```
Application
├── Viewer
│   └── View
│       └── ViewOptions
└── Project
    ├── FolderItem
    │   ├── CompItem
    │   │   ├── AVLayer ──────────┐
    │   │   ├── TextLayer ────────┤
    │   │   ├── ShapeLayer ───────┤
    │   │   ├── ThreeDModelLayer ─┤
    │   │   ├── CameraLayer ──────┤
    │   │   └── LightLayer ───────┘──▶ PropertyGroup
    │   │                              ├── Property
    │   │                              │   ├── Keyframe
    │   │                              │   │   └── KeyframeEase
    │   │                              │   ├── MarkerValue
    │   │                              │   └── Shape
    │   │                              │       └── FeatherPoint
    │   │                              ├── MaskPropertyGroup
    │   │                              └── PropertyGroup (nested)
    │   └── FootageItem
    │       ├── FileSource
    │       ├── SolidSource
    │       └── PlaceholderSource
    ├── TextDocument
    │   └── FontObject
    └── RenderQueue
        └── RenderQueueItem
            └── OutputModule
```

### Data Model

The library provides classes that mirror After Effects' object model:

- `Application`: Application-level object (version, build number, active viewer)
- `Viewer`, `View`, `ViewOptions`: Viewer panels and view settings
- `Project`: Root project object
- `Item`, `AVItem`, `FolderItem`, `CompItem`, `FootageItem`: Project items
- `AVLayer`, `TextLayer`, `ShapeLayer`, `ThreeDModelLayer`, `CameraLayer`, `LightLayer`: Layer types
- `PropertyBase`, `Property`, `PropertyGroup`, `MaskPropertyGroup`: Layer properties
- `Keyframe`, `KeyframeEase`, `MarkerValue`, `Shape`, `FeatherPoint`: Animation and property value data
- `FootageSource`, `FileSource`, `SolidSource`, `PlaceholderSource`: Footage sources
- `TextDocument`, `FontObject`: Text layer data
- `RenderQueue`, `RenderQueueItem`, `OutputModule`: Render queue

## API Reference

Browse the [API Reference](api/index.md) for detailed documentation of all classes and methods.

## Contributing

Contributions are welcome! See the [Contributing Guide](contributing.md) to get started, or visit the [GitHub repository](https://github.com/forticheprod/aep_parser) for more information.

## License

This project is licensed under the MIT License.
