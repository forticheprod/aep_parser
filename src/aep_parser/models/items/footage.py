from __future__ import annotations

import typing

from .av_item import AVItem

if typing.TYPE_CHECKING:
    from aep_parser.enums import Label

    from ..sources.file import FileSource
    from ..sources.placeholder import PlaceholderSource
    from ..sources.solid import SolidSource
    from .folder import FolderItem


class FootageItem(AVItem):
    """
    The `FootageItem` object represents a footage item imported into a project,
    which appears in the Project panel.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        footage = app.project.footages[0]
        print(footage.main_source)
        ```

    Info:
        `FootageItem` is a subclass of [AVItem][] object, which is a subclass of
        [Item][] object. All methods and attributes of [AVItem][] and [Item][] are
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

    def __init__(
        self,
        *,
        comment: str,
        id: int,
        label: Label,
        name: str,
        parent_folder: FolderItem | None,
        duration: float,
        frame_duration: int,
        frame_rate: float,
        height: int,
        pixel_aspect: float,
        width: int,
        main_source: FileSource | SolidSource | PlaceholderSource,
        asset_type: str,
        end_frame: int,
        start_frame: int,
    ) -> None:
        super().__init__(
            comment=comment,
            id=id,
            label=label,
            name=name,
            parent_folder=parent_folder,
            type_name="Footage",
            duration=duration,
            frame_duration=frame_duration,
            frame_rate=frame_rate,
            height=height,
            pixel_aspect=pixel_aspect,
            width=width,
        )
        self.main_source = main_source
        self.asset_type = asset_type
        self.end_frame = end_frame
        self.start_frame = start_frame

    @property
    def file(self) -> str | None:
        """The footage file path if its source is a [FileSource][], else `None`."""
        if hasattr(self.main_source, "file"):
            return self.main_source.file
        return None
