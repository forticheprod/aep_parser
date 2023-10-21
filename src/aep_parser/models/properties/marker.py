from __future__ import (
    absolute_import,
    unicode_literals,
    division
)
from builtins import str


class Marker(object):
    def __init__(self,
                 chapter, comment, cue_point_name, duration, navigation, frame_target,
                 url, label, protected_region, params, frame_duration, time=None):
        """
        Marker object of a layer.
        """
        self.chapter = chapter
        self.comment = comment
        self.cue_point_name = cue_point_name
        self.duration = duration
        self.navigation = navigation
        self.event_cue_point = not(navigation)
        self.frame_target = frame_target
        self.url = url
        self.label = label
        self.protected_region = protected_region
        self.params = params

        self.frame_duration = frame_duration
        self.time = time

    def __repr__(self):
        return str(self.__dict__)
