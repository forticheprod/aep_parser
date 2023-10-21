from __future__ import (
    absolute_import,
    unicode_literals,
    division
)
from builtins import str


class Project(object):
    def __init__(self,
                 bits_per_channel, effect_names, expression_engine, file, frame_rate,
                 project_items, ae_version=None, xmp_packet=None):
        """
        After Effects project file
        """
        self.ae_version = ae_version
        self.bits_per_channel = bits_per_channel
        # TODO displayStartFrame
        self.effect_names = effect_names
        self.expression_engine = expression_engine
        self.file = file
        # TODO footageTimecodeDisplayStartType
        self.frame_rate = frame_rate
        # TODO framesCountType
        self.project_items = project_items
        self.xmp_packet = xmp_packet
        self._layers_by_uid = None

    def __repr__(self):
        return str(self.__dict__)

    def layer_by_id(self, layer_id):
        if self._layers_by_uid is None:
            self._layers_by_uid = {
                layer.layer_id: layer
                for item in self.project_items.values()
                for layer in item.layers
            }
        return self._layers_by_uid[layer_id]

    @property
    def root_folder(self):
        return self.project_items[0]
