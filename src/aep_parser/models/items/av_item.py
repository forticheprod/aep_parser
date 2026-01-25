from __future__ import annotations

from .item import Item


class AVItem(Item):
    def __init__(
        self,
        duration: float,
        frame_duration: int,
        frame_rate: float,
        height: int,
        pixel_aspect: float,
        width: int,
        *args,
        **kwargs,
    ):
        """
        Generalized object storing information about compositions or footages.

        Args:
            duration: The duration of the item in seconds. Still fotages have
                a duration of 0.
            frame_duration: The duration of the item in frames. Still fotages
                have a duration of 0.
            frame_rate: The frame rate of the item in frames-per-second.
            height: The height of the item in pixels.
            pixel_aspect: The pixel aspect ratio of the item (1.0 is square).
            width: The width of the item in pixels.
        """
        super().__init__(*args, **kwargs)
        self.duration = duration
        self.frame_duration = frame_duration
        self.frame_rate = frame_rate
        self.height = height
        self.pixel_aspect = pixel_aspect
        self.width = width
        # I did not implement self.used_in as this would cause infinite recursion when
        # trying to print the object and we would have to override repr,
        # copy.deepcopy(self.__dict__) then override used_in and it slows things down
        # quite a bit

    def __repr__(self) -> str:
        """Return string representation of the object's attributes."""
        return str(self.__dict__)


    @property
    def footage_missing(self) -> bool:
        """
        When true, the AVItem is a placeholder, or represents footage with a
        source file that cannot be found. In this case, the path of the
        missing source file is in the missingFootagePath attribute of the
        footage item's source-file object. See FootageItem.main_source and
        FileSource.missing_footage_path.
        """
        try:
            return bool(self.main_source.missing_footage_path)
        except AttributeError:
            return False
