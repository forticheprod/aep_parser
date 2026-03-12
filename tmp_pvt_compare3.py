"""Compare PropertyValueType: parser vs ExtendScript JSON.

Uses the correct model API (proj.compositions, items dict).
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
    """Collect (path, pvt, pct) from parsed model recursively."""
    mn = getattr(prop, "match_name", None)
    pvt = getattr(prop, "property_value_type", None)
    pct = getattr(prop, "property_control_type", None)
    is_effect = getattr(prop, "is_effect", False)
    current_parts = path_parts + [mn] if mn else path_parts

    if pvt is not None and mn is not None:
        results.append((tuple(current_parts), pvt, pct, mn, is_effect))

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

# Collect from parsed (using proj.compositions)
parsed_props = {}  # {(comp_id, path): (pvt, pct, mn, is_effect)}
for comp in app.project.compositions:
    comp_id = comp.id
    for li, layer in enumerate(comp.layers):
        entries = []
        for prop in layer.properties:
            collect_parsed_pvt(prop, [f"L{li}"], entries)
        for path, pvt, pct, mn, is_effect in entries:
            parsed_props[(comp_id, path)] = (pvt, pct, mn, is_effect)

print(f"JSON properties: {len(json_props)}")
print(f"Parsed properties: {len(parsed_props)}")

# Compare
total = 0
match_count = 0
diffs = defaultdict(list)

for key in json_props:
    if key not in parsed_props:
        continue
    j_pvt, j_mn = json_props[key]
    p_pvt, p_pct, p_mn, is_effect = parsed_props[key]
    total += 1

    j_pvt_int = j_pvt
    p_pvt_int = int(p_pvt)

    if j_pvt_int == p_pvt_int:
        match_count += 1
    else:
        j_name = PropertyValueType(j_pvt_int).name if j_pvt_int in PropertyValueType._value2member_map_ else str(j_pvt_int)
        p_name = p_pvt.name
        p_pct_name = p_pct.name if p_pct else "None"
        comp_id = key[0]
        path = "/".join(key[1])
        diffs[(j_name, p_name)].append((comp_id, path, p_mn, p_pct_name, is_effect))

print(f"Matched paths: {total}")
print(f"PropertyValueType correct: {match_count}")
print(f"PropertyValueType mismatches: {total - match_count}")
print()

for (expected, got), items in sorted(diffs.items(), key=lambda x: -len(x[1])):
    print(f"=== Expected {expected}, Got {got}: {len(items)} occurrences ===")
    by_mn = defaultdict(list)
    for comp_id, path, mn, pct, is_effect in items:
        by_mn[(mn, pct, is_effect)].append((comp_id, path))
    for (mn, pct, is_eff), paths in sorted(by_mn.items()):
        print(f"  match_name={mn}  pct={pct}  in_effect={is_eff}  ({len(paths)}x)")
        for comp_id, path in paths[:2]:
            print(f"    comp {comp_id}: {path}")
        if len(paths) > 2:
            print(f"    ... +{len(paths)-2} more")
    print()
