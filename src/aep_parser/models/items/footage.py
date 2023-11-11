from .av_item import AVItem


class FootageItem(AVItem):
    def __init__(self,
                 main_source, asset_type, end_frame, start_frame,
                 *args, **kwargs):
        super(FootageItem, self).__init__(*args, **kwargs)
        self.main_source = main_source
        self.asset_type = asset_type
        self.end_frame = end_frame
        self.start_frame = start_frame

    @property
    def file(self):
        try:
            return self.main_source.file
        except AttributeError:
            return None

    @property
    def is_composition(self):
        return False

    @property
    def is_folder(self):
        return False

    @property
    def is_footage(self):
        return True
