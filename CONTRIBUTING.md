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
- `items/` - CompItem, FootageItem, FolderItem
- `layers/` - Layer types (AVLayer, TextLayer, ShapeLayer, etc.)
- `properties/` - Effects and animation (Property, PropertyGroup, Keyframe, MarkerValue)
- `sources/` - Footage sources (FileSource, SolidSource, PlaceholderSource)
- `renderqueue/` - Render queue (RenderQueueItem, RenderSettings, OutputModule)

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

These samples cover many attributes and are used by the test suite.

### Debugging Tips

#### Finding Chunk Types

Use `aep-visualize` to see the parsed project as a DAG:

```bash
aep-visualize samples/models/composition/bgColor_custom.aep --depth 3
```

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
- id: data
  type:
    switch-on: chunk_type
    cases:
      '"cdta"': chunk_cdta
      '"xxxx"': chunk_xxxx  # Add new chunk type
```

#### 3. Regenerate Kaitai Parser

```bash
kaitai-struct-compiler --target python \
  --outdir src/aep_parser/kaitai \
  src/aep_parser/kaitai/aep.ksy
```

> **⚠️ Integer division pitfall:** In Kaitai Struct, `/` between two integers
> compiles to Python's `//` (floor division). To get true (float) division,
> multiply one operand by `1.0`:
> ```yaml
> # Wrong — truncates to integer (e.g. 3 / 4 = 0)
> value: 'pixel_ratio_width / pixel_ratio_height'
> # Correct — produces float (e.g. 3 * 1.0 / 4 = 0.75)
> value: 'pixel_ratio_width * 1.0 / pixel_ratio_height'
> ```

#### 4. Update the Model

Add the attribute to the appropriate dataclass in `models/`. Use **inline docstrings** after each field:

```python
@dataclass
class CompItem(AVItem):
    """Composition item containing layers."""

    # ... existing fields ...

    shutter_angle: int
    """
    The shutter angle setting for the composition. This corresponds to the
    Shutter Angle setting in the Advanced tab of the Composition Settings
    dialog box.
    """
```

**Important**: Always add docstrings similar to the [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/). Keep docstring lines under 80 characters.

#### 5. Update the Parser

Wire the parsed data to the model in the corresponding parser:

```python
def parse_comp_item(chunk: Aep.Chunk, context: Context) -> CompItem:
    """Parse a composition item."""
    
    # Find the chunk containing your data
    cdta_chunk = find_by_type(chunks=child_chunks, chunk_type="cdta")
    
    return CompItem(
        # ... other arguments ...
        shutter_angle=cdta_chunk.shutter_angle,  # <-- Add this
    )
```

#### 6. Add Enum Mappings (only if the binary values do not match ExtendScript values)

Binary values often differ from ExtendScript API values:

1. Add the enum to `models/enums.py` (matching ExtendScript values)
2. Create `map_<name>()` function in `parsers/mappings.py`
3. Use `.get(value, default)` for unknown values

#### 7. Add Tests

Create a test in the appropriate test file:

```python
def test_comp_shutter_angle():
    """Test parsing shutter angle from composition."""
    project = parse_project("samples/models/composition/shutterAngle_180.aep")
    comp = project.items[0]
    
    assert comp.shutter_angle == 180.0
```

#### 8. Create Test Samples

Use After Effects to create test samples:

1. Create a minimal project with the attribute set to a known value
2. Save as `samples/models/<type>/<attribute>_<value>.aep`
3. Run the test to validate

Or use `generate_model_samples.jsx` to generate samples automatically.

### Adding Boolean Flags (1-bit Attributes)

Boolean flags are stored as individual bits within a byte. To add a new boolean flag:

#### 1. Find the Bit Position

Create two .aep files differing only in the boolean attribute, then compare:

```bash
aep-compare test_false.aep test_true.aep
```

Convert byte values to binary to identify the bit:

```
10 (decimal) = 00001010 (binary)
14 (decimal) = 00001110 (binary)
                    ^
                    bit 2 changed
```

#### 2. Update Kaitai Schema

Add bit fields to `aep.ksy`:

```yaml
# Read individual bits (from MSB to LSB: 7→0)
- id: preserve_nested_resolution
  type: b1  # bit 7
- type: b1  # skip bit 6
- id: motion_blur
  type: b1  # bit 5
- type: b5  # skip remaining bits
```

**Important**: All bits in a byte must be accounted for (sum to 8).

#### 3. Wire to Model

Add the attribute to the model with an inline docstring, then update the parser:

```python
# In model
motion_blur: bool
"""When True, motion blur is enabled for the composition."""

# In parser
motion_blur=flags_chunk.motion_blur,
```

### Adding a New Layer Type

To add support for a new layer type (e.g., ThreeDModelLayer):

1. **Create the model** in `models/layers/`:

```python
@dataclass
class ThreeDModelLayer(AVLayer):
    """
    The ThreeDModelLayer object represents a 3D Model layer within a composition.

    See: https://ae-scripting.docsforadobe.dev/layer/threedmodellayer/
    """

    pass
```

2. **Update the parser** in `parsers/layer.py`:

```python
def parse_layer(chunk: Aep.Chunk, context: Context) -> Layer:
    """Parse a layer from layer chunks."""
    
    # Detect layer type
    layer_type = determine_layer_type(chunk)
    
    if layer_type == "threeDLayer":
        return parse_3d_layer(chunk, context)
    # ... other layer types ...
```

3. **Add tests** in `tests/test_models_layer.py`

### Adding a New Property Type

Properties (effects, keyframes, expressions) are more complex. They may require:

1. **COS parser** (from python-lottie) for text properties
2. **Expression parsing** for expressions (if not already supported)
3. **Effect parameter parsing** for effect properties

python-lottie documentation for COS format details: [python-lottie COS documentation](https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md#list-btdk)

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
- `test_models_renderqueue.py` - Render queue, settings, output modules

### Writing Tests

Follow the existing test patterns and compare twith the JSON values whenever possible:

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
- **Imports**: Use `from __future__ import annotations` for forward references and modern type syntax
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Docstrings**: Google-style docstrings for all public functions and classes
- **Cross-references**: Use mkdocstrings syntax `[ClassName][]` or `[text][fully.qualified.path]` to link to other classes in docstrings. Do **not** use Sphinx-style `:class:` / `:func:` notation.
- **Modern types**: Use `list[int]` instead of `List[int]` (works on Python 3.7+ with annotations import)

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
mkdocs serve --strict
```

Documentation is auto-deployed to GitHub Pages when changes are pushed to `main`.

### Writing Documentation

- **API docs**: Auto-generated from docstrings using mkdocstrings

Reference the [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/) in docstrings:

```python
def parse_layer(chunk: Aep.Chunk) -> Layer:
    """Parse a layer from AEP chunk data.
    
    See: https://ae-scripting.docsforadobe.dev/layers/layer
    """
```

### Cross-Referencing in Docstrings

Use mkdocstrings [scoped cross-references](https://mkdocstrings.github.io/python/usage/configuration/docstrings/#scoped_crossrefs) to link to other classes, functions, or attributes. Do **not** use Sphinx-style `:class:`, `:func:`, or `:meth:` notation — mkdocs does not interpret it.

```python
# Short form — resolved via scoped cross-references (sibling/parent lookup)
"""The [CompItem][] that contains this layer."""

# Explicit path — for cross-module or ambiguous references
"""See [FileSource.missing_footage_path][aep_parser.models.sources.file.FileSource.missing_footage_path]."""

# ✗ Don't use Sphinx-style notation
"""Returns a :class:`CompItem` instance."""  # Wrong
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
    child_chunks = chunk.chunks
    
    # Find specific chunks
    data_chunk = find_by_type(chunks=child_chunks, chunk_type="cdta")
    name_chunk = find_by_type(chunks=child_chunks, chunk_type="tdgp")
    
    # Parse name (common pattern)
    name = name_chunk.name.decode("utf-8") if name_chunk else ""
    
    # Return model instance
    return ThingModel(
        name=name,
        some_value=data_chunk.some_value,
    )
```

## Getting Help

- **Issue tracker**: [GitHub Issues](https://github.com/forticheprod/aep_parser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/forticheprod/aep_parser/discussions)
- **After Effects Scripting**: [Official Scripting Guide](https://ae-scripting.docsforadobe.dev/)
- **Kaitai Struct**: [Documentation](https://doc.kaitai.io/)
- **python-lottie**: [python-lottie documentation](https://github.com/hunger-zh/lottie-docs/blob/main/docs/aep.md)

## See Also

- [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/) - Official AE scripting reference
- [Kaitai Struct Documentation](https://doc.kaitai.io/) - Binary format parsing
- [python-lottie](https://gitlab.com/mattbas/python-lottie) - Reference for COS format used in text properties
