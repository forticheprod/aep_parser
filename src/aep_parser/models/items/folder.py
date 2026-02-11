from __future__ import annotations

import typing
from dataclasses import dataclass, field

from .item import Item


@dataclass
class FolderItem(Item):
    """
    The `FolderItem` object corresponds to a folder in your Project panel. It
    can contain various types of items (footage, compositions, solids) as well
    as other folders.

    See: https://ae-scripting.docsforadobe.dev/item/folderitem/
    """

    items: list[Item] = field(default_factory=list)
    """
    The items in this folder. Contains only the top-level items in the folder.
    """

    def __iter__(self) -> typing.Iterator[Item]:
        """Return an iterator over the folder items."""
        return iter(self.items)

