from .footage import FootageSource


class SolidSource(FootageSource):
    def __init__(self, color, *args, **kwargs):
        super(SolidSource, self).__init__(*args, **kwargs)
        self.color = color
