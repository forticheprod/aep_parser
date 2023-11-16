from .footage import FootageSource


class SolidSource(FootageSource):
    def __init__(self, color, *args, **kwargs):
        """
        Args:
            color (str): The solid color (RGBA).
        """
        super(SolidSource, self).__init__(*args, **kwargs)
        self.color = color

    @property
    def is_solid(self):
        """
        Returns:
            bool: True.
        """
        return True
