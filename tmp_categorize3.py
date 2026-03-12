"""Categorize all diffs - directly invoke the validation logic."""
from __future__ import annotations
import json
import re
from collections import Counter
from aep_parser import parse
from aep_parser.cli.validate import compare_parsed_to_json

AEP = "samples/bugs/29.97_fps_time_scale_3.125.aep"
JSN = "samples/bugs/29.97_fps_time_scale_3.125.json"

with open(JSN, encoding="utf-8") as f:
    jdata = json.load(f)

app = parse(AEP)
diffs = compare_parsed_to_json(app, jdata)

print(f"Total diffs: {len(diffs)}")

# Categorize
patterns = Counter()
for d in diffs:
    desc = d["description"] if isinstance(d, dict) else str(d)
    norm = re.sub(r'Comp\[[^\]]+\]', 'Comp[*]', desc)
    norm = re.sub(r'layers\[\d+\]', 'layers[N]', norm)
    norm = re.sub(r'Footage\[[^\]]+\]', 'Footage[*]', norm)
    m = re.match(r'^(.*?):\s+expected\s', norm)
    field = m.group(1) if m else norm
    patterns[field] += 1

print()
for pattern, count in patterns.most_common():
    print(f"  {count:4d}  {pattern}")
