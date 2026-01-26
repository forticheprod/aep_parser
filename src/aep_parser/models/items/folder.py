from __future__ import annotations

import typing
from dataclasses import dataclass

from .item import Item


@dataclass
class Folder(Item):
    """
    Folder item.

    Attributes:
        folder_items: The IDs of items in this folder.
    """

    folder_items: list[int]

    def __iter__(self) -> typing.Iterator[int]:
        """Return an iterator over the folder item IDs."""
        return iter(self.folder_items)

    def item(self, index: int) -> int:
        """
        Get a folder item ID by index.

        Args:
            index: The index of the item to return.
        """
        return self.folder_items[index]
