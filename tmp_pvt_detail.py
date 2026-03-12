"""Deeper investigation of the 18 mismatches."""
from __future__ import annotations
import json
from aep_parser import parse
from aep_parser.enums import PropertyValueType, PropertyControlType

AEP = "samples/bugs/29.97_fps_time_scale_3.125.aep"
JSN = "samples/bugs/29.97_fps_time_scale_3.125.json"

with open(JSN, encoding="utf-8") as f:
    jdata = json.load(f)

app = parse(AEP)


def find_parsed_prop(comp_id, path_parts):
    """Navigate to a specific property in the parsed model."""
    for comp in app.project.compositions:
        if comp.id != comp_id:
            continue
        li = int(path_parts[0][1:])
        layer = comp.layers[li]
        current = None
        remaining = path_parts[1:]

        for prop in layer.properties:
            if getattr(prop, "match_name", None) == remaining[0]:
                current = prop
                break

        if current is None:
            return None

        for part in remaining[1:]:
            found = False
            for child in getattr(current, "properties", []) or []:
                if getattr(child, "match_name", None) == part:
                    current = child
                    found = True
                    break
            if not found:
                return None
        return current
    return None


# Investigate each category
cases = [
    # TwoD_SPATIAL expected
    (155, ("L0", "ADBE Effect Parade", "ADBE Geometry2", "ADBE Geometry2-0001")),
    (155, ("L0", "ADBE Effect Parade", "ADBE Geometry2", "ADBE Geometry2-0002")),
    (11516, ("L0", "ADBE Effect Parade", "ADBE Geometry2", "ADBE Geometry2-0001")),
    (11516, ("L0", "ADBE Effect Parade", "ADBE Geometry2", "ADBE Geometry2-0002")),
    # NO_VALUE expected
    (281855, ("L0", "ADBE Effect Parade", "S_BlurDirectional", "S_BlurDirectional-0238")),
    (281855, ("L0", "ADBE Effect Parade", "S_BlurDirectional", "S_BlurDirectional-0250")),
    (281855, ("L0", "ADBE Effect Parade", "S_BlurDirectional", "S_BlurDirectional-0251")),
    # LAYER_INDEX
    (281855, ("L0", "ADBE Effect Parade", "S_BlurDirectional", "S_BlurDirectional-0001")),
    # MASK_INDEX
    (281855, ("L0", "ADBE Effect Parade", "S_BlurDirectional", "S_BlurDirectional-0235")),
    # CUSTOM_VALUE
    (281855, ("L0", "ADBE Effect Parade", "S_BlurDirectional", "S_BlurDirectional-0520")),
    # TwoD (mask feather)
    (281855, ("L0", "ADBE Mask Parade", "ADBE Mask Atom", "ADBE Mask Feather")),
]

for comp_id, path in cases:
    prop = find_parsed_prop(comp_id, path)
    if prop is None:
        print(f"NOT FOUND: {comp_id} / {'/'.join(path)}")
        continue
    print(f"{comp_id} / {'/'.join(path)}:")
    print(f"  match_name={prop.match_name}")
    print(f"  property_value_type={prop.property_value_type}")
    print(f"  property_control_type={prop.property_control_type}")
    print(f"  is_effect={getattr(prop, 'is_effect', 'N/A')}")
    # Check tdb4 flags if accessible
    for attr in ["dimensions", "last_value", "default_value", "min_value", "max_value",
                 "nb_options", "property_parameters"]:
        val = getattr(prop, attr, "N/A")
        if val != "N/A":
            print(f"  {attr}={val}")
    print()
