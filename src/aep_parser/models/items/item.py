from __future__ import annotations

import typing
from abc import ABC
from dataclasses import dataclass, field

if typing.TYPE_CHECKING:
    from ...kaitai import Aep
    from .folder import FolderItem


@dataclass
class Item(ABC):
    """
    Abstract base class storing information about folders, compositions, or
    footages.

    Attributes:
        comment: The item comment.
        item_id: The item unique identifier.
        label: The label color. Colors are represented by their number
            (0 for None, or 1 to 16 for one of the preset colors in the
            Labels preferences).
        name: The name of the item, as shown in the Project panel.
        parent_folder: The parent folder of this item. None for the root
            folder.
        type_name: A user-readable name for the item type ("Folder",
            "Footage" or "Composition"). These names are application
            locale-dependent, meaning that they are different depending on
            the application's UI language.
    """

    comment: str
    item_id: int
    label: Aep.Label
    name: str
    parent_folder: FolderItem | None = field(repr=False)
    type_name: str

    @property
    def is_folder(self) -> bool:
        """True if the item is a folder."""
        return self.type_name == "Folder"

    @property
    def is_composition(self) -> bool:
        """True if the item is a composition."""
        return self.type_name == "Composition"

    @property
    def is_footage(self) -> bool:
        """True if the item is a footage."""
        return self.type_name == "Footage"
