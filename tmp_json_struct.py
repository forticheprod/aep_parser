"""Check JSON structure to understand property nesting."""
from __future__ import annotations
import json

JSN = "samples/bugs/29.97_fps_time_scale_3.125.json"
with open(JSN, encoding="utf-8") as f:
    jdata = json.load(f)

# Check first comp, first layer, first few levels
for item in jdata.get("items", []):
    if item.get("typeName") != "Composition":
        continue
    print(f"Comp: {item['name']} (id={item['id']})")
    for layer in item.get("layers", [])[:1]:
        print(f"  Layer keys: {list(layer.keys())[:15]}")
        # Check what has propertyValueType
        def show_props(obj, indent=2, depth=0):
            if depth > 4:
                return
            if isinstance(obj, dict):
                mn = obj.get("matchName")
                pvt = obj.get("propertyValueType")
                name = obj.get("name")
                if mn:
                    print(f"{'  ' * indent}mn={mn} pvt={pvt} name={name}")
                props = obj.get("properties")
                if isinstance(props, list):
                    for p in props[:5]:
                        show_props(p, indent + 1, depth + 1)
                    if len(props) > 5:
                        print(f"{'  ' * (indent+1)}... {len(props) - 5} more")

        show_props(layer)
    break
