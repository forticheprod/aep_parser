class Project(object):
    def __init__(self,
                 bits_per_channel, effect_names, expression_engine, framerate, items,
                 ae_version=None, xmp_packet=None, root_folder=None):
        """
        After Effects project file
        """
        self.bits_per_channel = bits_per_channel
        self.effect_names = effect_names
        self.expression_engine = expression_engine
        self.framerate = framerate
        self.items = items
        self.ae_version = ae_version
        self.xmp_packet = xmp_packet
        self.root_folder = root_folder
        # TODO self.file = file
        # TODO self.display_start_frame = display_start_frame
        # TODO self.footage_timecode_display_start_type = footage_timecode_display_start_type
        # TODO self.frames_count_type = frames_count_type
        # TODO self.linear_blending = linear_blending
        # TODO self.linearize_working_space = linearize_working_space
        # TODO self.compensate_for_scene_referred_profiles = compensate_for_scene_referred_profiles
        # TODO self.working_gamma = working_gamma
        # TODO self.working_space = working_space
        self._items_by_id = dict()
        self._layers_by_id = dict()

    def __repr__(self):
        return str(self.__dict__)

    def item_by_id(self, item_id):
        if self._items_by_id is None:
            self._items_by_id = {
                item.item_id: item
                for item in self.items
            }
        return self._items_by_id[item_id]

    def layer_by_id(self, item_id):
        if self._layers_by_id is None:
            self._layers_by_id = {
                layer.layer_id: layer
                for item in self.items.values()
                for layer in item.composition_layers
            }
        return self._items_by_id[item_id]
