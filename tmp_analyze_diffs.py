"""Analyze all validation diffs for samples/bugs/29.97_fps_time_scale_3.125.aep."""
from __future__ import annotations

import re
from collections import Counter

from aep_parser.cli.validate import main as validate_main

# Monkey-patch to capture all diffs
import aep_parser.cli.validate as validate_mod

# Read the source to understand validate internals
from pathlib import Path
import json
from aep_parser import parse

aep_path = Path("samples/bugs/29.97_fps_time_scale_3.125.aep")
json_path = Path("samples/bugs/29.97_fps_time_scale_3.125.json")

# Run validate with full output
import sys
from io import StringIO

# Patch the print limit
original_code = validate_mod.__file__

# Just run it and capture - but we need all diffs
# Let's temporarily patch the limit
old_main = validate_mod.main

# Instead, let's just call the comparison functions directly
app = parse(aep_path)

with open(json_path, "r", encoding="utf-8") as f:
    expected = json.load(f)

# Collect all diffs by running validate with a patched print
all_lines = []
original_print = print

def capturing_print(*args, **kwargs):
    msg = " ".join(str(a) for a in args)
    all_lines.append(msg)
    original_print(*args, **kwargs)

import builtins
old_print = builtins.print
builtins.print = capturing_print

try:
    validate_main(["samples/bugs/29.97_fps_time_scale_3.125.aep",
                    "samples/bugs/29.97_fps_time_scale_3.125.json",
                    "-v"])
except SystemExit:
    pass

builtins.print = old_print

# Now extract diff lines
diff_lines = [l.strip() for l in all_lines if ": expected " in l and "got " in l]

print(f"\n{'='*80}")
print(f"TOTAL DIFF LINES CAPTURED: {len(diff_lines)}")
print(f"{'='*80}\n")

# Categorize diffs
categories = Counter()
for line in diff_lines:
    if ".isModified:" in line:
        categories["isModified (expected False, got True)"] += 1
    elif "expected 'exists', got 'missing'" in line:
        categories["missing property"] += 1
    elif ".numProperties:" in line:
        categories["numProperties mismatch"] += 1
    elif ".value:" in line:
        categories["value mismatch"] += 1
    elif ".minValue:" in line:
        categories["minValue mismatch"] += 1
    elif ".maxValue:" in line:
        categories["maxValue mismatch"] += 1
    else:
        categories["other: " + line.split(":")[-2].strip() if ":" in line else "unknown"] += 1

print("DIFF CATEGORIES:")
for cat, count in categories.most_common():
    print(f"  {cat}: {count}")

# Print unique diff patterns (deduplicate by removing comp/layer indices)
print(f"\n{'='*80}")
print("UNIQUE DIFF PATTERNS (normalized):")
print(f"{'='*80}\n")
patterns = set()
for line in diff_lines:
    # Normalize: remove comp names, layer indices
    normalized = re.sub(r'Comp\[[^\]]+\]', 'Comp[*]', line)
    normalized = re.sub(r'layers\[\d+\]', 'layers[*]', normalized)
    patterns.add(normalized)

for p in sorted(patterns):
    print(f"  {p}")
