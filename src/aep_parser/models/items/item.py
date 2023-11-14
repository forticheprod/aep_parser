# coding: utf-8
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
            label (Aep.MarkerLabel): The label color. Colors are represented by their
                                     number (0 for None, or 1 to 16 for one of the
                                     preset colors in the Labels preferences).
            name (str): The name of the item, as shown in the Project panel.
            type_name (str): A user-readable name for the item type ("Folder", "Footage"
                             or "Composition"). These names are application
                             locale-dependent, meaning that they are different depending
                             on the application's UI language.
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

    @property
    def is_folder(self):
        """
        Returns:
            bool: True if the item is a folder.
        """
        return self.type_name == "Folder"
    
    @property
    def is_composition(self):
        """
        Returns:
            bool: True if the item is a composition.
        """
        return self.type_name == "Composition"
    
    @property
    def is_footage(self):
        """
        Returns:
            bool: True if the item is a footage.
        """
        return self.type_name == "Footage"