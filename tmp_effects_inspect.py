"""Deep investigation of layers with effects."""
import sys
sys.path.insert(0, "src")
from pathlib import Path
import aep_parser

r = aep_parser.parse(Path("samples/bugs/29.97_fps_time_scale_3.125.aep"))
p = r.project

for c in p.compositions:
    for idx, layer in enumerate(c.layers):
        # Navigate property tree to find effects
        for pg in layer.properties:
            mn = getattr(pg, "match_name", "")
            if mn == "ADBE Effect Parade":
                props = getattr(pg, "properties", [])
                if props:
                    lt = getattr(layer, "layer_type", "?")
                    print(f"Comp[{c.name}](id={c.id}).layers[{idx}] '{layer.name}' type={lt}")
                    for eff in props:
                        en = getattr(eff, "name", "?")
                        emn = getattr(eff, "match_name", "?")
                        eprops = getattr(eff, "properties", [])
                        print(f"  Effect: {en} ({emn}) props={len(eprops)}")
                        for ep in eprops:
                            epn = getattr(ep, "name", "?")
                            epmn = getattr(ep, "match_name", "?")
                            v = getattr(ep, "value", None)
                            kfs = getattr(ep, "keyframes", [])
                            minv = getattr(ep, "min_value", None)
                            maxv = getattr(ep, "max_value", None)
                            kfcount = len(kfs) if kfs else 0
                            print(f"    {epn} ({epmn}) val={v} min={minv} max={maxv} kfs={kfcount}")
                            if kfs:
                                for kf in kfs[:3]:
                                    print(f"      t={kf.time} ft={kf.frame_time} v={kf.value}")
                                    if kf.out_temporal_ease:
                                        print(f"      outEase: speed={kf.out_temporal_ease[0].speed}")
