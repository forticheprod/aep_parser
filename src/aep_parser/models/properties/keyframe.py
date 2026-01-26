from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from ...kaitai.aep import Aep


@dataclass
class Keyframe:
    """
    Keyframe of a property.

    Attributes:
        frame_time: Time of the keyframe, in frames.
        keyframe_interpolation_type: Interpolation type for the specified
            keyframe.
        label: The label color. Colors are represented by their number
            (0 for None, or 1 to 16 for one of the preset colors in the
            Labels preferences).
        continuous_bezier: True if the specified keyframe has temporal
            continuity.
        auto_bezier: True if the specified keyframe has spatial auto-Bezier
            interpolation.
        roving_across_time: True if the specified keyframe is roving. The
            first and last keyframe in a property cannot rove.
    """

    frame_time: int = 0
    keyframe_interpolation_type: Aep.KeyframeInterpolationType | None = None
    label: Aep.Label | None = None
    continuous_bezier: bool = False
    auto_bezier: bool = False
    roving_across_time: bool = False
