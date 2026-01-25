from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from ...kaitai.aep import Aep


class Keyframe:
    def __init__(
        self,
        frame_time: int = 0,
        keyframe_interpolation_type: Aep.KeyframeInterpolationType | None = None,
        label: Aep.Label | None = None,
        continuous_bezier: bool = False,
        auto_bezier: bool = False,
        roving_across_time: bool = False,
    ):
        """
        Keyframe of a property.

        Args:
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
        self.frame_time = frame_time
        self.keyframe_interpolation_type = keyframe_interpolation_type
        self.label = label
        self.continuous_bezier = continuous_bezier
        self.auto_bezier = auto_bezier
        self.roving_across_time = roving_across_time

    def __repr__(self) -> str:
        return str(self.__dict__)
