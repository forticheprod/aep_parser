"""Inspect JSON expected data for the 29.97fps bug sample."""
import json

data = json.load(open("samples/bugs/29.97_fps_time_scale_3.125.json", encoding="utf-8"))
comps = [i for i in data.get("items", []) if "layers" in i]

for c in comps[:1]:
    name = c["name"]
    fr = c.get("frameRate")
    dur = c.get("duration")
    print(f"Comp: {name} fps={fr} dur={dur}")

    for idx, layer in enumerate(c.get("layers", [])[:2]):
        ln = layer.get("name", "?")
        ip = layer.get("inPoint")
        st = layer.get("startTime")
        lt = layer.get("layerType")
        print(f"\n  Layer[{idx}]: {ln} type={lt} in={ip} start={st}")

        effects = layer.get("effects", [])
        print(f"    effects count: {len(effects)}")
        for eff in effects[:2]:
            en = eff.get("name", "?")
            emn = eff.get("matchName", "?")
            props = eff.get("properties", [])
            print(f"    Effect: {en} ({emn}) props={len(props)}")
            for p in props:
                pn = p.get("name", "?")
                pmn = p.get("matchName", "?")
                v = p.get("value")
                minv = p.get("minValue")
                maxv = p.get("maxValue")
                kfs = p.get("keyframes", [])
                print(f"      {pn} ({pmn}) val={v} min={minv} max={maxv} kfs={len(kfs)}")
                for kf in kfs[:3]:
                    t = kf.get("time")
                    kv = kf.get("value")
                    oe = kf.get("outTemporalEase", [])
                    sp = oe[0].get("speed") if oe else None
                    print(f"        t={t} v={kv} outSpeed={sp}")

        # Time Remap
        tr = layer.get("timeRemap")
        if tr:
            print(f"    Time Remap: min={tr.get('minValue')} max={tr.get('maxValue')}")
            kfs = tr.get("keyframes", [])
            print(f"      keyframes: {len(kfs)}")
            for kf in kfs[:3]:
                print(f"        t={kf.get('time')} v={kf.get('value')}")
