# coding: utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
    division
)
from builtins import str


class Layer(object):
    def __init__(self,
                 auto_orient, comment, effects, enabled, frame_in_point,
                 frame_out_point, frame_start_time, in_point, label, layer_id, locked,
                 markers, name, null_layer, out_point, parent_id, start_time, shy, solo,
                 stretch, text, time, transform, containing_comp_id=None):
        """
        Base class for layers.
        Args:
            auto_orient (bool): The type of automatic orientation to perform for the
                                layer.
            comment (str): A descriptive comment for the layer.
            containing_comp_id (int): The ID of the composition that contains this layer
            effects (list[PropertyGroup]): Contains a layer's effects (if any).
            enabled (bool): Corresponds to the video switch state of the layer in the
                            Timeline panel
            frame_in_point (int): The "in" point of the layer, expressed in composition
                                  time (frames).
            frame_out_point (int): The "out" point of the layer, expressed in
                                   composition time (frames).
            frame_start_time (int): The start time of the layer, expressed in
                                    composition time (frames).
            in_point (float): The "in" point of the layer, expressed in composition time
                              (seconds).
            label (Aep.MarkerLabel): The label color. Colors are represented by their
                                     number (0 for None, or 1 to 16 for one of the
                                     preset colors in the Labels preferences).
            layer_id (int): Unique and persistent identification number used internally
                            to identify a Layer between sessions.
            locked (bool): When true, the layer is locked. This corresponds to the lock
                           toggle in the Layer panel.
            markers (list[Marker]): Contains a layer's markers.
            name (str): The name of the layer.
            null_layer (bool): When true, the layer was created as a null object
            out_point (float): The "out" point of the layer, expressed in composition
                               time (seconds).
            parent_id (int): The ID of the layer's parent layer. None if the layer has
                             no parent.
            shy (bool): When true, the layer is "shy", meaning that it is hidden in the
                        Layer panel if the composition's "Hide all shy layers" option is
                        toggled on.
            solo (bool): When true, the layer is soloed.
            start_time (float): The start time of the layer, expressed in composition
                                time (seconds).
            stretch (float): The layer's time stretch, expressed as a percentage. A
                             value of 100 means no stretch. Values between 0 and 1 are
                             set to 1, and values between -1 and 0 (not including 0) are
                             set to -1.
            text (PropertyGroup): Contains a layer's text properties (if any).
            time (float): The current time of the layer, expressed in composition time
                          (seconds).
            transform (list[Property]): Contains a layer's transform properties
        """
        self.enabled = enabled
        self.auto_orient = auto_orient
        self.comment = comment
        self.frame_in_point = frame_in_point
        self.frame_out_point = frame_out_point
        self.frame_start_time = frame_start_time
        self.in_point = in_point
        self.is_name_set = bool(name)
        self.layer_id = layer_id
        self.label = label
        self.locked = locked
        self.name = name
        self.null_layer = null_layer
        self.out_point = out_point
        self.parent_id = parent_id
        self.shy = shy
        self.solo = solo
        self.start_time = start_time
        self.stretch = stretch
        self.time = time
        self.transform = transform
        self.effects = effects
        self.text = text
        self.markers = markers
        self.containing_comp_id = containing_comp_id

    def __repr__(self):
        """
        Returns:
            str: A string representation of the object.
        """
        return str(self.__dict__)
