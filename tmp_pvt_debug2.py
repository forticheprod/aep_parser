"""Debug parsed layer structure."""
from __future__ import annotations
from aep_parser import parse

app = parse("samples/bugs/29.97_fps_time_scale_3.125.aep")

for proj_item in app.project.items:
    comp_id = getattr(proj_item, "id", None)
    if comp_id != 155:
        continue
    layers = getattr(proj_item, "layers", None)
    if not layers:
        print("NO LAYERS")
        continue
    layer = layers[0]
    print(f"Layer type: {type(layer).__name__}")
    print(f"Layer attrs: {[a for a in dir(layer) if not a.startswith('_')][:20]}")
    props = getattr(layer, "properties", None)
    print(f"Properties: {type(props)} len={len(props) if props else 0}")
    if props:
        for p in props[:5]:
            mn = getattr(p, "match_name", None)
            pvt = getattr(p, "property_value_type", None)
            children = getattr(p, "properties", None)
            nchildren = len(children) if children else 0
            print(f"  mn={mn} pvt={pvt} children={nchildren} type={type(p).__name__}")
            if children:
                for c in children[:3]:
                    cmn = getattr(c, "match_name", None)
                    cpvt = getattr(c, "property_value_type", None)
                    cc = getattr(c, "properties", None)
                    ncc = len(cc) if cc else 0
                    print(f"    mn={cmn} pvt={cpvt} children={ncc}")
    break
