from __future__ import (
    absolute_import,
    unicode_literals,
    division
)
import abc
import sys
from builtins import str


if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(
        b'ABC',
        (object,),
        {'__slots__': ()}
    )


class Item(ABC):
    def __init__(self, comment, item_id, label, name, type_name, parent_id):
        """
        Generalized object storing information about folders, compositions, or footages.
        Args:
            comment (str): The item comment.
            item_id (int): The item unique identifier.
            label (int): The item label color.
            name (str): The item name.
            type_name (str): The item type ("Folder", "Composition" or "Footage").
            parent_id (int): The unique identifier of the item's parent folder.
        """
        self.comment = comment
        self.item_id = item_id
        self.label = label
        self.name = name
        self.parent_id = parent_id
        self.type_name = type_name

    def __repr__(self):
        """
        Returns:
            str: The string representation of the object.
        """
        return str(self.__dict__)

    @abc.abstractmethod
    def is_composition(self):
        """
        Returns:
            bool: True if the item is a composition, False otherwise.
        """
        pass

    @abc.abstractmethod
    def is_folder(self):
        """
        Returns:
            bool: True if the item is a folder, False otherwise.
        """
        pass

    @abc.abstractmethod
    def is_footage(self):
        """
        Returns:
            bool: True if the item is a footage, False otherwise.
        """
        pass
