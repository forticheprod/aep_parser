from .item import Item


class Asset(Item):
    def __init__(
            self,
            width=0,
            height=0,
            framerate=0.0,
            duration_sec=0.0,
            duration_frames=0,
            asset_type=None,
            start_frame=0,
            end_frame=0,
            *args,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.height = height
        self.framerate = framerate
        self.duration_sec = duration_sec
        self.duration_frames = duration_frames
        self.asset_type = asset_type
        self.start_frame = start_frame,
        self.end_frame = end_frame,
