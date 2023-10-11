from .av_item import AVItem


class FootageItem(AVItem):
    def __init__(self,
                 asset_type=None, duration_frames=0, duration_sec=0.0, end_frame=0,
                 framerate=0.0, height=0, start_frame=0, width=0,
                 *args, **kwargs):
        super(FootageItem, self).__init__(*args, **kwargs)
        self.width = width
        self.height = height
        self.framerate = framerate
        self.duration_sec = duration_sec
        self.duration_frames = duration_frames
        self.asset_type = asset_type
        self.start_frame = start_frame
        self.end_frame = end_frame
