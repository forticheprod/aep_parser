"""Calculate time offsets."""
import sys
sys.path.insert(0, "src")
from pathlib import Path
import aep_parser

r = aep_parser.parse(Path("samples/bugs/29.97_fps_time_scale_3.125.aep"))
c = r.project.compositions[0]
layer = c.layers[0]

print(f"Layer: {layer.name}")
print(f"  in_point={layer.in_point}")
print(f"  out_point={layer.out_point}")
print(f"  start_time={layer.start_time}")
tre = getattr(layer, "time_remap_enabled", None)
print(f"  time_remap_enabled={tre}")
print(f"Comp time_scale={c.time_scale} fps={c.frame_rate}")
print(f"Comp display_start_time={c.display_start_time}")
print(f"Comp display_start_frame={c.display_start_frame}")
print()

# Parsed keyframe times and expected
parsed_times = [-0.3003002880688188, 3.43676996345426, 7.50750720172047]
expected_times = [6.50650650650651, 10.2435769102436, 14.3143143143143]

print("Time offset analysis:")
for pt, et in zip(parsed_times, expected_times):
    diff = et - pt
    print(f"  expected={et:.3f}  parsed={pt:.3f}  diff={diff:.3f}")

print(f"\nLayer start_time={layer.start_time}")
print(f"Diff matches start_time? {abs(expected_times[0] - parsed_times[0] - layer.start_time) < 0.1}")

# Frame calculation
print(f"\nFrame time analysis (time_scale={c.time_scale}):")
for pt in parsed_times:
    raw = pt * c.frame_rate
    print(f"  parsed_t={pt:.3f} -> frame={raw:.1f}")
for et in expected_times:
    raw = et * c.frame_rate
    print(f"  expected_t={et:.3f} -> frame={raw:.1f}")
