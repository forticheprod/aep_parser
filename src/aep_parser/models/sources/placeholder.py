from .footage import FootageSource


class PlaceholderSource(FootageSource):
    def __init__(self, *args, **kwargs):
        super(PlaceholderSource, self).__init__(*args, **kwargs)
