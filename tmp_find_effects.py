"""Find all effects in JSON."""
import json

data = json.load(open("samples/bugs/29.97_fps_time_scale_3.125.json", encoding="utf-8"))
comps = [i for i in data.get("items", []) if "layers" in i]

for c in comps:
    name = c["name"]
    cid = c.get("id")
    for idx, layer in enumerate(c.get("layers", [])):
        effects = layer.get("effects", [])
        if effects:
            ln = layer.get("name", "?")
            lt = layer.get("layerType", "?")
            print(f"Comp[{name}](id={cid}).layers[{idx}] '{ln}' type={lt}")
            for eff in effects:
                en = eff.get("name", "?")
                emn = eff.get("matchName", "?")
                props = eff.get("properties", [])
                print(f"  Effect: {en} ({emn}) props={len(props)}")
                for p in props[:3]:
                    pn = p.get("name", "?")
                    kfs = p.get("keyframes", [])
                    v = p.get("value")
                    print(f"    {pn}: val={v} kfs={len(kfs)}")
                    for kf in kfs[:2]:
                        print(f"      t={kf.get('time')} v={kf.get('value')}")

        # Also show time remap
        tr_props = [p for p in layer.get("properties", []) if "Time Remap" in p.get("name", "")]
        if not tr_props:
            tr = layer.get("timeRemap")
            if tr and (tr.get("minValue") is not None or tr.get("maxValue") is not None):
                ln = layer.get("name", "?")
                print(f"Comp[{name}](id={cid}).layers[{idx}] '{ln}' has timeRemap min={tr.get('minValue')} max={tr.get('maxValue')}")

# Also check markers
for c in comps:
    markers = c.get("markers", [])
    if markers:
        name = c["name"]
        cid = c.get("id")
        print(f"\nComp[{name}](id={cid}) has {len(markers)} markers")
        for m in markers[:3]:
            print(f"  marker: comment={m.get('comment')}")
    for idx, layer in enumerate(c.get("layers", [])):
        markers = layer.get("markers", [])
        if markers:
            ln = layer.get("name", "?")
            print(f"Comp[{name}](id={cid}).layers[{idx}] '{ln}' has {len(markers)} markers")
            for m in markers[:3]:
                print(f"  marker: comment={m.get('comment', '?')}")
