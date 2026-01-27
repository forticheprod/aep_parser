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

# Run tests with coverage (configured in pyproject.toml)
pytest

# Type checking
mypy src/aep_parser

# Linting (excludes auto-generated kaitai/aep.py)
ruff check src/
ruff format src/
```

## Code Conventions

### Type Hints
- All functions require type hints (`disallow_untyped_defs = true`)
- Use `from __future__ import annotations` for Python 3.7+ compatibility
- Conditional imports for TYPE_CHECKING to avoid circular imports

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
4. Do not add tests, it will come later.

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
- Do not add tests for now, they will be added later.

## Regenerating Kaitai Parser
When modifying `aep.ksy`, regenerate the Python parser:
```powershell
kaitai-struct-compiler --target python --outdir src/aep_parser/kaitai src/aep_parser/kaitai/aep.ksy
```
Then manually optimize the generated `aep.py`: replace large `if/elif/else` blocks with `try: dict[key]; except KeyError: default_value` pattern for better performance (see `_ON_TO_KAITAISTRUCT_TYPE` for example).

## Important Notes
- `kaitai/aep.py` is **auto-generated** - edit `aep.ksy` and regenerate (see above)
- Python 3.7+ compatibility required (no walrus operator, no match case, use union types via annotations)
- Model docstrings should reference equivalent After Effects ExtendScript properties from [After Effects Scripting Guide](https://ae-scripting.docsforadobe.dev/).
