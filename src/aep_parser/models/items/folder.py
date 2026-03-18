from __future__ import annotations

import typing

from .item import Item

if typing.TYPE_CHECKING:
    from aep_parser.enums import Label


class FolderItem(Item):
    """
    The `FolderItem` object corresponds to a folder in your Project panel. It
    can contain various types of items (footage, compositions, solids) as well
    as other folders.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        root = app.project.root_folder
        print(root.name)
        for item in root:
            ...
        ```

    See: https://ae-scripting.docsforadobe.dev/item/folderitem/
    """

    items: list[Item]
    """
    The items in this folder. Contains only the top-level items in the folder.
    """

    def __init__(
        self,
        *,
        comment: str,
        id: int,
        label: Label,
        name: str,
        parent_folder: FolderItem | None,
    ) -> None:
        super().__init__(
            comment=comment,
            id=id,
            label=label,
            name=name,
            parent_folder=parent_folder,
            type_name="Folder",
        )
        self.items: list[Item] = []

    def __iter__(self) -> typing.Iterator[Item]:
        """Return an iterator over the folder items."""
        return iter(self.items)

    @property
    def num_items(self) -> int:
        """
        Return the number of items in the folder.

        Note:
            Equivalent to `len(folder.items)`
        """
        return len(self.items)
