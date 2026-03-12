"""Inspect binary values for the 29.97fps sample layer."""
from __future__ import annotations

from pathlib import Path
from aep_parser import parse

app = parse(Path("samples/bugs/29.97_fps_time_scale_3.125.aep"))
project = app.project


def find_comps(folder):
    """Find all comps recursively."""
    for item in folder.items:
        if hasattr(item, "layers"):
            yield item
        if hasattr(item, "items"):
            yield from find_comps(item)


for comp in find_comps(project.root_folder):
    if "lignes" not in comp.name:
        continue
    print(f"Comp: {comp.name} (id={comp.id})")
    print(f"  frame_rate={comp.frame_rate}")
    print(f"  time_scale={comp.time_scale}")
    print(f"  width={comp.width}, height={comp.height}")
    for i, layer in enumerate(comp.layers[:2]):
        print(f"\n  Layer[{i}]: {layer.name}")
        print(f"    start_time={layer.start_time}")
        print(f"    stretch={layer.stretch}")
        print(f"    in_point={layer.in_point}")
        print(f"    out_point={layer.out_point}")
        print(f"    time_remap_enabled={layer.time_remap_enabled}")
        # Find effect keyframes
        for prop in layer.properties:
            if prop.match_name == "ADBE Effect Parade" and hasattr(prop, "properties"):
                for eff in prop.properties:
                    print(f"    Effect: {eff.name} ({eff.match_name})")
                    if hasattr(eff, "properties"):
                        for ep in eff.properties:
                            if hasattr(ep, "keyframes") and ep.keyframes:
                                print(f"      {ep.name} ({ep.match_name}):")
                                for ki, kf in enumerate(ep.keyframes):
                                    print(f"        kf[{ki}]: frame_time={kf.frame_time}, time={kf.time:.15f}, value={kf.value}")
                            elif hasattr(ep, "value"):
                                print(f"      {ep.name}: value={ep.value}")
        # Find time remap
        for prop in layer.properties:
            if prop.match_name == "ADBE Time Remapping":
                if hasattr(prop, "keyframes") and prop.keyframes:
                    print(f"    Time Remap keyframes:")
                    for ki, kf in enumerate(prop.keyframes):
                        print(f"      kf[{ki}]: frame_time={kf.frame_time}, time={kf.time:.15f}, value={kf.value}")
                else:
                    print(f"    Time Remap: value={prop.value}, animated={prop.animated}")
    break
