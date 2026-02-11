from __future__ import annotations

import typing
from dataclasses import dataclass

from .av_item import AVItem

if typing.TYPE_CHECKING:
    from ..sources.file import FileSource
    from ..sources.placeholder import PlaceholderSource
    from ..sources.solid import SolidSource


@dataclass
class FootageItem(AVItem):
    """
    The `FootageItem` object represents a footage item imported into a project,
    which appears in the Project panel.

    Info:
        `FootageItem` is a subclass of `AVItem` object, which is a subclass of
        `Item` object. All methods and attributes of `AVItem` and `Item` are
        available when working with `FootageItem`.

    See: https://ae-scripting.docsforadobe.dev/item/footageitem/
    """

    main_source: FileSource | SolidSource | PlaceholderSource
    """The footage source."""

    asset_type: str
    """The footage type (placeholder, solid, file)."""

    end_frame: int
    """The footage end frame."""

    start_frame: int
    """The footage start frame."""

    @property
    def file(self) -> str | None:
        """The footage file path if its source is a `FileSource`, else `None`."""
        if hasattr(self.main_source, "file"):
            return str(self.main_source.file)
        return None
