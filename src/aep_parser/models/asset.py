from aep_parser.models.item import Item


class Asset(Item):
    def __init__(
            self,
            width=0,
            height=0,
            framerate=0.0,
            duration_sec=0.0,
            *args,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.height = height
        self.framerate = framerate
        self.duration_sec = duration_sec
