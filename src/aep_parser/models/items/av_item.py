import copy
import os
from .item import Item


class AVItem(Item):
    def __init__(self,
                 duration, frame_duration, frame_rate, height, pixel_aspect, width,
                 *args, **kwargs):
        """
        Generalized object storing information about compositions or footages
        Args:
            duration (float): The duration of the item in seconds.
            frame_duration (float): The duration of the item in seconds.
            frame_rate (float): The frame rate of the item in frames per second.
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
        self.used_in = []
        self.width = width

    def __repr__(self):
        attrs = copy.deepcopy(self.__dict__)
        # Collapse parent_folder to avoid infinite recursion
        if self.parent_folder is None:
            parent_folder = "<project>"
        else:
            parent_folder = "<'{parent_name}' folder>".format(
                parent_name=self.parent_folder.name
            )
        attrs["parent_folder"] = parent_folder
        # Collapse width to avoid infinite recursion
        attrs["used_in"] = [
            "<'{comp_name}' Composition>".format(comp_name=comp.name)
            for comp in self.used_in
        ]
        return str(attrs)

    @property
    def footage_missing(self):
        """
        Returns:
            str: footage file path if the footage is missing
        """
        if not os.path.isfile(self.file):
            return self.file

