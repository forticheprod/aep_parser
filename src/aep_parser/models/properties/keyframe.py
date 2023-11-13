from __future__ import (
    absolute_import,
    unicode_literals,
    division
)
from builtins import str


class Keyframe(object):
    def __init__(self, frame_time=0, keyframe_interpolation_type=None, label=None,
                 continuous_bezier=False, auto_bezier=False, roving_across_time=False):
        """
        Keyframe of a property.
        Args:
            frame_time (int): Time of the keyframe, in frames.
            keyframe_interpolation_type (Aep.KeyframeInterpolationType):
                interpolation type for the specified keyframe.
            label (Aep.MarkerLabel): The label color. Colors are represented by their
                                     number (0 for None, or 1 to 16 for one of the
                                     preset colors in the Labels preferences).
            continuous_bezier (bool): True if the specified keyframe has temporal
                                      continuity.
            auto_bezier (bool): True if the specified keyframe has spatial auto-Bezier
                                interpolation.
            roving_across_time (bool): True if the specified keyframe is roving. The
                                       first and last keyframe in a property cannot
                                       rove.
        """
        self.frame_time = frame_time
        self.keyframe_interpolation_type = keyframe_interpolation_type
        self.label = label
        self.continuous_bezier = continuous_bezier
        self.auto_bezier = auto_bezier
        self.roving_across_time = roving_across_time

    def __repr__(self):
        """
        Returns:
            str: String representation of the keyframe.
        """
        return str(self.__dict__)
