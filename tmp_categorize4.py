"""Categorize all diffs using validate_aep directly."""
from __future__ import annotations
import re
from collections import Counter
from pathlib import Path
from aep_parser.cli.validate import validate_aep

result = validate_aep(
    Path("samples/bugs/29.97_fps_time_scale_3.125.aep"),
    Path("samples/bugs/29.97_fps_time_scale_3.125.json"),
)

print(f"Total diffs: {len(result)}")
print(f"Categories: {result.categories}")
print()

# Normalize and categorize
patterns = Counter()
examples = {}
for diff_line in result.differences:
    norm = re.sub(r'Comp\[[^\]]+\]', 'Comp[*]', diff_line)
    norm = re.sub(r'layers\[\d+\]', 'layers[N]', norm)
    norm = re.sub(r'Footage\[[^\]]+\]', 'Footage[*]', norm)
    m = re.match(r'^(.*?):\s+expected\s', norm)
    field = m.group(1) if m else norm
    patterns[field] += 1
    if field not in examples:
        examples[field] = diff_line

print("=== Diffs by pattern (most common first) ===\n")
for pattern, count in patterns.most_common():
    print(f"  {count:4d}  {pattern}")
    print(f"        Example: {examples[pattern][:120]}")
    print()
