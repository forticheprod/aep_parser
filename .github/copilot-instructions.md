# AEP Parser - AI Coding Agent Instructions

## Project Overview
A Python library for parsing Adobe After Effects project files (.aep). The binary RIFX format is decoded using [Kaitai Struct](https://kaitai.io/), then transformed into typed Python dataclasses representing the AE object model (App → Project → Items → Layers → Properties).

## Architecture

### Data Flow
```
.aep file → Kaitai (kaitai/aep.ksy) → Raw chunks → Parsers → Model dataclasses
```

### Key Directories
- **`src/aep_parser/kaitai/`** - Binary parsing layer
  - `aep.ksy` - Kaitai schema defining RIFX chunk structure (auto-generates `aep.py`)
  - `aep_optimized.py` - Performance optimizations via monkey-patching
  - `utils.py` - Chunk filtering helpers (`find_by_type`, `filter_by_list_type`)
- **`src/aep_parser/__init__.py`** - Public API entry point: `parse()`
- **`src/aep_parser/parsers/`** - Transform raw chunks into models
  - `app.py` - App-level parsing (version, viewers)
  - `project.py` - Internal project parsing (`_parse_project()`) and deprecated `parse_project()` wrapper
  - `mappings.py` - Binary value → ExtendScript enum mappings
  - `match_names.py` - Effect/property match name lookups
  - `render_queue.py` - Render queue and output module parsing
  - Pattern: Each parser receives chunks + context, returns a model instance
- **`src/aep_parser/models/`** - Typed dataclasses mirroring AE's object model
  - `app.py` - Application-level model (App)
  - `items/` - Project items (CompItem, FootageItem, FolderItem)
  - `layers/` - Layer types (AVLayer, CameraLayer, LightLayer, TextLayer, ShapeLayer)
  - `properties/` - Effects and animation properties (Property, PropertyGroup, Keyframe, MarkerValue)
  - `sources/` - Footage sources (FileSource, SolidSource, PlaceholderSource)
  - `renderqueue/` - Render queue models (RenderQueueItem, RenderSettings, OutputModule)
- **`src/aep_parser/cli/`** - Command-line tools
  - `visualize.py` - Tree visualization of parsed projects
  - `validate.py` - Validate parsed output against ExtendScript JSON
  - `compare.py` - Compare two parsed projects
- **`src/aep_parser/cos/`** - COS (PDF) format parser for embedded data in text properties (from python-lottie)
- **`scripts/`** - Development and analysis scripts
  - `jsx/` - ExtendScript files for exporting AE project data as JSON
  - Python scripts for binary format analysis and reverse engineering
- **`samples/`** - Test .aep files covering specific features

## Development Commands

```powershell
# Install with dev dependencies
pip install -e ".[dev]"

# Install with documentation dependencies
pip install -e ".[docs]"

# Run tests with coverage (configured in pyproject.toml)
pytest

# Type checking
mypy src/aep_parser

# Linting (excludes auto-generated kaitai/aep.py)
ruff check src/
ruff format src/

# Build documentation
mkdocs build --strict

# Serve documentation locally (with live reload)
mkdocs serve --strict
```

## Code Conventions

### Style Guide
- All functions require type hints (`disallow_untyped_defs = true`)
- Use `from __future__ import annotations` and modern type hints (e.g. `list[int]` instead of `List[int]`)
- Conditional imports for TYPE_CHECKING to avoid circular imports
- Follow PEP8 naming conventions (snake_case for functions/variables, PascalCase for classes)
- Use `pathlib` for file paths
- Use f-strings for formatting
- No spaces on empty lines

### Adding New Parsed Data
1. Find the chunk type in `kaitai/aep.ksy` or add new chunk definition
2. Create/update model dataclass in `models/` with docstrings explaining AE equivalents
3. Add parser function in `parsers/` following the pattern:
   ```python
   def parse_thing(chunk: Aep.Chunk, context: ...) -> ThingModel:
       data_chunk = find_by_type(chunks=chunk.chunks, chunk_type="xxxx")
       return ThingModel(field=data_chunk.field)
   ```
4. Add test case in `tests/test_models_*.py` using sample .aep files

### Binary Format Debugging
See `docs/flags_tutorial.md` for reverse-engineering bitflags:
```yml
# Pattern for boolean flags from bits
- id: preserve_nested_resolution
  type: b1  # bit 7
- type: b1  # skip bit 6
- id: preserve_nested_frame_rate
  type: b1  # bit 5
- id: frame_blending
  type: b1  # bit 4
- id: motion_blur
  type: b1  # bit 3
- type: b2  # skip bits 2-1
- id: hide_shy_layers
  type: b1  # bit 0
```

### Chunk Navigation Pattern
```python
from aep_parser.kaitai.utils import find_by_type, find_by_list_type, filter_by_type

# Find single chunk by type
ldta_chunk = find_by_type(chunks=child_chunks, chunk_type="ldta")

# Find LIST chunk by list_type
fold_chunk = find_by_list_type(chunks=root_chunks, list_type="Fold")

# Filter multiple chunks
layer_chunks = filter_by_list_type(chunks=comp_chunks, list_type="Layr")
ldta_chunks = filter_by_type(chunks=comp_chunks, chunk_type="ldta")
```

### Value Mapping Pattern
Binary values often differ from ExtendScript API values. Use mapping functions in `parsers/mappings.py` when this is the case:
```python
from aep_parser.parsers.mappings import map_blending_mode, map_layer_quality

# Map binary value to enum
blending_mode = map_blending_mode(raw_value)  # Returns BlendingMode enum
quality = map_layer_quality(raw_value)        # Returns LayerQuality enum
```

When adding new mappings:
1. Add the enum to `models/enums.py` (matching ExtendScript values)
2. Create `map_<name>()` function in `parsers/mappings.py`
3. Use `.get(value, default)` for unknown values

## Testing
- Tests use sample .aep files from `samples/` directory
- Each sample file tests a specific AE feature (markers, expressions, compositions, etc.)
- Add test case in `tests/test_models_*.py` using sample .aep files

## Regenerating Kaitai Parser
When modifying `aep.ksy`, regenerate the Python parser:
```powershell
kaitai-struct-compiler --target python --outdir src/aep_parser/kaitai src/aep_parser/kaitai/aep.ksy
```
No manual modifications are needed after regeneration. Performance optimizations (dict-based chunk type lookup) are applied automatically via the `aep_optimized.py` wrapper module.

**Integer division pitfall:** Kaitai Struct's `/` on two integers compiles to Python's `//` (floor division). Always multiply one operand by `1.0` to get true division (e.g. `value: 'dividend * 1.0 / divisor'`).

## Important Notes
- `kaitai/aep.py` is **auto-generated** - edit `aep.ksy` and regenerate (see above)
- `kaitai/aep_optimized.py` applies performance optimizations via monkey-patching
- Run python code through a temporary file, not using `python.exe -c`, to avoid issues with large code blocks, quotes, comments, ...
- Python 3.7+ compatibility required (no walrus operator, no match case, use union types via annotations)
- Model docstrings should reference equivalent After Effects ExtendScript properties from [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/).

## CLI Tools
The package includes command-line tools for development and testing:

```powershell
# Visualize parsed project as tree
python -m aep_parser.cli.visualize samples/models/composition/bgColor_custom.aep

# Validate parsed output against ExtendScript JSON export
python -m aep_parser.cli.validate samples/versions/ae2025/complete.aep samples/versions/ae2025/complete.json

# Compare two parsed projects
python -m aep_parser.cli.compare project1.aep project2.aep
```

## Documentation

### Overview
The project uses **MkDocs with Material theme** to auto-generate API documentation from Python docstrings. Documentation is automatically deployed to GitHub Pages on push/merge to `main` branch.

- **Live site**: https://forticheprod.github.io/aep_parser/
- **Theme**: Material for MkDocs with dark mode (supports light/dark/auto toggle)
- **Auto-generation**: mkdocstrings extracts API docs from docstrings and type hints

### Documentation Structure
```
docs/
├── index.md              # Overview, installation, quick start
├── api/                  # Auto-generated API reference
│   ├── index.md          # API overview with parse() entry point
│   ├── app.md            # App dataclass
│   ├── project.md        # Project dataclass
│   ├── items/            # CompItem, FootageItem, FolderItem
│   ├── layers/           # AVLayer, TextLayer, ShapeLayer, etc.
│   ├── properties/       # Property, PropertyGroup, Keyframe, MarkerValue
│   ├── sources/          # FileSource, SolidSource, PlaceholderSource
│   ├── enums.md          # All enumerations
│   └── parsers.md        # Internal parsing functions
└── contributing.md       # Links to gituhub contributing guide
```

### Building Documentation Locally
```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build static site (output to site/)
mkdocs build --strict

# Serve with live reload at http://127.0.0.1:8000
mkdocs serve --strict
```

### Docstring Requirements
For proper documentation generation, all public classes, methods, and functions should have docstrings:

```python
def parse_thing(chunk: Aep.Chunk, context: Context) -> ThingModel:
    """Parse a Thing from AEP chunk data.

    Args:
        chunk: The RIFX chunk containing Thing data.
        context: Parsing context with shared state.
    """
    # implementation
```

For dataclass attributes, use **inline docstrings** after each field instead of an `Attributes:` section:

```python
@dataclass
class CompItem(AVItem):
    """Composition item containing layers."""

    bg_color: list[float]
    """
    The background color of the composition. The three array values specify
    the red, green, and blue components of the color.
    """

    frame_rate: float
    """The frame rate of the composition."""

    layers: list[Layer]
    """All the Layer objects for layers in this composition."""
```

**Key points**:
- Use Google-style docstrings for functions (Args, Returns, Raises sections)
- Use inline docstrings after each dataclass field (mkdocstrings displays them as attribute docs)
- Include type hints in function signatures (displayed automatically)
- Reference AE ExtendScript properties in attribute descriptions
- Keep lines under 80 characters (use multi-line docstrings when needed)
- Use mkdocstrings cross-reference syntax to link to other classes; do **not** use Sphinx `:class:` / `:func:` notation (mkdocs does not interpret it)

### Cross-Referencing in Docstrings
Use [scoped cross-references](https://mkdocstrings.github.io/python/usage/configuration/docstrings/#scoped_crossrefs) (`scoped_crossrefs` and `relative_crossrefs` are enabled in `mkdocs.yml`):

```python
# Short form — resolved via scoped cross-references
"""The [CompItem][] that contains this layer."""

# Explicit path — for cross-module or ambiguous references
"""See [FileSource][aep_parser.models.sources.file.FileSource]."""

# ✗ Don't use Sphinx-style notation
"""Returns a :class:`CompItem` instance."""  # Wrong — mkdocs won't render it
```

### Documentation Configuration
Configuration in `mkdocs.yml` enables:
- **Type hint display**: `show_signature_annotations: true` - Shows all type annotations
- **Cross-references**: `signature_crossrefs: true` - Makes types clickable links
- **Source code**: `show_source: true` - Links to source code
- **Navigation**: Organized by module (Items, Layers, Properties, etc.)

### Adding New Documentation Pages
1. Create markdown file in `docs/api/` directory
2. Use mkdocstrings syntax to reference Python objects:
   ```markdown
   # My Module
   
   ::: aep_parser.models.my_module.MyClass
       options:
         show_root_heading: true
         show_source: true
   ```
3. Add page to navigation in `mkdocs.yml` under `nav:` section
4. Build and verify: `mkdocs serve --strict`

### Automatic Deployment
The `.github/workflows/docs.yml` workflow:
- Triggers on push/merge to `main` branch
- Installs dependencies with `pip install -e ".[docs]"`
- Builds documentation with `mkdocs build --strict`
- Deploys to GitHub Pages automatically
- No manual intervention required

### Documentation Dependencies
Defined in `pyproject.toml` under `[project.optional-dependencies]`:
- `mkdocs>=1.5.0` - Static site generator
- `mkdocs-material>=9.0.0` - Material theme with dark mode
- `mkdocstrings[python]>=0.24.0` - Auto-generates API docs from docstrings and type hints
