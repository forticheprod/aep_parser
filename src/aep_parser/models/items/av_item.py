from __future__ import annotations

from dataclasses import dataclass

from .item import Item


@dataclass
class AVItem(Item):
    """
    Abstract base class storing information about compositions or footages.

    Attributes:
        duration: The duration of the item in seconds. Still footages have
            a duration of 0.
        frame_duration: The duration of the item in frames. Still footages
            have a duration of 0.
        frame_rate: The frame rate of the item in frames-per-second.
        height: The height of the item in pixels.
        pixel_aspect: The pixel aspect ratio of the item (1.0 is square).
        width: The width of the item in pixels.
    """

    duration: float
    frame_duration: int
    frame_rate: float
    height: int
    pixel_aspect: float
    width: int

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
