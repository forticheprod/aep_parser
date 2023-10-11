class Project(object):
    def __init__(self,
                 bits_per_channel, effect_names, expression_engine, frame_rate, items,
                 ae_version=None, xmp_packet=None, root_folder=None):
        """
        After Effects project file
        """
        self.ae_version = ae_version
        self.bits_per_channel = bits_per_channel
        # TODO displayStartFrame
        self.effect_names = effect_names
        self.expression_engine = expression_engine
        # TODO file
        # TODO footageTimecodeDisplayStartType
        self.frame_rate = frame_rate
        # TODO framesCountType
        self.items = items
        self.root_folder = root_folder
        self.xmp_packet = xmp_packet
        self._items_by_uid = None
        self._layers_by_uid = None

    def __repr__(self):
        return str(self.__dict__)

    def item_by_id(self, item_id):
        if self._items_by_uid is None:
            self._items_by_uid = {
                item.item_id: item
                for item in self.items
            }
        return self._items_by_uid[item_id]

    def layer_by_id(self, layer_id):
        if self._layers_by_uid is None:
            self._layers_by_uid = {
                layer.layer_id: layer
                for item in self.items.values()
                for layer in item.layers
            }
        return self._layers_by_uid[layer_id]
