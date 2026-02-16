from __future__ import annotations

import typing
from abc import ABC
from dataclasses import dataclass, field

if typing.TYPE_CHECKING:
    from ...kaitai import Aep
    from .folder import FolderItem


@dataclass(eq=False)
class Item(ABC):
    """
    The `Item` object represents an item that can appear in the Project panel.

    Info:
        `Item` is the base class for [AVItem][] object and for [FolderItem][]
        object, which are in turn the base classes for various other item
        types, so `Item` attributes and methods are available when working with
        all of these item types.

    See: https://ae-scripting.docsforadobe.dev/item/item/
    """

    comment: str
    """The item comment."""

    id: int
    """The item unique identifier."""

    label: Aep.Label
    """
    The label color. Colors are represented by their number (0 for None, or 1
    to 16 for one of the preset colors in the Labels preferences).
    """

    name: str
    """The name of the item, as shown in the Project panel."""

    parent_folder: FolderItem | None = field(repr=False)
    """The parent folder of this item. `None` for the root folder."""

    type_name: str
    """
    A user-readable name for the item type ("Folder", "Footage" or
    "Composition"). These names are application locale-dependent, meaning that
    they are different depending on the application's UI language.
    """

    @property
    def is_folder(self) -> bool:
        """`True` if the item is a folder."""
        return self.type_name == "Folder"

    @property
    def is_composition(self) -> bool:
        """`True` if the item is a composition."""
        return self.type_name == "Composition"

    @property
    def is_footage(self) -> bool:
        """`True` if the item is a footage."""
        return self.type_name == "Footage"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
