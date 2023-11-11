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
        """
        self.comment = comment
        self.item_id = item_id
        self.label = label
        self.name = name
        self.parent_id = parent_id
        self.type_name = type_name

    def __repr__(self):
        return str(self.__dict__)

    @abc.abstractmethod
    def is_composition(self):
        pass

    @abc.abstractmethod
    def is_folder(self):
        pass

    @abc.abstractmethod
    def is_footage(self):
        pass
