from __future__ import annotations

import typing
from dataclasses import dataclass, field

from .item import Item


@dataclass
class Folder(Item):
    """
    Folder item.

    Attributes:
        items: The items in this folder.
    """

    items: list[Item] = field(default_factory=list)

    def __iter__(self) -> typing.Iterator[Item]:
        """Return an iterator over the folder items."""
        return iter(self.items)

