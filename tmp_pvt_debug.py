"""Debug path matching."""
from __future__ import annotations
import json
from aep_parser import parse

AEP = "samples/bugs/29.97_fps_time_scale_3.125.aep"
JSN = "samples/bugs/29.97_fps_time_scale_3.125.json"

with open(JSN, encoding="utf-8") as f:
    jdata = json.load(f)

app = parse(AEP)


def collect_json_pvt(obj, path_parts, results):
    mn = obj.get("matchName")
    pvt = obj.get("propertyValueType")
    current_parts = path_parts + [mn] if mn else path_parts
    if pvt is not None and mn is not None:
        results.append((tuple(current_parts), pvt, mn))
    for child in obj.get("properties", []):
        collect_json_pvt(child, current_parts, results)


def collect_parsed_pvt(prop, path_parts, results):
    mn = getattr(prop, "match_name", None)
    pvt = getattr(prop, "property_value_type", None)
    current_parts = path_parts + [mn] if mn else path_parts
    if pvt is not None and mn is not None:
        results.append((tuple(current_parts), pvt, mn))
    for child in getattr(prop, "properties", []) or []:
        collect_parsed_pvt(child, current_parts, results)


# Check first comp
for item in jdata.get("items", []):
    if item.get("typeName") != "Composition":
        continue
    comp_id = item["id"]
    print(f"JSON comp {comp_id}:")
    for li, layer in enumerate(item.get("layers", [])[:1]):
        entries = []
        collect_json_pvt(layer, [f"L{li}"], entries)
        for path, pvt, mn in entries[:10]:
            print(f"  {'/'.join(path)}")
    break

print()

for proj_item in app.project.items:
    comp_id = getattr(proj_item, "id", None)
    if comp_id != 155:
        continue
    print(f"Parsed comp {comp_id}:")
    layers = getattr(proj_item, "layers", None)
    if not layers:
        print("  NO LAYERS")
        continue
    for li, layer in enumerate(layers[:1]):
        entries = []
        for prop in getattr(layer, "properties", []) or []:
            collect_parsed_pvt(prop, [f"L{li}"], entries)
        for path, pvt, mn in entries[:10]:
            print(f"  {'/'.join(path)}")
    break
