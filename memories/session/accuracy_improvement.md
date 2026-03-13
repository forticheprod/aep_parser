# value_at_time accuracy improvement - session state

## Task
Reduce error thresholds for Property.value_at_time() interpolation.

## Files Modified
- `src/aep_parser/models/properties/interpolation.py` - Main interpolation module
- `tests/test_value_at_time.py` - Pytest tests with thresholds

## COMPLETED: Temporal Auto-Bezier Fix (0.74 → 0.0000 EXACT!)
Changed `_compute_auto_temporal_ease()` to use Catmull-Rom derivative:
- Interior: `slope = (v_next - v_prev) / (t_next - t_prev)` (signed)
- Endpoints: signed slope (removed abs())
- ALREADY APPLIED AND VERIFIED: keyframe_temporal_auto_bezier now shows 0.0000 error

## Current Error Levels (POST temporal fix)
- temporal_auto_bezier: 0.0000 EXACT ✅ (was 0.74)
- spatial_auto_bezier: 0.2626 CLOSE (needs improvement)
- ~8 spatial OK samples: 0.01-0.015 (baseline, unfixable - systematic AE precision)
- 23 EXACT samples: < 0.01

## REMAINING: Spatial Auto-Bezier Improvement
Current code in `_compute_auto_spatial_tangents()` uses empirical scales:
- Endpoints: 0.20 (first/last keyframe tangent toward neighbor)
- Interior: 0.34 (dt-weighted Catmull-Rom direction)
- The spatial_auto_bezier sample has 3 KFs: [50,250,0], [150,50,0], [250,250,0]
- All tangents stored as [0,0,0], all ease=(0,0)
- Need to try different tangent scale factors and formulas

## Spatial Auto-Bezier Approach Ideas
1. Try matching Catmull-Rom scale 1/3 for all (was tested: 40532 error → WORSE bc of eval_segment bug in test script)
2. Actually AE might use the same Catmull-Rom 1/6th for spatial tangents as temporal (since 16.667% = 1/6)
3. Grid search: tried ep=0.20 ip=0.34 gives 0.26 max error in the REAL implementation

## What Still Needs Doing
1. ✅ Applied Catmull-Rom fix for temporal auto-bezier
2. ✅ Verified temporal fix (0.0000 error)
3. Try to improve spatial auto-bezier (current max 0.26)
4. Move temporal_auto_bezier from _CLOSE_SAMPLES to _OK_SAMPLES (or even remove from both since it's EXACT)
5. Update test thresholds in tests/test_value_at_time.py
6. Run quality checks: pytest, mypy, ruff, mkdocs
7. Clean up tmp files

## Test File Structure: tests/test_value_at_time.py
```python
_OK_SAMPLES = [...]  # max error < 0.1 threshold
_CLOSE_SAMPLES = [   # max error < 1.0 threshold
    "keyframe_spatial_auto_bezier",
    "keyframe_temporal_auto_bezier",  # MOVE TO OK or EXACT
]
class TestValueAtTimeOK:  # asserts max_err < 0.1
class TestValueAtTimeCLOSE:  # asserts max_err < 1.0
class TestValueAtTimeAPI:  # NotImplementedError, static value tests
```

## Temp Files to Clean
tmp_measure_errors.py, tmp_test_catmull.py, tmp_spatial_catmull.py,
tmp_arc_resolution.py, tmp_value_precision.py, tmp_linear_debug.py,
tmp_analyze_auto.py, tmp_auto_output.txt
