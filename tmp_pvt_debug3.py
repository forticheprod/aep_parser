"""Debug: list all parsed items."""
from aep_parser import parse

app = parse("samples/bugs/29.97_fps_time_scale_3.125.aep")
for item in app.project.items:
    item_id = getattr(item, "id", None)
    name = getattr(item, "name", None)
    typ = type(item).__name__
    has_layers = hasattr(item, "layers") and item.layers is not None
    nl = len(item.layers) if has_layers else 0
    print(f"  id={item_id} type={typ} name={name} layers={nl}")
