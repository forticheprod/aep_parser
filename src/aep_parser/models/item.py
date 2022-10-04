class Item(object):
    def __init__(self, name="", item_id=0, item_type=None, folder_contents=[],
                 footage_dimensions=[0, 0], footage_framerate=0.0, footage_seconds=0.0,
                 footage_type=None, background_color=[], composition_layers=[]):
        """
        Generalized object storing information about folders, compositions, or footage
        """
        self.name = name
        self.item_id = item_id
        self.item_type = item_type
        self.folder_contents = folder_contents
        self.footage_dimensions = footage_dimensions
        self.footage_framerate = footage_framerate
        self.footage_seconds = footage_seconds
        self.footage_type = footage_type
        self.background_color = background_color
        self.composition_layers = composition_layers

    def __repr__(self):
        return str(self.__dict__)
