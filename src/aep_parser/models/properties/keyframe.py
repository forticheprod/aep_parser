from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from ...kaitai import Aep
    from ..enums import KeyframeInterpolationType


@dataclass
class Keyframe:
    """
    The `Keyframe` object represents a keyframe of a property.

    Warning:
        `Keyframe` object does not exist in ExtendScript API. It has been added
        for convenience.
    """

    auto_bezier: bool
    """`True` if the specified keyframe has spatial auto-Bezier interpolation."""

    continuous_bezier: bool
    """`True` if the specified keyframe has temporal continuity."""

    frame_time: int
    """Time of the keyframe, in frames."""

    keyframe_interpolation_type: KeyframeInterpolationType
    """Interpolation type for the specified keyframe."""

    label: Aep.Label
    """
    The label color. Colors are represented by their number (0 for None, or 1
    to 16 for one of the preset colors in the Labels preferences).
    """

    roving_across_time: bool
    """
    `True` if the specified keyframe is roving. The first and last keyframe in
    a property cannot rove.
    """
