# Contributing Guide

This guide helps you understand the AEP Parser codebase and contribute new features, fixes, and improvements.

## Quick Start

1. **Fork and clone** the repository
2. **Install with dev dependencies**: `pip install -e ".[dev]"`
3. **Run tests**: `pytest`
4. **Make your changes** following this guide
5. **Submit a pull request**

## Understanding the Codebase

### Architecture Overview

AEP Parser transforms binary .aep files into typed Python objects through a three-stage pipeline:

```
.aep file → Kaitai Parser → Raw Chunks → Parsers → Model Dataclasses
```

**Stage 1: Binary Parsing (Kaitai)**
- `src/aep_parser/kaitai/aep.ksy` - Schema defining RIFX chunk structure
- `src/aep_parser/kaitai/aep.py` - Auto-generated Python parser (don't edit manually)
- `src/aep_parser/kaitai/utils.py` - Helper functions for navigating chunks

**Stage 2: Data Transformation (Parsers)**
- `src/aep_parser/parsers/` - Transform raw chunks into model instances
- Entry point: `parse_project()` in `parsers/project.py`
- Pattern: Each parser receives chunks + context, returns a model instance

**Stage 3: Data Models**
- `src/aep_parser/models/` - Typed dataclasses mirroring AE's object model
- `items/` - CompItem, FootageItem, Folder
- `layers/` - Layer types (AVLayer, TextLayer, ShapeLayer, etc.)
- `properties/` - Effects and animation (Property, PropertyGroup, Keyframe, Marker)
- `sources/` - Footage sources (FileSource, SolidSource, PlaceholderSource)

### Key Concepts

**Chunks**: AEP files use the RIFX format (big-endian RIFF). The file is a tree of "chunks" identified by 4-character types (e.g., `"cdta"`, `"ldta"`).

**LIST chunks**: Special chunks that contain other chunks. They have a `list_type` field (e.g., `"Layr"` for layers).

**Chunk navigation**: Use helper functions from `kaitai/utils.py`:
- `find_by_type()` - Find a single chunk by type
- `find_by_list_type()` - Find a LIST chunk by its list_type
- `filter_by_type()` - Get all chunks of a given type

## Development Workflow

### Setting Up Your Environment

```bash
# Clone the repository
git clone https://github.com/forticheprod/aep_parser.git
cd aep_parser

# Install with dev dependencies
pip install -e ".[dev]"

# Verify installation
pytest
mypy src/aep_parser
ruff check src/
```

### Tools and Scripts

#### Python CLI Tools

**aep-compare**: Compare two AEP files to find differences

```bash
# Basic comparison
aep-compare file1.aep file2.aep

# JSON output
aep-compare file1.aep file2.aep --json

# Filter by chunk type
aep-compare file1.aep file2.aep --filter ldta
```

**aep-visualize**: Visualize project structure

```bash
# Tree view (default)
aep-visualize project.aep

# Mermaid diagram
aep-visualize project.aep --format mermaid

# Limit depth
aep-visualize project.aep --depth 2

# Hide properties
aep-visualize project.aep --no-properties
```

#### After Effects JSX Scripts

Located in `scripts/jsx/`, these scripts help generate test samples and validate parsing:

**export_project_json.jsx**: Export AE project to JSON for testing

1. Open After Effects
2. Open your .aep file
3. File → Scripts → Run Script File → `export_project_json.jsx`
4. A `.json` file is saved next to the .aep file

This JSON serves as "ground truth" for validating the Python parser.

**generate_model_samples.jsx**: Generate comprehensive test samples

1. Open After Effects
2. Run the script
3. Select the `samples/` folder
4. Script creates one .aep file per test case

These samples cover all attributes and are used by the test suite.

### Debugging Tips

#### Finding Chunk Types

Use `aep-visualize` to explore the chunk structure:

```bash
aep-visualize samples/models/composition/bgColor_custom.aep --depth 3
```

Look for the chunk types containing your target data.

#### Comparing Files

To understand what bytes change when you modify an attribute:

1. Create a minimal .aep file
2. Save it as `before.aep`
3. Change ONE attribute in After Effects
4. Save as `after.aep`
5. Compare: `aep-compare before.aep after.aep`

#### Using the Kaitai Web IDE

The [Kaitai Struct Web IDE](https://ide.kaitai.io/) is invaluable for debugging binary formats:

1. Upload `aep.ksy` to the IDE
2. Upload your .aep file as sample data
3. Browse the parsed structure interactively
4. Identify byte positions and chunk relationships

#### Using Python REPL

Explore parsed data interactively:

```python
from aep_parser import parse_project
from aep_parser.kaitai.utils import find_by_type, filter_by_list_type

# Parse a project
project = parse_project("samples/models/composition/bgColor_custom.aep")

# Explore the data
print(project.frame_rate)
print(project.items[0].name)

# Access raw Kaitai chunks (advanced)
from aep_parser.kaitai.aep import Aep
aep_data = Aep.from_file("samples/models/composition/bgColor_custom.aep")
chunks = aep_data.rifx.chunks
```

## Adding New Features

### Adding a New Attribute

Follow this workflow to add support for a new attribute:

#### 1. Identify the Data Location

Use `aep-compare` to find where the attribute is stored:

```bash
# Create two files that differ only in the target attribute
aep-compare without_attr.aep with_attr.aep
```

Note the chunk type and byte position.

#### 2. Update Kaitai Schema (if needed)

If the chunk isn't already parsed, add it to `aep.ksy`:

```yaml
# Example: Add a new chunk type
- id: my_new_chunk
  type:
    switch-on: chunk_type
    cases:
      '"cdta"': chunk_cdta
      '"ldta"': chunk_ldta
      '"xxxx"': chunk_xxxx  # <-- Add this
```

For boolean flags, see the [Flags Tutorial](flags_tutorial.md).

#### 3. Regenerate Kaitai Parser

```bash
kaitai-struct-compiler --target python \
  --outdir src/aep_parser/kaitai \
  src/aep_parser/kaitai/aep.ksy
```

#### 4. Update the Model

Add the attribute to the appropriate dataclass in `models/`:

```python
@dataclass
class CompItem(AVItem):
    """Composition item containing layers."""
    
    # ... existing fields ...
    
    shutter_angle: float
    """Shutter angle in degrees for motion blur.
    
    Corresponds to CompItem.shutterAngle in ExtendScript.
    """
```

**Important**: Always add docstrings referencing the [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/).

#### 5. Update the Parser

Wire the parsed data to the model in the corresponding parser:

```python
def parse_comp_item(chunk: Aep.Chunk, context: Context) -> CompItem:
    """Parse a composition item."""
    
    # Find the chunk containing your data
    data_chunk = find_by_type(chunks=child_chunks, chunk_type="cdta")
    
    return CompItem(
        # ... other arguments ...
        shutter_angle=data_chunk.data.shutter_angle,  # <-- Add this
    )
```

#### 6. Add Tests

Create a test in the appropriate test file:

```python
def test_comp_shutter_angle():
    """Test parsing shutter angle from composition."""
    project = parse_project("samples/models/composition/shutterAngle_180.aep")
    comp = project.items[0]
    
    assert comp.shutter_angle == 180.0
```

#### 7. Create Test Samples

Use After Effects to create test samples:

1. Create a minimal project with the attribute set to a known value
2. Save as `samples/models/<type>/<attribute>_<value>.aep`
3. Run the test to validate

Or use `generate_model_samples.jsx` to generate samples automatically.

### Adding a New Layer Type

To add support for a new layer type (e.g., a plugin-based layer):

1. **Create the model** in `models/layers/`:

```python
@dataclass
class CustomLayer(Layer):
    """Custom layer type from a plugin."""
    
    plugin_name: str
    """Name of the plugin."""
```

2. **Update the parser** in `parsers/layer.py`:

```python
def parse_layer(chunk: Aep.Chunk, context: Context) -> Layer:
    """Parse a layer from layer chunks."""
    
    # Detect layer type
    layer_type = determine_layer_type(chunk)
    
    if layer_type == "CustomLayer":
        return parse_custom_layer(chunk, context)
    # ... other layer types ...
```

3. **Add tests** in `tests/test_models_layer.py`

### Adding a New Property Type

Properties (effects, keyframes, expressions) are more complex. They may require:

1. **COS parser** (from python-lottie) for text properties
2. **Expression parsing** for expressions (if not already supported)
3. **Effect parameter parsing** for effect properties

Reference the python-lottie documentation for COS format details: [python-lottie COS module](https://gitlab.com/mattbas/python-lottie/-/tree/master/lib/lottie/parsers/aep)

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models_layer.py

# Run specific test
pytest tests/test_models_layer.py::test_layer_motion_blur -v

# Run with coverage
pytest --cov=aep_parser --cov-report=html
```

### Test Structure

Tests are organized by model type:
- `test_models_project.py` - Project-level attributes
- `test_models_composition.py` - CompItem attributes
- `test_models_footage.py` - FootageItem and sources
- `test_models_layer.py` - Layer types and attributes
- `test_models_property.py` - Properties, keyframes, effects
- `test_models_marker.py` - Markers

### Writing Tests

Follow the existing test patterns:

```python
def test_attribute_name():
    """Test parsing <attribute> from <object>."""
    # Parse a sample project
    project = parse_project("samples/models/<type>/<attribute>_<value>.aep")
    
    # Navigate to the target object
    comp = project.items[0]
    layer = comp.layers[0]
    
    # Assert the attribute value
    assert layer.attribute_name == expected_value
```

### Creating Test Samples

Test samples should be minimal and focused:
- One .aep file per test case
- Minimal project structure (one comp, one layer if possible)
- Descriptive filename: `<attribute>_<value>.aep`
- Store in `samples/models/<type>/`

Use the JSX scripts to generate samples systematically.

## Code Style

### Python Conventions

- **Type hints**: All functions must have type hints
- **Imports**: Use `from __future__ import annotations` for forward references
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Docstrings**: Google-style docstrings for all public functions and classes
- **Modern types**: Use `list[int]` instead of `List[int]` (Python 3.9+)

### Linting and Type Checking

```bash
# Check code style
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/

# Type checking
mypy src/aep_parser
```

**Note**: `kaitai/aep.py` is auto-generated and excluded from linting.

## Documentation

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build static site
mkdocs build --strict

# Serve with live reload
mkdocs serve
```

Documentation is auto-deployed to GitHub Pages when changes are pushed to `main`.

### Writing Documentation

- **API docs**: Auto-generated from docstrings using mkdocstrings
- **Guides**: Markdown files in `docs/guides/`
- **Examples**: Include code examples in docstrings

Reference the [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/) in docstrings:

```python
def parse_layer(chunk: Aep.Chunk) -> Layer:
    """Parse a layer from AEP chunk data.
    
    Corresponds to the Layer object in the After Effects Scripting Guide:
    https://ae-scripting.docsforadobe.dev/layers/layer.html
    """
```

## Common Patterns

### Chunk Navigation

```python
from aep_parser.kaitai.utils import find_by_type, find_by_list_type, filter_by_type

# Find single chunk by type
data_chunk = find_by_type(chunks=child_chunks, chunk_type="cdta")

# Find LIST chunk by list_type
comp_chunk = find_by_list_type(chunks=root_chunks, list_type="Comp")

# Filter multiple chunks
layer_chunks = filter_by_list_type(chunks=comp_chunks, list_type="Layr")
```

### Parser Pattern

```python
def parse_thing(chunk: Aep.Chunk, context: Context) -> ThingModel:
    """Parse a Thing from AEP chunk data."""
    
    # Get child chunks
    child_chunks = chunk.data.chunks
    
    # Find specific chunks
    data_chunk = find_by_type(chunks=child_chunks, chunk_type="cdta")
    name_chunk = find_by_type(chunks=child_chunks, chunk_type="tdgp")
    
    # Parse name (common pattern)
    name = name_chunk.data.name.decode("utf-8") if name_chunk else ""
    
    # Return model instance
    return ThingModel(
        name=name,
        some_value=data_chunk.data.some_value,
    )
```

### Error Handling

```python
# Gracefully handle missing chunks
data_chunk = find_by_type(chunks=child_chunks, chunk_type="cdta")
if data_chunk:
    value = data_chunk.data.value
else:
    value = None  # or default value
```

## Getting Help

- **Issue tracker**: [GitHub Issues](https://github.com/forticheprod/aep_parser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/forticheprod/aep_parser/discussions)
- **After Effects Scripting**: [Official Scripting Guide](https://ae-scripting.docsforadobe.dev/)
- **Kaitai Struct**: [Documentation](https://doc.kaitai.io/)
- **python-lottie**: [COS parser reference](https://gitlab.com/mattbas/python-lottie/-/tree/master/lib/lottie/parsers/aep)

## See Also

- [Flags Tutorial](flags_tutorial.md) - Detailed guide for parsing boolean flags
- [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/) - Official AE scripting reference
- [Kaitai Struct Documentation](https://doc.kaitai.io/) - Binary format parsing
- [python-lottie](https://gitlab.com/mattbas/python-lottie) - Reference for COS format used in text properties
