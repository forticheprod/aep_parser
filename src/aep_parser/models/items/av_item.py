from __future__ import annotations

import typing
from dataclasses import dataclass, field

from .item import Item

if typing.TYPE_CHECKING:
    from .composition import CompItem


@dataclass(eq=False)
class AVItem(Item):
    """
    The `AVItem` object provides access to attributes and methods of
    audio/visual files imported into After Effects.

    Info:
        `AVItem` is a subclass of [Item][]. All methods and attributes of [Item][]
        are available when working with `AVItem`.

    Info:
        `AVItem` is the base class for both [CompItem][] and [FootageItem][], so
        `AVItem` attributes and methods are also available when working with
        [CompItem][] and [FootageItem][] objects. See [CompItem][] object and
        [FootageItem][] object.

    See: https://ae-scripting.docsforadobe.dev/item/avitem/
    """

    duration: float
    """The duration of the item in seconds. Still footages have a duration of 0."""

    frame_duration: int
    """The duration of the item in frames. Still footages have a duration of 0."""

    frame_rate: float
    """The frame rate of the item in frames-per-second."""

    height: int
    """The height of the item in pixels."""

    pixel_aspect: float
    """The pixel aspect ratio of the item (1.0 is square)."""

    width: int
    """The width of the item in pixels."""

    footage_missing: bool = field(default=False, init=False)
    """
    When `True`, the AVItem is a placeholder, or represents footage with a
    source file that could not be found when the project was last saved.

    In this case, the path of the missing source file is in the
    `missing_footage_path` attribute of the footage item's source-file object.
    See [FootageItem.main_source][aep_parser.models.items.footage.FootageItem.main_source] and
    [FileSource.missing_footage_path][aep_parser.models.sources.file.FileSource.missing_footage_path].
    """

    _used_in: set[CompItem] = field(default_factory=set, init=False, repr=False)

    @property
    def has_video(self) -> bool:
        """`True` if the item has a video component.

        An AVItem has video when it has non-zero dimensions (`width > 0`
        and `height > 0`). In a [CompItem][], the value is always `True`.
        In a [FootageItem][aep_parser.models.items.footage.FootageItem],
        the value depends on the footage source (e.g. audio-only files
        return `False`).
        """
        return self.width > 0 and self.height > 0

    @property
    def used_in(self) -> list[CompItem]:
        """All the compositions that use this AVItem."""
        return list(self._used_in)
