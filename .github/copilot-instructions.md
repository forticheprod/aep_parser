# AEP Parser - AI Coding Agent Instructions

## Project Overview
A Python library for parsing Adobe After Effects project files (.aep). The binary RIFX format is decoded using [Kaitai Struct](https://kaitai.io/), then transformed into typed Python dataclasses representing the AE object model (Project → Items → Layers → Properties).

## Architecture

### Data Flow
```
.aep file → Kaitai (kaitai/aep.ksy) → Raw chunks → Parsers → Model dataclasses
```

### Key Directories
- **`src/aep_parser/kaitai/`** - Binary parsing layer
  - `aep.ksy` - Kaitai schema defining RIFX chunk structure (auto-generates `aep.py`)
  - `utils.py` - Chunk filtering helpers (`find_by_type`, `filter_by_list_type`)
- **`src/aep_parser/parsers/`** - Transform raw chunks into models
  - Entry point: `project.py::parse_project()` 
  - Pattern: Each parser receives chunks + context, returns a model instance
- **`src/aep_parser/models/`** - Typed dataclasses mirroring AE's object model
  - `items/` - Project items (CompItem, FootageItem, Folder)
  - `layers/` - Layer types (AVLayer, Layer base class)
  - `properties/` - Effects and animation properties (Property, PropertyGroup, Keyframe, Marker)
  - `sources/` - Footage sources (FileSource, SolidSource, PlaceholderSource)
- **`src/aep_parser/cos/`** - COS (PDF) format parser for embedded data in text properties (from python-lottie)
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
mkdocs serve
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
       child_chunks = chunk.data.chunks
       data_chunk = find_by_type(chunks=child_chunks, chunk_type="xxxx")
       return ThingModel(field=data_chunk.data.field)
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
```

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

## Important Notes
- `kaitai/aep.py` is **auto-generated** - edit `aep.ksy` and regenerate (see above)
- `kaitai/aep_optimized.py` applies performance optimizations via monkey-patching
- Python 3.7+ compatibility required (no walrus operator, no match case, use union types via annotations)
- Model docstrings should reference equivalent After Effects ExtendScript properties from [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/).

## Documentation

### Overview
The project uses **MkDocs with Material theme** to auto-generate API documentation from Python docstrings. Documentation is automatically deployed to GitHub Pages on push/merge to `main` branch.

- **Live site**: https://forticheprod.github.io/aep_parser/
- **Theme**: Material for MkDocs with dark mode (supports light/dark/auto toggle)
- **Auto-generation**: mkdocstrings extracts API docs from docstrings with full type hint support

### Documentation Structure
```
docs/
├── index.md              # Overview, installation, quick start
├── api/                  # Auto-generated API reference
│   ├── index.md          # API overview with parse_project() entry point
│   ├── project.md        # Project dataclass
│   ├── items/            # CompItem, FootageItem, Folder
│   ├── layers/           # AVLayer, TextLayer, ShapeLayer, etc.
│   ├── properties/       # Property, PropertyGroup, Keyframe, Marker
│   ├── sources/          # FileSource, SolidSource, PlaceholderSource
│   ├── enums.md          # All enumerations
│   └── parsers.md        # Internal parsing functions
└── guides/
    └── flags_tutorial.md # Binary format debugging guide
```

### Building Documentation Locally
```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build static site (output to site/)
mkdocs build --strict

# Serve with live reload at http://127.0.0.1:8000
mkdocs serve
```

### Docstring Requirements
For proper documentation generation, all public classes, methods, and functions should have docstrings:

```python
def parse_thing(chunk: Aep.Chunk, context: Context) -> ThingModel:
    """Parse a Thing from AEP chunk data.
    
    Args:
        chunk: The RIFX chunk containing Thing data.
        context: Parsing context with shared state.
    
    Returns:
        A ThingModel instance with parsed data.
    """
    # implementation
```

**Key points**:
- Use Google-style docstrings (the default for mkdocstrings)
- Include type hints in function signatures (displayed automatically)
- Reference AE ExtendScript properties in attribute descriptions
- Type hints are automatically extracted and displayed with cross-references

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
4. Build and verify: `mkdocs serve`

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
- `mkdocstrings[python]>=0.24.0` - Auto-generates API docs from docstrings with type hint support
