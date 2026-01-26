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
    Footage item.

    Attributes:
        main_source: The footage source.
        asset_type: The footage type (placeholder, solid, file).
        end_frame: The footage end frame.
        start_frame: The footage start frame.
    """

    main_source: FileSource | SolidSource | PlaceholderSource
    asset_type: str
    end_frame: int
    start_frame: int

    @property
    def file(self) -> str | None:
        """The footage file path if its source is a FileSource, else None."""
        try:
            return self.main_source.file
        except AttributeError:
            return None
