"""Interpolation utilities for keyframe-based property evaluation.

Implements HOLD, LINEAR, and BEZIER interpolation for
``Property.value_at_time()``. Pure Python with no external dependencies.
"""

from __future__ import annotations

import math
import typing
from typing import cast

from aep_parser.enums import KeyframeInterpolationType

if typing.TYPE_CHECKING:
    from aep_parser.models.properties.keyframe import Keyframe
    from aep_parser.models.properties.keyframe_ease import KeyframeEase

_DEFAULT_INFLUENCE = 100.0 / 6.0  # 16.6667 %

# ---------------------------------------------------------------------------
# Low-level bezier helpers
# ---------------------------------------------------------------------------


def _cubic_bezier(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
    """Evaluate a 1D cubic Bezier at parameter *t* in [0, 1]."""
    u = 1.0 - t
    return u * u * u * p0 + 3.0 * u * u * t * p1 + 3.0 * u * t * t * p2 + t * t * t * p3


def _cubic_bezier_derivative(
    p0: float, p1: float, p2: float, p3: float, t: float
) -> float:
    """First derivative of a 1D cubic Bezier at parameter *t*."""
    u = 1.0 - t
    return 3.0 * u * u * (p1 - p0) + 6.0 * u * t * (p2 - p1) + 3.0 * t * t * (p3 - p2)


def _solve_bezier_t(p0: float, p1: float, p2: float, p3: float, target: float) -> float:
    """Find *t* such that ``cubic_bezier(p0, p1, p2, p3, t) == target``.

    Uses Newton-Raphson with bisection fallback.  The curve is assumed
    to be monotonically increasing from *p0* to *p3*.
    """
    # Newton-Raphson
    t = 0.5
    for _ in range(16):
        v = _cubic_bezier(p0, p1, p2, p3, t) - target
        d = _cubic_bezier_derivative(p0, p1, p2, p3, t)
        if abs(d) < 1e-12:
            break
        t_new = t - v / d
        if 0.0 <= t_new <= 1.0:
            t = t_new
        else:
            break
        if abs(v) < 1e-10:
            return t

    # Bisection fallback
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) * 0.5
        v = _cubic_bezier(p0, p1, p2, p3, mid)
        if abs(v - target) < 1e-10:
            return mid
        if v < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) * 0.5


# ---------------------------------------------------------------------------
# Ease default helpers
# ---------------------------------------------------------------------------


def _effective_ease_1d(
    ease: KeyframeEase,
    default_speed: float,
) -> tuple[float, float]:
    """Return (speed, influence) using defaults when the binary stores 0.

    When ``setInterpolationTypeAtKey`` resets ease in AE, both speed
    and influence are stored as 0.  At runtime AE substitutes the
    segment's average speed and ~16.667 % influence.
    """
    inf = ease.influence
    spd = ease.speed
    if inf == 0.0:
        inf = _DEFAULT_INFLUENCE
        if spd == 0.0:
            spd = default_speed
    return spd, inf


def _bezier_arc_length(
    v0: list[float],
    v1: list[float],
    out_tan: list[float],
    in_tan: list[float],
) -> float:
    """Approximate the arc length of a spatial cubic Bezier path.

    Uses 16-point Gauss-Legendre quadrature on [0, 1].
    """
    ndim = len(v0)
    p1 = [v0[d] + out_tan[d] for d in range(ndim)]
    p2 = [v1[d] + in_tan[d] for d in range(ndim)]

    # 8-point Gauss-Legendre nodes & weights on [0, 1]
    _GL = [
        (0.01985507, 0.05061427),
        (0.10166676, 0.11119052),
        (0.23723379, 0.15685332),
        (0.40828268, 0.18134189),
        (0.59171732, 0.18134189),
        (0.76276621, 0.15685332),
        (0.89833324, 0.11119052),
        (0.98014493, 0.05061427),
    ]

    total = 0.0
    for node, weight in _GL:
        # B'(t) per dimension
        mag_sq = 0.0
        for d in range(ndim):
            deriv = _cubic_bezier_derivative(v0[d], p1[d], p2[d], v1[d], node)
            mag_sq += deriv * deriv
        total += weight * math.sqrt(mag_sq)
    return total


def _tangents_are_zero(tangent: list[float] | None) -> bool:
    if tangent is None:
        return True
    return all(abs(x) < 1e-12 for x in tangent)


def _bezier_speed(
    v0: list[float],
    p1: list[float],
    p2: list[float],
    v1: list[float],
    ndim: int,
    u: float,
) -> float:
    """Magnitude of the spatial Bezier derivative at parameter *u*."""
    mag_sq = 0.0
    for d in range(ndim):
        deriv = _cubic_bezier_derivative(v0[d], p1[d], p2[d], v1[d], u)
        mag_sq += deriv * deriv
    return math.sqrt(mag_sq)


def _arc_length_reparam(
    v0: list[float],
    v1: list[float],
    out_tan: list[float],
    in_tan: list[float],
    s: float,
) -> float:
    """Convert arc-length fraction *s* to Bezier parameter *u*.

    Builds a cumulative arc-length table via midpoint quadrature,
    then binary-searches for an initial estimate and refines with
    Newton-Raphson using Simpson's rule for local arc-length.
    """
    ndim = len(v0)
    p1 = [v0[d] + out_tan[d] for d in range(ndim)]
    p2 = [v1[d] + in_tan[d] for d in range(ndim)]

    n_seg = 128
    inv_n = 1.0 / n_seg
    # Cumulative arc length at u = i / n_seg
    table = [0.0] * (n_seg + 1)
    for i in range(1, n_seg + 1):
        um = (i - 0.5) * inv_n
        mag_sq = 0.0
        for d in range(ndim):
            deriv = _cubic_bezier_derivative(v0[d], p1[d], p2[d], v1[d], um)
            mag_sq += deriv * deriv
        table[i] = table[i - 1] + math.sqrt(mag_sq) * inv_n

    total = table[n_seg]
    if total < 1e-12:
        return s

    target = s * total

    # Binary search for the segment
    lo, hi = 0, n_seg
    while lo < hi - 1:
        mid = (lo + hi) >> 1
        if table[mid] < target:
            lo = mid
        else:
            hi = mid

    seg_start = table[lo]
    seg_end = table[hi]
    if seg_end - seg_start < 1e-12:
        u = float(hi) * inv_n
    else:
        frac = (target - seg_start) / (seg_end - seg_start)
        u = (lo + frac) * inv_n

    # Newton-Raphson refinement using the table + local Simpson's
    for _ in range(3):
        idx = u * n_seg
        idx_lo = min(int(idx), n_seg - 1)
        u_lo = idx_lo * inv_n
        u_rem = u - u_lo
        if u_rem < 1e-15:
            arc_at_u = table[idx_lo]
        else:
            # Simpson's rule on [u_lo, u]
            u_mid = u_lo + u_rem * 0.5
            fa = _bezier_speed(v0, p1, p2, v1, ndim, u_lo)
            fm = _bezier_speed(v0, p1, p2, v1, ndim, u_mid)
            fb = _bezier_speed(v0, p1, p2, v1, ndim, u)
            arc_at_u = table[idx_lo] + (fa + 4.0 * fm + fb) * u_rem / 6.0
        residual = arc_at_u - target
        speed = _bezier_speed(v0, p1, p2, v1, ndim, u)
        if speed < 1e-12:
            break
        du = residual / speed
        u -= du
        u = max(0.0, min(1.0, u))
        if abs(du) < 1e-12:
            break

    return u


# ---------------------------------------------------------------------------
# Auto-bezier computation
# ---------------------------------------------------------------------------


def _compute_auto_spatial_tangents(
    keyframes: list[Keyframe],
) -> list[tuple[list[float] | None, list[float] | None]]:
    """Compute spatial tangents for keyframes with ``spatial_auto_bezier``.

    Returns a list of (out_tangent, in_tangent) per keyframe.  Non-auto
    keyframes return the stored tangent values unchanged.
    """
    n = len(keyframes)
    result: list[tuple[list[float] | None, list[float] | None]] = []

    for i in range(n):
        kf = keyframes[i]
        is_auto = getattr(kf, "spatial_auto_bezier", False)
        out_tan = kf.out_spatial_tangent
        in_tan = kf.in_spatial_tangent

        if not is_auto or not isinstance(kf.value, list):
            result.append((out_tan, in_tan))
            continue

        # Only compute if tangents are zero (AE didn't store them)
        if not _tangents_are_zero(out_tan) or not _tangents_are_zero(in_tan):
            result.append((out_tan, in_tan))
            continue

        ndim = len(kf.value)

        if n == 1:
            result.append(([0.0] * ndim, [0.0] * ndim))
            continue

        # Catmull-Rom tangent scales: 1/6 for endpoints, 1/3 with
        # dt-weighting for interior (standard Kochanek-Bartels form).
        _EP_SCALE = 1.0 / 6.0
        _INT_SCALE = 1.0 / 3.0

        if i == 0:
            # First KF: tangent toward next
            nxt_val = keyframes[1].value
            if isinstance(nxt_val, list):
                out_t = [(nxt_val[d] - kf.value[d]) * _EP_SCALE for d in range(ndim)]
            else:
                out_t = [0.0] * ndim
            result.append((out_t, [0.0] * ndim))
        elif i == n - 1:
            # Last KF: tangent from previous
            prv_val = keyframes[i - 1].value
            if isinstance(prv_val, list):
                in_t = [-(kf.value[d] - prv_val[d]) * _EP_SCALE for d in range(ndim)]
            else:
                in_t = [0.0] * ndim
            result.append(([0.0] * ndim, in_t))
        else:
            # Interior: Catmull-Rom with dt-weighting
            prv = keyframes[i - 1]
            nxt = keyframes[i + 1]
            if not isinstance(prv.value, list) or not isinstance(nxt.value, list):
                result.append(([0.0] * ndim, [0.0] * ndim))
                continue

            dt_left = kf.time - prv.time
            dt_right = nxt.time - kf.time
            dt_sum = dt_left + dt_right
            if dt_sum < 1e-12:
                result.append(([0.0] * ndim, [0.0] * ndim))
                continue

            direction = [nxt.value[d] - prv.value[d] for d in range(ndim)]
            in_t = [-direction[d] * dt_left / dt_sum * _INT_SCALE for d in range(ndim)]
            out_t = [direction[d] * dt_right / dt_sum * _INT_SCALE for d in range(ndim)]
            result.append((out_t, in_t))

    return result


def _compute_auto_temporal_ease(
    keyframes: list[Keyframe],
) -> list[tuple[float, float, float, float]]:
    """Compute temporal ease for keyframes with ``temporal_auto_bezier``.

    Returns a list of (out_speed, out_influence, in_speed, in_influence)
    per keyframe.  Non-auto keyframes return the stored values.
    """
    n = len(keyframes)
    result: list[tuple[float, float, float, float]] = []

    for i in range(n):
        kf = keyframes[i]
        is_auto = getattr(kf, "temporal_auto_bezier", False)
        out_e = kf.out_temporal_ease[0] if kf.out_temporal_ease else None
        in_e = kf.in_temporal_ease[0] if kf.in_temporal_ease else None

        # Default: pass through stored values
        out_spd = out_e.speed if out_e else 0.0
        out_inf = out_e.influence if out_e else 0.0
        in_spd = in_e.speed if in_e else 0.0
        in_inf = in_e.influence if in_e else 0.0

        if not is_auto or (out_inf > 0.0 or in_inf > 0.0):
            result.append((out_spd, out_inf, in_spd, in_inf))
            continue

        v = kf.value
        v_scalar = v if isinstance(v, (int, float)) else None

        if v_scalar is None:
            # Multi-dim non-spatial: not handled
            result.append((out_spd, out_inf, in_spd, in_inf))
            continue

        if i == 0 and n > 1:
            nv = keyframes[1].value
            dt = keyframes[1].time - kf.time
            if isinstance(nv, (int, float)) and dt > 0:
                out_spd = (float(nv) - float(v_scalar)) / dt
            out_inf = _DEFAULT_INFLUENCE
            in_inf = _DEFAULT_INFLUENCE
        elif i == n - 1 and n > 1:
            pv = keyframes[i - 1].value
            dt = kf.time - keyframes[i - 1].time
            if isinstance(pv, (int, float)) and dt > 0:
                in_spd = (float(v_scalar) - float(pv)) / dt
            in_inf = _DEFAULT_INFLUENCE
            out_inf = _DEFAULT_INFLUENCE
        else:
            # Interior: Catmull-Rom derivative through adjacent
            pv = keyframes[i - 1].value
            nv = keyframes[i + 1].value
            dt_total = keyframes[i + 1].time - keyframes[i - 1].time
            if (
                isinstance(pv, (int, float))
                and isinstance(nv, (int, float))
                and dt_total > 0
            ):
                slope = (float(nv) - float(pv)) / dt_total
                out_spd = slope
                in_spd = slope
            out_inf = _DEFAULT_INFLUENCE
            in_inf = _DEFAULT_INFLUENCE

        result.append((out_spd, out_inf, in_spd, in_inf))

    return result


# ---------------------------------------------------------------------------
# Segment interpolation
# ---------------------------------------------------------------------------


def _interpolate_bezier_1d(
    t: float,
    t0: float,
    t1: float,
    v0: float,
    v1: float,
    out_ease: KeyframeEase,
    in_ease: KeyframeEase,
    out_override: tuple[float, float] | None = None,
    in_override: tuple[float, float] | None = None,
) -> float:
    """Interpolate a single dimension using cubic Bezier temporal ease.

    *out_override* / *in_override* are optional ``(speed, influence)``
    tuples that replace the stored ease when auto-bezier is active.
    """
    dt = t1 - t0
    if dt == 0:
        return v0

    if out_override is not None:
        o_spd, o_inf = out_override
    else:
        o_spd, o_inf = out_ease.speed, out_ease.influence
    if in_override is not None:
        i_spd, i_inf = in_override
    else:
        i_spd, i_inf = in_ease.speed, in_ease.influence

    out_inf_frac = o_inf / 100.0
    in_inf_frac = i_inf / 100.0

    # Bezier in (time, value) space
    cp1_t = t0 + out_inf_frac * dt
    cp1_v = v0 + o_spd * out_inf_frac * dt

    cp2_t = t1 - in_inf_frac * dt
    cp2_v = v1 - i_spd * in_inf_frac * dt

    s = _solve_bezier_t(t0, cp1_t, cp2_t, t1, t)
    return _cubic_bezier(v0, cp1_v, cp2_v, v1, s)


def _interpolate_spatial_bezier(
    t: float,
    t0: float,
    t1: float,
    kf0: Keyframe,
    kf1: Keyframe,
    out_tan_override: list[float] | None = None,
    in_tan_override: list[float] | None = None,
) -> list[float]:
    """Interpolate a spatial property along a cubic Bezier path.

    The spatial path uses keyframe values as endpoints and spatial
    tangent vectors as control point offsets.  The temporal ease maps
    time to a *progress* parameter along the path.

    *out_tan_override* / *in_tan_override* replace stored tangents when
    auto-bezier tangent computation is needed.
    """
    v0 = kf0.value
    v1 = kf1.value
    if not isinstance(v0, list) or not isinstance(v1, list):
        return list(v0) if isinstance(v0, list) else [float(v0)]  # type: ignore[arg-type]

    dt = t1 - t0
    if dt == 0:
        return list(v0)

    ndim = len(v0)
    out_tan = out_tan_override or kf0.out_spatial_tangent or [0.0] * ndim
    in_tan = in_tan_override or kf1.in_spatial_tangent or [0.0] * ndim
    straight_path = _tangents_are_zero(out_tan) and _tangents_are_zero(in_tan)

    # Temporal ease (scalar for spatial properties)
    out_ease = kf0.out_temporal_ease[0] if kf0.out_temporal_ease else None
    in_ease = kf1.in_temporal_ease[0] if kf1.in_temporal_ease else None

    # Build temporal bezier in (time, progress) space
    has_explicit_ease = (
        out_ease is not None
        and in_ease is not None
        and (out_ease.influence > 0 or in_ease.influence > 0)
    )
    if has_explicit_ease:
        assert out_ease is not None and in_ease is not None
        out_inf_frac = out_ease.influence / 100.0
        in_inf_frac = in_ease.influence / 100.0

        if straight_path:
            seg_dist = math.sqrt(sum((v1[d] - v0[d]) ** 2 for d in range(ndim)))
            path_deriv_mag_0 = seg_dist
            path_deriv_mag_1 = seg_dist
        else:
            # |B'(0)| = 3 * |P1 - P0|, |B'(1)| = 3 * |P3 - P2|
            p1 = [v0[d] + out_tan[d] for d in range(ndim)]
            p2 = [v1[d] + in_tan[d] for d in range(ndim)]
            path_deriv_mag_0 = 3.0 * math.sqrt(
                sum((p1[d] - v0[d]) ** 2 for d in range(ndim))
            )
            path_deriv_mag_1 = 3.0 * math.sqrt(
                sum((v1[d] - p2[d]) ** 2 for d in range(ndim))
            )

        # ds/dt at endpoints (speed in px/s divided by |B'(s)| in px/unit-s)
        ds_dt_0 = out_ease.speed / path_deriv_mag_0 if path_deriv_mag_0 > 1e-12 else 0.0
        ds_dt_1 = in_ease.speed / path_deriv_mag_1 if path_deriv_mag_1 > 1e-12 else 0.0

        cp1_time = t0 + out_inf_frac * dt
        cp1_s = 0.0 + ds_dt_0 * out_inf_frac * dt

        cp2_time = t1 - in_inf_frac * dt
        cp2_s = 1.0 - ds_dt_1 * in_inf_frac * dt

        cp1_s = max(0.0, min(1.0, cp1_s))
        cp2_s = max(0.0, min(1.0, cp2_s))

        u = _solve_bezier_t(t0, cp1_time, cp2_time, t1, t)
        s = _cubic_bezier(0.0, cp1_s, cp2_s, 1.0, u)
    else:
        # No ease data → linear temporal
        s = (t - t0) / dt

    # Evaluate spatial path at parameter s
    if straight_path:
        return [v0[d] + (v1[d] - v0[d]) * s for d in range(ndim)]

    # Arc-length reparameterization: convert arc fraction s to bezier u
    u = _arc_length_reparam(v0, v1, out_tan, in_tan, s)
    result: list[float] = []
    for d in range(ndim):
        p0d = v0[d]
        p1d = v0[d] + out_tan[d]
        p2d = v1[d] + in_tan[d]
        p3d = v1[d]
        result.append(_cubic_bezier(p0d, p1d, p2d, p3d, u))
    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def interpolate_keyframes(
    time: float,
    keyframes: list[Keyframe],
    is_spatial: bool,
) -> list[float] | float | None:
    """Compute the interpolated value at *time* from a keyframe list.

    Args:
        time: Time in seconds.
        keyframes: Sorted list of keyframes.
        is_spatial: Whether the property is spatial.

    Returns:
        Interpolated value, or ``None`` if no keyframes.
    """
    if not keyframes:
        return None

    n = len(keyframes)

    # Before first keyframe or single keyframe
    if n == 1 or time <= keyframes[0].time:
        return cast("list[float] | float | None", keyframes[0].value)

    # After last keyframe
    if time >= keyframes[-1].time:
        return cast("list[float] | float | None", keyframes[-1].value)

    # Pre-compute auto-bezier tangents/ease (once per call)
    auto_tangents: list[tuple[list[float] | None, list[float] | None]] | None
    auto_ease: list[tuple[float, float, float, float]] | None

    has_auto_spatial = is_spatial and any(
        getattr(kf, "spatial_auto_bezier", False) for kf in keyframes
    )
    auto_tangents = (
        _compute_auto_spatial_tangents(keyframes) if has_auto_spatial else None
    )

    has_auto_temporal = any(
        getattr(kf, "temporal_auto_bezier", False) for kf in keyframes
    )
    auto_ease = _compute_auto_temporal_ease(keyframes) if has_auto_temporal else None

    # Find the segment: kf_left ... kf_right
    right_idx = 0
    for i in range(1, n):
        if keyframes[i].time >= time:
            right_idx = i
            break

    left_idx = right_idx - 1
    kf_left = keyframes[left_idx]
    kf_right = keyframes[right_idx]

    t0 = kf_left.time
    t1 = kf_right.time

    # At exactly a keyframe time, return that keyframe's value
    if abs(time - t0) < 1e-12:
        return cast("list[float] | float | None", kf_left.value)
    if abs(time - t1) < 1e-12:
        return cast("list[float] | float | None", kf_right.value)

    # Determine interpolation type for this segment
    out_type = kf_left.out_interpolation_type
    in_type = kf_right.in_interpolation_type

    # HOLD takes priority
    if out_type == KeyframeInterpolationType.HOLD:
        return cast("list[float] | float | None", kf_left.value)
    if in_type == KeyframeInterpolationType.HOLD:
        return cast("list[float] | float | None", kf_right.value)

    v0 = kf_left.value
    v1 = kf_right.value

    # LINEAR interpolation
    if out_type == KeyframeInterpolationType.LINEAR:
        ratio = (time - t0) / (t1 - t0)
        if isinstance(v0, list) and isinstance(v1, list):
            return [v0[d] + (v1[d] - v0[d]) * ratio for d in range(len(v0))]
        if isinstance(v0, (int, float)) and isinstance(v1, (int, float)):
            return float(v0) + (float(v1) - float(v0)) * ratio
        return cast("list[float] | float | None", v0)

    # BEZIER interpolation
    if out_type == KeyframeInterpolationType.BEZIER:
        if is_spatial and isinstance(v0, list) and isinstance(v1, list):
            # Get auto-bezier tangent overrides if available
            out_tan_ov: list[float] | None = None
            in_tan_ov: list[float] | None = None
            if auto_tangents:
                out_tan_ov = auto_tangents[left_idx][0]
                in_tan_ov = auto_tangents[right_idx][1]
            return _interpolate_spatial_bezier(
                time,
                t0,
                t1,
                kf_left,
                kf_right,
                out_tan_override=out_tan_ov,
                in_tan_override=in_tan_ov,
            )

        # Non-spatial: per-dimension 1D bezier
        # Get auto-ease overrides for this segment
        out_ov: tuple[float, float] | None = None
        in_ov: tuple[float, float] | None = None
        if auto_ease:
            ae_left = auto_ease[left_idx]
            ae_right = auto_ease[right_idx]
            out_ov = (ae_left[0], ae_left[1])  # out_speed, out_influence
            in_ov = (ae_right[2], ae_right[3])  # in_speed, in_influence

        if isinstance(v0, list) and isinstance(v1, list):
            result: list[float] = []
            for d in range(len(v0)):
                out_e = (
                    kf_left.out_temporal_ease[d]
                    if d < len(kf_left.out_temporal_ease)
                    else kf_left.out_temporal_ease[0]
                )
                in_e = (
                    kf_right.in_temporal_ease[d]
                    if d < len(kf_right.in_temporal_ease)
                    else kf_right.in_temporal_ease[0]
                )
                result.append(
                    _interpolate_bezier_1d(
                        time,
                        t0,
                        t1,
                        v0[d],
                        v1[d],
                        out_e,
                        in_e,
                        out_override=out_ov,
                        in_override=in_ov,
                    )
                )
            return result

        if isinstance(v0, (int, float)) and isinstance(v1, (int, float)):
            out_e_1d = (
                kf_left.out_temporal_ease[0] if kf_left.out_temporal_ease else None
            )
            in_e_1d = (
                kf_right.in_temporal_ease[0] if kf_right.in_temporal_ease else None
            )
            if out_e_1d and in_e_1d:
                return _interpolate_bezier_1d(
                    time,
                    t0,
                    t1,
                    float(v0),
                    float(v1),
                    out_e_1d,
                    in_e_1d,
                    out_override=out_ov,
                    in_override=in_ov,
                )
            # Fallback to linear if no ease data
            ratio = (time - t0) / (t1 - t0)
            return float(v0) + (float(v1) - float(v0)) * ratio

    # Fallback: return left value
    return cast("list[float] | float | None", v0)
