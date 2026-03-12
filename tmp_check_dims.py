"""Check parsed values for both comp instances and speed scaling."""
from __future__ import annotations

from aep_parser import parse

app = parse("samples/bugs/29.97_fps_time_scale_3.125.aep")
project = app.project

for item_id, item in project.items.items():
    if hasattr(item, "layers") and "lignes" in getattr(item, "name", ""):
        if item_id == 11516:
            layer = item.layers[0]
            for p in layer.properties:
                if p.match_name == "ADBE Effect Parade":
                    for eff in getattr(p, "properties", []):
                        ie = getattr(eff, "is_effect", None)
                        print(f"Effect: {eff.name} mn={eff.match_name} is_effect={ie}")
                        for ep in getattr(eff, "properties", []):
                            pct = getattr(ep, "property_control_type", None)
                            ie2 = getattr(ep, "is_effect", None)
                            print(f"  {ep.name} mn={ep.match_name} pct={pct} is_effect={ie2}")

