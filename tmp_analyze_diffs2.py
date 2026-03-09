"""Analyze all validation diffs for samples/bugs/29.97_fps_time_scale_3.125.aep."""
from __future__ import annotations

import re
import json
from collections import Counter
from pathlib import Path

from aep_parser import parse
from aep_parser.cli.validate import validate_aep

aep_path = Path("samples/bugs/29.97_fps_time_scale_3.125.aep")
json_path = Path("samples/bugs/29.97_fps_time_scale_3.125.json")

result = validate_aep(aep_path, json_path, verbose=False)

print(f"TOTAL DIFFERENCES: {len(result.differences)}")
print(f"\nBy category: {result.categories}")

# Normalize and deduplicate
patterns = set()
for line in result.differences:
    normalized = re.sub(r'Comp\[[^\]]+\]', 'Comp[*]', line)
    normalized = re.sub(r'layers\[\d+\]', 'layers[*]', normalized)
    patterns.add(normalized)

print(f"\nUNIQUE PATTERNS ({len(patterns)}):")
print("=" * 80)
for p in sorted(patterns):
    print(f"  {p}")

# Count by pattern
pattern_counts = Counter()
for line in result.differences:
    normalized = re.sub(r'Comp\[[^\]]+\]', 'Comp[*]', line)
    normalized = re.sub(r'layers\[\d+\]', 'layers[*]', normalized)
    pattern_counts[normalized] += 1

print(f"\n\nPATTERN COUNTS (sorted by frequency):")
print("=" * 80)
for pattern, count in pattern_counts.most_common():
    print(f"  [{count:3d}x] {pattern}")

# Also categorize by issue type
print(f"\n\nISSUE TYPES:")
print("=" * 80)
issue_types = Counter()
for line in result.differences:
    if ".isModified:" in line:
        issue_types["isModified wrong (expected False got True)"] += 1
    elif "expected 'exists', got 'missing'" in line:
        # Extract what's missing
        match = re.search(r'\.([^.]+): expected', line)
        prop_name = match.group(1) if match else "unknown"
        issue_types[f"missing property: {prop_name}"] += 1
    elif ".numProperties:" in line:
        issue_types["numProperties mismatch"] += 1
    elif ".value:" in line:
        issue_types["value mismatch"] += 1
    elif ".minValue:" in line:
        issue_types["minValue mismatch"] += 1
    elif ".maxValue:" in line:
        issue_types["maxValue mismatch"] += 1
    else:
        issue_types[f"other: {line}"] += 1

for itype, count in issue_types.most_common():
    print(f"  [{count:3d}x] {itype}")
