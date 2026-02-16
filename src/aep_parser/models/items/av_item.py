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

    _used_in: set[CompItem] = field(default_factory=set, init=False, repr=False)

    @property
    def used_in(self) -> list[CompItem]:
        """All the compositions that use this AVItem."""
        return list(self._used_in)

    @property
    def footage_missing(self) -> bool:
        """
        When `True`, the AVItem is a placeholder, or represents footage with a
        source file that cannot be found. In this case, the path of the
        missing source file is in the `missing_footage_path` attribute of the
        footage item's source-file object.
        See [FootageItem.main_source][aep_parser.models.items.footage.FootageItem.main_source] and
        [FileSource.missing_footage_path][aep_parser.models.sources.file.FileSource.missing_footage_path].
        """
        if not hasattr(self, "main_source"):
            return False
        source = self.main_source
        if hasattr(source, "missing_footage_path"):
            return bool(source.missing_footage_path)
        return False
