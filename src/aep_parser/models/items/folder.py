from __future__ import annotations

import typing

from .item import Item


class Folder(Item):
    def __init__(self, folder_items: list[int], *args, **kwargs):
        """
        Folder item.

        Args:
            folder_items: The IDs of items in this folder.
        """
        super().__init__(*args, **kwargs)
        self.folder_items = folder_items

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
