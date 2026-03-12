"""Categorize all 257 diffs by pattern."""
from __future__ import annotations
import re
from collections import Counter

with open("tmp_diffs_full.txt", encoding="utf-8") as f:
    content = f.read()

# Find all diff lines in the "All differences:" section
in_diffs = False
lines = []
for line in content.splitlines():
    if line.strip() == "All differences:":
        in_diffs = True
        continue
    if in_diffs and line.startswith("  "):
        lines.append(line.strip())
    if line.startswith("  ... and ") and "more" in line:
        # There are truncated lines; we need the non-verbose output
        pass

print(f"Diff lines found: {len(lines)}")

# Normalize and categorize
patterns = Counter()
for line in lines:
    # Remove comp name, layer index
    norm = re.sub(r'Comp\[[^\]]+\]', 'Comp[*]', line)
    norm = re.sub(r'layers\[\d+\]', 'layers[N]', norm)
    norm = re.sub(r'Footage\[[^\]]+\]', 'Footage[*]', norm)
    # Extract field (before ": expected")
    m = re.match(r'^(.*?):\s+expected\s', norm)
    if m:
        field = m.group(1)
    else:
        field = norm
    patterns[field] += 1

print()
for pattern, count in patterns.most_common(30):
    print(f"  {count:4d}  {pattern}")
