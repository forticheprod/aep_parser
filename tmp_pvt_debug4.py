"""Debug parsed model structure."""
from aep_parser import parse

app = parse("samples/bugs/29.97_fps_time_scale_3.125.aep")
proj = app.project
print(f"Project type: {type(proj).__name__}")
print(f"Project attrs: {[a for a in dir(proj) if not a.startswith('_')]}")

# Check items
items = proj.items
print(f"items type: {type(items)}, len={len(items)}")
if items:
    print(f"  first item type: {type(items[0])}")

# Check if there's a different way to access comps
for attr in dir(proj):
    if attr.startswith("_"):
        continue
    val = getattr(proj, attr)
    if isinstance(val, list) and len(val) > 0:
        print(f"proj.{attr}: list[{type(val[0]).__name__}] len={len(val)}")
    elif not callable(val):
        print(f"proj.{attr}: {type(val).__name__} = {repr(val)[:80]}")
