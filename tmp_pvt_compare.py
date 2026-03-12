"""Compare PropertyValueType between parser and ExtendScript JSON.

Walks all properties in the parsed model and the JSON, matches them
by path, and reports any propertyValueType mismatches.
"""
from __future__ import annotations

import json
from aep_parser import parse
from aep_parser.enums import PropertyValueType

AEP = "samples/bugs/29.97_fps_time_scale_3.125.aep"
JSN = "samples/bugs/29.97_fps_time_scale_3.125.json"

with open(JSN, encoding="utf-8") as f:
    jdata = json.load(f)

app = parse(AEP)


def walk_json_props(obj, path="", results=None):
    """Recursively walk JSON and collect property info by path."""
    if results is None:
        results = {}
    if isinstance(obj, dict):
        pvt = obj.get("propertyValueType")
        mn = obj.get("matchName")
        name = obj.get("name")
        if pvt is not None and mn is not None:
            results[path] = {
                "propertyValueType": pvt,
                "matchName": mn,
                "name": name,
            }
        # Recurse into properties array
        props = obj.get("properties")
        if isinstance(props, list):
            for item in props:
                item_mn = item.get("matchName", item.get("name", "?"))
                child_path = f"{path}/{item_mn}" if path else item_mn
                walk_json_props(item, child_path, results)
    return results


def walk_parsed_props(prop, path="", results=None):
    """Recursively walk parsed model and collect property info by path."""
    if results is None:
        results = {}
    mn = getattr(prop, "match_name", None)
    pvt = getattr(prop, "property_value_type", None)
    if pvt is not None and mn is not None:
        results[path] = {
            "property_value_type": pvt,
            "match_name": mn,
            "name": getattr(prop, "name", None),
        }
    children = getattr(prop, "properties", None)
    if children:
        for child in children:
            child_mn = getattr(child, "match_name", "?")
            child_path = f"{path}/{child_mn}" if path else child_mn
            walk_parsed_props(child, child_path, results)
    return results


# Build maps for each comp
diffs_by_type = {}  # (expected, got) -> list of match_names
total_compared = 0
total_match = 0

for item in jdata.get("items", []):
    if item.get("typeName") != "Composition":
        continue
    comp_id = item["id"]
    comp_name = item["name"]

    # Find matching parsed comp
    parsed_comp = None
    for proj_item in app.project.items:
        if getattr(proj_item, "id", None) == comp_id:
            parsed_comp = proj_item
            break
    if parsed_comp is None:
        continue

    # Walk JSON layers
    json_by_path = {}
    for layer_data in item.get("layers", []):
        layer_idx = layer_data.get("index", "?")
        layer_prefix = f"layer[{layer_idx}]"
        walk_json_props(layer_data, layer_prefix, json_by_path)

    # Walk parsed layers
    parsed_by_path = {}
    layers = getattr(parsed_comp, "layers", [])
    for layer in layers:
        layer_idx = getattr(layer, "index", "?")
        layer_prefix = f"layer[{layer_idx}]"
        for prop in getattr(layer, "properties", []):
            child_mn = getattr(prop, "match_name", "?")
            walk_parsed_props(prop, f"{layer_prefix}/{child_mn}", parsed_by_path)

    # Compare
    for path, j_info in json_by_path.items():
        if path not in parsed_by_path:
            continue
        p_info = parsed_by_path[path]
        j_pvt = j_info["propertyValueType"]
        p_pvt = p_info["property_value_type"]

        # Convert parsed enum to int for comparison
        p_pvt_int = int(p_pvt) if p_pvt is not None else None

        total_compared += 1
        if j_pvt == p_pvt_int:
            total_match += 1
        else:
            j_name = PropertyValueType(j_pvt).name if j_pvt in PropertyValueType._value2member_map_ else str(j_pvt)
            p_name = p_pvt.name if p_pvt is not None else "None"
            key = (j_name, p_name)
            if key not in diffs_by_type:
                diffs_by_type[key] = []
            diffs_by_type[key].append((comp_name, comp_id, path, j_info["matchName"]))

print(f"Total compared: {total_compared}")
print(f"Matching: {total_match}")
print(f"Mismatches: {total_compared - total_match}")
print()

for (expected, got), items in sorted(diffs_by_type.items(), key=lambda x: -len(x[1])):
    print(f"=== Expected {expected}, Got {got} ({len(items)} occurrences) ===")
    # Show unique match names
    unique_mns = {}
    for comp_name, comp_id, path, mn in items:
        if mn not in unique_mns:
            unique_mns[mn] = []
        unique_mns[mn].append(f"  {comp_name}(id={comp_id}): {path}")
    for mn, paths in unique_mns.items():
        print(f"  match_name: {mn}")
        for p in paths[:3]:
            print(f"    {p}")
        if len(paths) > 3:
            print(f"    ... and {len(paths) - 3} more")
    print()
