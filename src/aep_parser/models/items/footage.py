from .av_item import AVItem


class FootageItem(AVItem):
    def __init__(self,
                 file, main_source, asset_type, end_frame, start_frame,
                 *args, **kwargs):
        super(FootageItem, self).__init__(*args, **kwargs)
        self.file = file
        self.main_source = main_source
        self.asset_type = asset_type
        self.end_frame = end_frame
        self.start_frame = start_frame
