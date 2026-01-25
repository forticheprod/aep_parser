from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    from ...kaitai.aep import Aep


class Item(abc.ABC):
    def __init__(
        self,
        comment: str,
        item_id: int,
        label: Aep.Label,
        name: str,
        type_name: str,
        parent_id: int | None,
    ):
        """
        Generalized object storing information about folders, compositions, or footages.

        Args:
            comment: The item comment.
            item_id: The item unique identifier.
            label: The label color. Colors are represented by their number
                (0 for None, or 1 to 16 for one of the preset colors in the
                Labels preferences).
            name: The name of the item, as shown in the Project panel.
            type_name: A user-readable name for the item type ("Folder",
                "Footage" or "Composition"). These names are application
                locale-dependent, meaning that they are different depending on
                the application's UI language.
            parent_id: The unique identifier of the item's parent folder.
        """
        self.comment = comment
        self.item_id = item_id
        self.label = label
        self.name = name
        self.parent_id = parent_id
        self.type_name = type_name

    def __repr__(self) -> str:
        """Return the string representation of the object."""
        return str(self.__dict__)

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
