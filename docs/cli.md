# Command Line Tools

py_aep provides three command-line utilities for working with After Effects project files. These tools are installed automatically when you install the package.

## Installation

All CLI tools are available after installing py_aep:

=== "uv"

    ```bash
    uv sync --extra dev
    ```

=== "pip"

    ```bash
    pip install py_aep
    ```

---

## aep-validate

Compares parsed AEP values against expected JSON values (from ExtendScript export) to validate parsing correctness.

### Usage

```bash
aep-validate project.aep expected.json
aep-validate project.aep expected.json --verbose
aep-validate project.aep expected.json --category layers
```

### Arguments

| Argument | Description |
|----------|-------------|
| `aep_file` | Path to the .aep file to parse |
| `json_file` | Path to the expected JSON file (exported from ExtendScript) |

### Options

| Option | Description |
|--------|-------------|
| `--verbose`, `-v` | Show all differences in detail |
| `--category`, `-c` | Filter results by category: `project`, `composition`, `layers`, `markers`, `folders`, `renderqueue` |

### Example

```bash
# Basic validation
aep-validate my_project.aep expected_output.json

# Verbose output showing all differences
aep-validate my_project.aep expected_output.json --verbose

# Only show layer-related differences
aep-validate my_project.aep expected_output.json --category layers

# Only show render queue differences
aep-validate my_project.aep expected_output.json --category renderqueue
```

### Output

The tool reports:

- ✓ Number of matching values
- ✗ Number of mismatches with details
- Differences categorized by type (project, composition, layers, markers, folders, renderqueue)

---

## aep-compare

Inspects and compares After Effects project files (.aep) at the binary chunk level. Supports four modes:

- **Compare** - diff two files byte-by-byte
- **Multi** - diff three or more files simultaneously (first file is the reference)
- **List** - print a tree of all chunks and their sizes in a single file
- **Dump** - hex-dump a specific chunk from a single file

### Usage

```bash
# Two-file comparison
aep-compare file1.aep file2.aep

# Multi-file comparison (first file = reference)
aep-compare ref.aep v1.aep v2.aep v3.aep

# List all chunks in a file
aep-compare file.aep --list

# Hex-dump a specific chunk
aep-compare file.aep --dump "LIST:Fold/ftts"

# Show surrounding bytes around each difference
aep-compare file1.aep file2.aep --context 4
```

### Arguments

| Argument | Description |
|----------|-------------|
| `files` | One or more .aep files. Use one file with `--list` or `--dump`; two or more for comparison (three or more triggers multi-file mode with the first file as reference) |

### Options

| Option | Description |
|--------|-------------|
| `--list` | Print a tree of all chunk paths and sizes from a single file |
| `--dump PATH` | Hex-dump the chunk at the given path (e.g. `LIST:Fold/ftts`). Accepts partial paths when unambiguous |
| `--context N` | Show `N` surrounding bytes on either side of each differing byte |
| `--json` | Output differences in JSON format (two-file mode only) |
| `--filter` | Filter results by chunk path pattern (case-insensitive, e.g., `ldta`, `LIST:Layr`) |

### Examples

```bash
# Compare two AEP files
aep-compare original.aep modified.aep

# Multi-file comparison against a reference
aep-compare baseline.aep with_blur.aep with_glow.aep with_both.aep

# Export two-file diff as JSON
aep-compare original.aep modified.aep --json > diff.json

# Only show differences in layer data chunks
aep-compare original.aep modified.aep --filter ldta

# Filter by LIST chunk type
aep-compare original.aep modified.aep --filter "LIST:Layr"

# Show 4 bytes of context around each difference
aep-compare original.aep modified.aep --context 4

# Combine context and filter for focused investigation
aep-compare original.aep modified.aep --filter ldta --context 2

# List all chunks in a file to find paths for --dump
aep-compare my_project.aep --list

# Hex-dump a specific chunk for byte-level inspection
aep-compare my_project.aep --dump "LIST:Fold/ftts"

# Partial path matching (dumps all matching chunks if unambiguous)
aep-compare my_project.aep --dump "cdta"
```

### Output

#### Two-file comparison

Reports for each differing chunk:

- **Chunk path**: Hierarchical location in the file structure
- **Byte offset**: Position within the chunk (decimal and hex)
- **Hex values**: Side-by-side comparison with binary representation
- **Bit position**: If only one bit differs, shows which bit (7 to 0, left to right)

```
[LIST:Fold/LIST:Layr/ldta]
  Offset   38 (0x0026): 0x00 (00000000) vs 0x01 (00000001), bit 0
  Offset   42 (0x002A): 0x64 (01100100) vs 0x32 (00110010)
```

With `--context 2`, surrounding bytes are shown for each difference:

```
  Offset   38 (0x0026): 0x00 (00000000) vs 0x01 (00000001), bit 0
    File 1:  64  00 [00] 00  00
    File 2:  64  00 [01] 00  00
```

#### Multi-file comparison

All file values are shown side by side separated by `|`:

```
[LIST:Fold/LIST:Layr/ldta]
  Offset   38 (0x0026): 0x00 (00000000) | 0x01 (00000001) | 0x01 (00000001), bit 0
```

Missing chunks (not present in every file) are listed with which files contain them.

#### `--list` output

Prints a chunk tree with sizes for every leaf chunk:

```
Chunk tree: my_project.aep

LIST:RIFX/
  LIST:Fold/
    hdta (112B)
    ftts (4B)
    LIST:Item/
      cdta (52B)
      ...
```

#### `--dump` output

Hex dump with offset, hex bytes, and ASCII representation:

```
[LIST:Fold/ftts] (4 bytes)

0000: A6 00 00 00                                       ....
```

---

## aep-visualize

Visualizes an After Effects project structure in various output formats.

### Usage

```bash
aep-visualize project.aep
aep-visualize project.aep --format dot > project.dot
aep-visualize project.aep --format mermaid
aep-visualize project.aep --depth 2
aep-visualize project.aep --no-properties
```

### Arguments

| Argument | Description |
|----------|-------------|
| `aep_file` | Path to the .aep file to visualize |

### Options

| Option | Description |
|--------|-------------|
| `--format`, `-f` | Output format: `text` (default), `dot`, `mermaid`, `json` |
| `--depth`, `-d` | Maximum depth to traverse (default: unlimited) |
| `--no-properties` | Exclude property details from output |
| `--output`, `-o` | Output file (default: stdout) |

### Output Formats

#### Text (default)
ASCII tree representation in the terminal:

```
📦 my_project.aep {'ae_version': '25.2x26', 'bits_per_channel': 'BPC_8', 'frame_rate': 30.0}
├── 🎬 Comp 1 {'size': '1920x1080', 'duration': '10.00s', 'frame_rate': 30.0, 'layers_count': 2}
│   ├── 📄 Background {'type': 'SOLID'}
│   │   └── 🔄 Transform {'properties': 5}
│   └── 📄 Text Layer {'type': 'TEXT'}
├── 🎞️ image.png {'asset_type': 'image', 'size': '1920x1080'}
└── 🎯 Render Queue {'items': 1}
    └── 📋 Item 1 {'output_modules': 1, 'comp': 'Comp 1'}
        └── 💾 Output Module {'file': 'output.mov', 'template': 'Lossless'}
```

The visualization includes:

- **📦 Project**: Root project with version and settings
- **📁 Folder**: Folder items containing other items
- **🎬 Composition**: Compositions with layers
- **🎞️ Footage**: Footage items (images, video, solids)
- **📄 Layer**: Layers within compositions
- **🔄 Transform**: Transform property groups
- **📂 PropertyGroup**: Property groups (effects, text properties)
- **⚙️ Property**: Individual properties
- **🎯 RenderQueue**: Render queue (if items present)
- **📋 RenderQueueItem**: Individual render queue items
- **💾 OutputModule**: Output module settings

#### DOT (Graphviz)
Generate DOT format for rendering with Graphviz:

```bash
aep-visualize project.aep --format dot > project.dot
dot -Tpng project.dot -o project.png
```

#### Mermaid
Generate Mermaid flowchart syntax for embedding in Markdown:

```bash
aep-visualize project.aep --format mermaid
```

Output can be embedded in GitHub README or documentation:

````markdown
```mermaid
flowchart TD
    A[Project] --> B[Comp 1]
    B --> C[Layer 1]
    B --> D[Layer 2]
```
````

#### JSON
Structured JSON output for custom processing:

```bash
aep-visualize project.aep --format json | python process.py
```

### Examples

```bash
# Quick overview of project structure
aep-visualize my_project.aep

# Generate PNG diagram
aep-visualize my_project.aep --format dot | dot -Tpng -o structure.png

# Shallow view (only top-level items)
aep-visualize my_project.aep --depth 1

# Structure only, no property details
aep-visualize my_project.aep --no-properties

# Save Mermaid diagram to file
aep-visualize my_project.aep --format mermaid --output diagram.md
```

---

## Common Use Cases

### Debugging Parse Differences

When developing or troubleshooting the parser:

```bash
# Create reference JSON using scripts/jsx/export_project_json.jsx, then validate
aep-validate test_project.aep reference.json --verbose
```

### Reverse Engineering Binary Format

When investigating unknown binary fields:

```bash
# Explore chunk structure before diffing
aep-compare baseline.aep --list

# Inspect raw bytes of a specific chunk
aep-compare baseline.aep --dump "LIST:Fold/LIST:Layr/ldta"

# Compare two files with known single difference
aep-compare baseline.aep with_auto_orient.aep --filter ldta

# Show surrounding bytes for context around each changed byte
aep-compare baseline.aep with_auto_orient.aep --filter ldta --context 4

# Multi-file comparison to isolate which values different settings produce
aep-compare baseline.aep setting_a.aep setting_b.aep --filter ldta
```

### Documentation Generation

Generate project structure diagrams for documentation or debugging

```bash
# Mermaid for GitHub/GitLab
aep-visualize project.aep --format mermaid > docs/structure.md

# PNG for general documentation
aep-visualize project.aep --format dot | dot -Tpng -o docs/structure.png
```
