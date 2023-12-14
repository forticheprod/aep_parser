from __future__ import absolute_import, unicode_literals, division
import os
from builtins import str
from .item import Item


class AVItem(Item):
    def __init__(
        self,
        duration,
        frame_duration,
        frame_rate,
        height,
        pixel_aspect,
        width,
        *args,
        **kwargs
    ):
        """
        Generalized object storing information about compositions or footages
        Args:
            duration (float): The duration of the item in seconds. Still fotages have a
                              duration of 0.
            frame_duration (int): The duration of the item in frames. Still fotages have a
                                  duration of 0.
            frame_rate (float): The frame rate of the item in frames-per-second.
            height (int): The height of the item in pixels.
            pixel_aspect (float): The pixel aspect ratio of the item (1.0 is square).
            width (int): The width of the item in pixels.
        """
        super(AVItem, self).__init__(*args, **kwargs)
        self.duration = duration
        self.frame_duration = frame_duration
        self.frame_rate = frame_rate
        self.height = height
        self.pixel_aspect = pixel_aspect
        self.width = width
        # I did not implement self.used_in as this would cause infinite recursion when
        # trying to print the object and we would have to override repr,
        # copy.deepcopy(self.__dict__) then override used_in and it slows things down
        # quite a bit

    def __repr__(self):
        """
        Returns:
            str: string representation of the object's attributes
        """
        return str(self.__dict__)

    @property
    def footage_missing(self):
        """
        Returns:
            str: footage file path if the footage is missing
        """
        if not os.path.isfile(self.file):
            return self.file
