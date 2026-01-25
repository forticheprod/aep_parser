from __future__ import annotations

import typing

from .av_item import AVItem

if typing.TYPE_CHECKING:
    from ..sources.file import FileSource
    from ..sources.placeholder import PlaceholderSource
    from ..sources.solid import SolidSource


class FootageItem(AVItem):
    def __init__(
        self,
        main_source: FileSource | SolidSource | PlaceholderSource,
        asset_type: str,
        end_frame: int,
        start_frame: int,
        *args,
        **kwargs,
    ):
        """
        Footage item.

        Args:
            main_source: The footage source.
            asset_type: The footage type (placeholder, solid, file).
            end_frame: The footage end frame.
            start_frame: The footage start frame.
        """
        super().__init__(*args, **kwargs)
        self.main_source = main_source
        self.asset_type = asset_type
        self.end_frame = end_frame
        self.start_frame = start_frame

    @property
    def file(self) -> str | None:
        """The footage file path if its source is a FileSource, else None."""
        try:
            return self.main_source.file
        except AttributeError:
            return None
