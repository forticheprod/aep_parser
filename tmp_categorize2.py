"""Categorize all diffs by running validation ourselves."""
from __future__ import annotations
import re
import subprocess
import sys
from collections import Counter

result = subprocess.run(
    [sys.executable, "-m", "aep_parser.cli.validate",
     "samples/bugs/29.97_fps_time_scale_3.125.aep",
     "samples/bugs/29.97_fps_time_scale_3.125.json",
     "--verbose"],
    capture_output=True, text=True, encoding="utf-8"
)

output = result.stdout + result.stderr
lines = []
in_diffs = False
for line in output.splitlines():
    if "All differences:" in line:
        in_diffs = True
        continue
    if in_diffs and line.startswith("  ") and ":" in line:
        lines.append(line.strip())

print(f"Total diff lines: {len(lines)}")

# Normalize and categorize
patterns = Counter()
for line in lines:
    norm = re.sub(r'Comp\[[^\]]+\]', 'Comp[*]', line)
    norm = re.sub(r'layers\[\d+\]', 'layers[N]', norm)
    norm = re.sub(r'Footage\[[^\]]+\]', 'Footage[*]', norm)
    m = re.match(r'^(.*?):\s+expected\s', norm)
    if m:
        field = m.group(1)
    else:
        field = norm
    patterns[field] += 1

print()
for pattern, count in patterns.most_common():
    print(f"  {count:4d}  {pattern}")
