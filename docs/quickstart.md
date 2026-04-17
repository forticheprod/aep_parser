# Quick Start

## Parse a project

```python
import py_aep

app = py_aep.parse("myproject.aep")
project = app.project

print(f"AE version: {app.version}")
print(f"Bits per channel: {project.bits_per_channel}")
```

## Iterate over items and layers

```python
for item in project:
    print(f"{item.name} ({type(item).__name__})")

for comp in project.compositions:
    print(f"Composition: {comp.name} ({comp.width}x{comp.height})")
    for layer in comp:
        print(f"  Layer: {layer.name}")
```

## Access layer properties

```python
layer = comp.layers[0]
transform = layer.property("ADBE Transform Group")  # By match name
opacity = transform.opacity  # Or using attributes
print(f"Opacity: {opacity.value}")

# Check for keyframes
if opacity.is_time_varying:
    for kf in opacity.keyframes:
        print(f"  Key at {kf.time}s: {kf.value}")
```

## Access footage sources

```python
for layer in comp.footage_layers:
    print(f"  File: {layer.source.file}")
```

## Inspect the render queue

```python
for rq_item in project.render_queue:
    print(f"Status: {rq_item.status}")
    print(f"Settings: {rq_item.settings}")
    for om in rq_item:
        print(f"  Format: {om.settings['Format']}")
```

## Modify and save

```python
app = py_aep.parse("myproject.aep")
project = app.project
comp = project.compositions[0]

# Change composition settings
comp.name = "Final Comp"
comp.frame_rate = 30

# Modify a layer property
layer = comp.layers[0]
opacity = layer.transform.opacity
opacity.value = 50

# Save to a new file (produces a byte-identical RIFX structure)
project.save("modified.aep")
```
