"""Analyze validation diffs."""
from collections import Counter

lines = open("tmp_all_diffs.txt", encoding="utf-8").read().strip().split("\n")
lines = [l for l in lines if l.strip()]

cats = Counter()
for l in lines:
    if "layerType" in l:
        cats["layerType"] += 1
    elif "Time Remap" in l:
        cats["Time Remap"] += 1
    elif "Effects" in l:
        cats["Effects.Transform"] += 1
    elif "marker" in l.lower():
        cats["markers"] += 1
    elif l.startswith("Project."):
        cats["project"] += 1
    elif any(x in l for x in ["alphaMode", "frameRate", "hasAlpha", "file"]):
        cats["footage"] += 1
    else:
        cats["other"] += 1

print("=== DIFF CATEGORY BREAKDOWN ===")
for k, v in cats.most_common():
    print(f"  {k}: {v}")
print(f"  Total: {sum(cats.values())}")

print("\n=== ALL UNIQUE PATTERN TYPES ===")
# Find unique diff patterns
import re
patterns = Counter()
for l in lines:
    # Normalize comp names and layer indices
    p = re.sub(r'\[.*?\]', '[*]', l)
    p = re.sub(r'keyframes\[*\]\.\w+', 'keyframes[*].FIELD', p)
    patterns[p] += 1

for p, c in patterns.most_common():
    print(f"  [{c:3d}] {p}")
