from __future__ import (
    absolute_import,
    unicode_literals,
    division
)
from builtins import str


class Keyframe(object):
    def __init__(self, time=0, keyframe_interpolation_type=None, label=None,
                 continuous_bezier=False, auto_bezier=False, roving_across_time=False):
        """
        Keyframe of a property.
        """
        self.time = time
        self.keyframe_interpolation_type = keyframe_interpolation_type
        self.label = label
        self.continuous_bezier = continuous_bezier
        self.auto_bezier = auto_bezier
        self.roving_across_time = roving_across_time

    def __repr__(self):
        return str(self.__dict__)
