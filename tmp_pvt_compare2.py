"""Compare PropertyValueType: parser vs ExtendScript JSON.

Collects all properties by full path (comp_id + ancestor match_names)
and compares propertyValueType values.
"""
from __future__ import annotations

import json
from collections import defaultdict
from aep_parser import parse
from aep_parser.enums import PropertyValueType, PropertyControlType

AEP = "samples/bugs/29.97_fps_time_scale_3.125.aep"
JSN = "samples/bugs/29.97_fps_time_scale_3.125.json"

with open(JSN, encoding="utf-8") as f:
    jdata = json.load(f)

app = parse(AEP)


def collect_json_pvt(obj, path_parts, results):
    """Collect (path, pvt) from JSON recursively."""
    mn = obj.get("matchName")
    pvt = obj.get("propertyValueType")
    current_parts = path_parts + [mn] if mn else path_parts

    if pvt is not None and mn is not None:
        results.append((tuple(current_parts), pvt, mn))

    for child in obj.get("properties", []):
        collect_json_pvt(child, current_parts, results)


def collect_parsed_pvt(prop, path_parts, results):
    """Collect (path, pvt) from parsed model recursively."""
    mn = getattr(prop, "match_name", None)
    pvt = getattr(prop, "property_value_type", None)
    pct = getattr(prop, "property_control_type", None)
    current_parts = path_parts + [mn] if mn else path_parts

    if pvt is not None and mn is not None:
        results.append((tuple(current_parts), pvt, pct, mn))

    for child in getattr(prop, "properties", []) or []:
        collect_parsed_pvt(child, current_parts, results)


# Collect from JSON
json_props = {}  # {(comp_id, path): (pvt, mn)}
for item in jdata.get("items", []):
    if item.get("typeName") != "Composition":
        continue
    comp_id = item["id"]
    for li, layer in enumerate(item.get("layers", [])):
        entries = []
        collect_json_pvt(layer, [f"L{li}"], entries)
        for path, pvt, mn in entries:
            json_props[(comp_id, path)] = (pvt, mn)

# Collect from parsed
parsed_props = {}  # {(comp_id, path): (pvt, pct, mn)}
for proj_item in app.project.items:
    comp_id = getattr(proj_item, "id", None)
    if comp_id is None:
        continue
    layers = getattr(proj_item, "layers", None)
    if not layers:
        continue
    for li, layer in enumerate(layers):
        for prop in getattr(layer, "properties", []) or []:
            entries = []
            collect_parsed_pvt(prop, [f"L{li}"], entries)
            for path, pvt, pct, mn in entries:
                parsed_props[(comp_id, path)] = (pvt, pct, mn)

# Compare
total = 0
match = 0
diffs = defaultdict(list)  # (expected_name, got_name) -> [(comp_id, path, mn, pct)]

for key in json_props:
    if key not in parsed_props:
        continue
    j_pvt, j_mn = json_props[key]
    p_pvt, p_pct, p_mn = parsed_props[key]
    total += 1

    j_pvt_int = j_pvt
    p_pvt_int = int(p_pvt)

    if j_pvt_int == p_pvt_int:
        match += 1
    else:
        j_name = PropertyValueType(j_pvt_int).name if j_pvt_int in PropertyValueType._value2member_map_ else str(j_pvt_int)
        p_name = p_pvt.name
        p_pct_name = p_pct.name if p_pct else "None"
        comp_id = key[0]
        path = "/".join(key[1])
        diffs[(j_name, p_name)].append((comp_id, path, p_mn, p_pct_name))

print(f"Total compared: {total}")
print(f"Matching: {match}")
print(f"Mismatches: {total - match}")
print()

for (expected, got), items in sorted(diffs.items(), key=lambda x: -len(x[1])):
    print(f"=== Expected {expected}, Got {got}: {len(items)} occurrences ===")
    # Group by unique match_name + pct
    by_mn = defaultdict(list)
    for comp_id, path, mn, pct in items:
        by_mn[(mn, pct)].append((comp_id, path))
    for (mn, pct), paths in sorted(by_mn.items()):
        print(f"  match_name={mn}  pct={pct}  ({len(paths)}x)")
        for comp_id, path in paths[:2]:
            print(f"    comp {comp_id}: {path}")
        if len(paths) > 2:
            print(f"    ... +{len(paths)-2} more")
    print()
