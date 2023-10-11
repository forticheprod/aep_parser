from .item import Item


class AVItem(Item):
    def __init__(self,
                 duration, frame_duration, frame_rate, height, pixel_aspect, width,
                 *args, **kwargs):
        """
        Generalized object storing information about folders, compositions, or footages
        """
        super(AVItem, self).__init__(*args, **kwargs)
        self.duration = duration
        self.frame_duration = frame_duration
        self.frame_rate = frame_rate
        self.height = height
        self.pixel_aspect = pixel_aspect
        # TODO usedIn
        self.width = width

    @property
    def footage_missing(self):
        # TODO
        pass