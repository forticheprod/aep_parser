# AEP Parser - AI Coding Agent Instructions

## Project Overview
A Python library for parsing Adobe After Effects project files (.aep). The binary RIFX format is decoded using [Kaitai Struct](https://kaitai.io/), then transformed into typed Python dataclasses representing the AE object model (Application > Project > Items > Layers > Properties).

## Architecture

### Data Flow
```
.aep file > Kaitai (kaitai/aep.ksy) > Raw chunks > Parsers > Model dataclasses
```

### Key Directories
- **`src/aep_parser/kaitai/`** - Binary parsing layer
  - `aep.ksy` - Kaitai schema defining RIFX chunk structure (auto-generates `aep.py`)
  - `aep_optimized.py` - Performance optimizations via monkey-patching
  - `utils.py` - Chunk filtering helpers (`find_by_type`, `filter_by_list_type`)
- **`src/aep_parser/__init__.py`** - Public API entry point: `parse()`
- **`src/aep_parser/parsers/`** - Transform raw chunks into models
  - `application.py`, `project.py`, `mappings.py`, `match_names.py`, `render_queue.py`, ...
  - Pattern: Each parser receives chunks + context, returns a model instance
- **`src/aep_parser/models/`** - Typed dataclasses mirroring AE's object model
  - `application.py`, `items/`, `layers/`, `properties/`, `sources/`, `renderqueue/`, ...
- **`src/aep_parser/enums/`** - Enumerations matching ExtendScript values (`general.py`, `property.py`, `render_settings.py`, ...)
- **`src/aep_parser/resolvers/`** - Business logic for computing derived values (e.g. `output.py` resolves render filenames, dimensions, timecodes)
- **`src/aep_parser/cli/`** - `visualize.py`, `validate.py`, `compare.py`
- **`src/aep_parser/cos/`** - COS (PDF) format parser for embedded text data
- **`scripts/`** - Dev/analysis scripts; `jsx/` has ExtendScript JSON exporters
- **`samples/`** - Test .aep files covering specific features

## Development Commands

```powershell
uv sync --extra dev                  # Install with dev dependencies
uv sync --extra docs                 # Install with docs dependencies
uv run pytest                        # Run tests (parallel)
uv run pytest --cov=src/aep_parser --cov-report html --cov-report term:skip-covered  # With coverage
uv run mypy src/aep_parser           # Type checking
uv run ruff check src/ ; uv run ruff format src/  # Linting (excludes auto-generated kaitai/aep.py)
uv run mkdocs build --strict         # Build documentation
uv run mkdocs serve --strict         # Serve documentation locally (with live reload)
```

JSX scripts run in After Effects via VS Code debugger - see `.vscode/launch.json`.

## Code Conventions

### Style Guide
- All functions require type hints (`disallow_untyped_defs = true`)
- Use `from __future__ import annotations` and modern type hints (`list[int]` not `List[int]`)
- Conditional imports for TYPE_CHECKING to avoid circular imports
- PEP8 naming: snake_case for functions/variables, PascalCase for classes
- Use `pathlib` for file paths, f-strings for formatting
- No spaces on empty lines
- **No `struct` module** - all binary decoding must be in `kaitai/aep.ksy`

### Adding New Parsed Data
1. Find/add chunk type in `kaitai/aep.ksy`
2. Create/update model dataclass in `models/` with docstrings referencing AE equivalents
3. Add parser in `parsers/`:
   ```python
   def parse_thing(chunk: Aep.Chunk, context: ...) -> ThingModel:
       data_chunk = find_by_type(chunks=chunk.data.chunks, chunk_type="xxxx")
       return ThingModel(field=data_chunk.data.field)
   ```
4. Validate parsed values against ExtendScript using `aep-validate` (see [CLI Tools](#cli-tools))
5. Add test case in `tests/test_models_*.py` using sample .aep files

### Binary Format Debugging
See `docs/flags_tutorial.md` for reverse-engineering bitflags:
```yml
- id: preserve_nested_resolution
  type: b1
- type: b1
- id: frame_blending
  type: b1
- type: b2
- id: hide_shy_layers
  type: b1
```

### Chunk Navigation Pattern
```python
from aep_parser.kaitai.utils import find_by_type, find_by_list_type, filter_by_type

ldta_chunk = find_by_type(chunks=child_chunks, chunk_type="ldta")
fold_chunk = find_by_list_type(chunks=root_chunks, list_type="Fold")
layer_chunks = filter_by_list_type(chunks=comp_chunks, list_type="Layr")
```

For debugging, `chunk_tree(chunks, depth)` prints the chunk hierarchy and `recursive_find(chunks, chunk_type, list_type)` searches the entire tree recursively.

### Chunk Data Access
Chunk attributes live on `chunk.data`, not on the chunk itself. Always use explicit `chunk.data.X` access:
```python
chunk.data.list_type     # the list_type of a LIST chunk
cdta_chunk.data.time_scale  # a typed body field
```

### Value Mapping Pattern
Binary values often differ from ExtendScript values. Single-param mappings use a `from_binary` classmethod on the enum (`enums/general.py` or relevant module):
```python
blending_mode = BlendingMode.from_binary(raw_value)
```
Multi-param mappings (e.g. `map_alpha_mode(value, has_alpha)`) go in `parsers/mappings.py`.

When adding new mappings:
1. Add enum to `enums/general.py` (matching ExtendScript values)
2. Single-param: add `from_binary(cls, value)` classmethod
3. Multi-param: create `map_<name>()` in `parsers/mappings.py`
4. Use `.get(value, default)` for unknown values

## Testing
- Tests use sample `.aep` files from `samples/`; most have a matching `.json` from ExtendScript
- Add test cases in `tests/test_models_*.py`
- **Always validate** parsed output against ExtendScript ground truth using `aep-validate` after any parsing change (see [CLI Tools](#cli-tools))
- Use `aep-compare` to investigate unknown binary fields by diffing `.aep` files that differ in a single AE setting

## Regenerating Kaitai Parser
When modifying `aep.ksy`, regenerate:
```powershell
kaitai-struct-compiler --target python --outdir src/aep_parser/kaitai src/aep_parser/kaitai/aep.ksy --read-write --no-auto-read
```
No manual edits needed after regeneration - `aep_optimized.py` applies optimizations automatically.

**Integer division pitfall:** Kaitai's `/` on two integers compiles to `//` (floor division). Multiply one operand by `1.0` for true division: `value: 'dividend * 1.0 / divisor'`.

## Important Notes
- `kaitai/aep.py` is **auto-generated** - edit `aep.ksy` and regenerate
- Run python code through a temporary file, not `python.exe -c`
- Python 3.7+ compatibility (no walrus operator, no match/case, union types via annotations)
- Model docstrings should reference [AE Scripting Guide](https://ae-scripting.docsforadobe.dev/)

## CLI Tools
Installed via `uv sync --extra dev`. Also invocable as `uv run python -m aep_parser.cli.{visualize,validate,compare}`.

- **`aep-visualize`** - Tree visualization of a parsed project
- **`aep-validate`** - Compare parsed output against ExtendScript JSON. **Use after any parsing change.**
- **`aep-compare`** - Binary chunk diff between `.aep` files. **Use to investigate unknown fields.**

```powershell
aep-visualize samples/models/composition/bgColor_custom.aep

aep-validate sample.aep sample.json
aep-validate sample.aep sample.json --verbose          # all fields
aep-validate sample.aep sample.json --category layers  # filter

aep-compare file1.aep file2.aep
aep-compare ref.aep v1.aep v2.aep v3.aep     # multi-file
aep-compare file.aep --list                  # list chunks
aep-compare file.aep --dump "LIST:Fold/ftts" # dump raw bytes
```

## Documentation
MkDocs with Material theme; auto-deployed to [GitHub Pages](https://forticheprod.github.io/aep_parser/) on push to `main`. Build locally: `mkdocs serve --strict`.

### Docstring Conventions
- **Functions**: Google-style (Args, Returns, Raises sections)
- **Dataclass fields**: inline docstrings after each field (not `Attributes:` section):
  ```python
  @dataclass
  class CompItem(AVItem):
      """Composition item containing layers."""

      frame_rate: float
      """The frame rate of the composition."""
  ```
- Copy AE ExtendScript descriptions
- Lines under 80 characters
- Use mkdocstrings [scoped cross-references](https://mkdocstrings.github.io/python/usage/configuration/docstrings/#scoped_crossrefs), **not** Sphinx `:class:`/`:func:`:
  ```python
  """The [CompItem][] that contains this layer."""                    # ✓ short
  """See [FileSource][aep_parser.models.sources.file.FileSource]."""  # ✓ explicit
  """Returns a :class:`CompItem` instance."""                         # ✗ Sphinx
  ```

### Adding Documentation Pages
1. Create markdown file in `docs/api/`
2. Reference Python objects: `::: aep_parser.models.my_module.MyClass`
3. Add to `nav:` in `mkdocs.yml`
4. Verify: `mkdocs serve --strict`
