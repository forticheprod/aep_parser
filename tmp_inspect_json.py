"""Inspect JSON expected data for the 29.97fps bug sample."""
import json

data = json.load(open("samples/bugs/29.97_fps_time_scale_3.125.json", encoding="utf-8"))
comps = [i for i in data.get("items", []) if "layers" in i]
for c in comps[:1]:
    print(f"Comp: {c['name']}")
    print(f"  frameRate: {c.get('frameRate')}")
    print(f"  displayStartTime: {c.get('displayStartTime')}")
    print(f"  duration: {c.get('duration')}")
    for layer in c.get("layers", [])[:1]:
        print(f"  Layer: {layer.get('name')}")
        print(f"    inPoint: {layer.get('inPoint')}")
        print(f"    outPoint: {layer.get('outPoint')}")
        print(f"    startTime: {layer.get('startTime')}")
        effects = layer.get("effects", [])
        for eff in effects[:2]:
            print(f"    Effect: {eff.get('name')}")
            for prop in eff.get("properties", []):
                name = prop.get("name")
                mn = prop.get("matchName")
                kfs = prop.get("keyframes", [])
                val = prop.get("value")
                minv = prop.get("minValue")
                maxv = prop.get("maxValue")
                print(f"      {name} ({mn}) val={val} min={minv} max={maxv} kf_count={len(kfs)}")
                for kf in kfs[:3]:
                    print(f"        kf time={kf.get('time')} value={kf.get('value')}")
                    ease_out = kf.get("outTemporalEase", [])
                    if ease_out:
                        print(f"           outEase speed={ease_out[0].get('speed')}")
