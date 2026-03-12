"""Check marker layer start times."""
import sys
sys.path.insert(0, "src")
from pathlib import Path
import aep_parser

r = aep_parser.parse(Path("samples/bugs/29.97_fps_time_scale_3.125.aep"))

for c in r.project.compositions:
    for idx, layer in enumerate(c.layers):
        markers = getattr(layer, "markers", [])
        if markers:
            st = layer.start_time
            print(f"Comp[{c.name}](id={c.id}).layers[{idx}] '{layer.name}'")
            print(f"  start_time={st}")
            for m in markers[:3]:
                t = m.time
                print(f"  marker t={t} + start_time = {t + st}")
