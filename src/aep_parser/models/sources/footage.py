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


class FootageSource(ABC):
    def __init__(self):
        pass

    def __repr__(self):
        """
        Returns:
            str: A string representation of the object.
        """
        return str(self.__dict__)

    @property
    def is_solid(self):
        """
        Returns:
            bool: False
        """
        return False
