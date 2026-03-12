"""Deep investigation of 29.97fps diffs."""
import json
import sys
sys.path.insert(0, "src")
from pathlib import Path
import aep_parser

# Parse AEP
result = aep_parser.parse(Path("samples/bugs/29.97_fps_time_scale_3.125.aep"))

# Load JSON
data = json.load(open("samples/bugs/29.97_fps_time_scale_3.125.json", encoding="utf-8"))

# Find parsed comps
print("=== PARSED COMPOSITIONS ===")
for item in result.project.items:
    if hasattr(item, "layers"):
        print(f"  Comp: {item.name} (id={item.id})")
        if hasattr(item, "time_scale"):
            print(f"    time_scale={item.time_scale}")
        print(f"    frame_rate={item.frame_rate}")
        if hasattr(item, "display_start_time"):
            print(f"    display_start_time={item.display_start_time}")

        # Check first layer with effects
        for idx, layer in enumerate(item.layers):
            lt = layer.layer_type if hasattr(layer, "layer_type") else "?"
            # Check for effects
            effects = None
            for pg in getattr(layer, "properties", []):
                if hasattr(pg, "match_name") and pg.match_name == "ADBE Effect Parade":
                    effects = pg
                    break
            if effects and hasattr(effects, "properties") and effects.properties:
                print(f"    Layer[{idx}] '{layer.name}' type={lt}")
                for eff in effects.properties:
                    ename = getattr(eff, "name", "?")
                    emn = getattr(eff, "match_name", "?")
                    print(f"      Effect: {ename} ({emn})")
                    if hasattr(eff, "properties"):
                        for p in eff.properties:
                            pn = getattr(p, "name", "?")
                            pmn = getattr(p, "match_name", "?")
                            v = getattr(p, "value", None)
                            kfs = getattr(p, "keyframes", [])
                            minv = getattr(p, "min_value", None)
                            maxv = getattr(p, "max_value", None)
                            print(f"        {pn} ({pmn}) val={v} min={minv} max={maxv} kfs={len(kfs) if kfs else 0}")
                            if kfs:
                                for kf in kfs[:3]:
                                    print(f"          t={kf.time} ft={kf.frame_time} v={kf.value}")

            # Check layer type
            if idx < 2:
                print(f"    Layer[{idx}] '{layer.name}' type={lt} has_effects={'effects' in str(type(effects))}")
        break  # Just first comp
