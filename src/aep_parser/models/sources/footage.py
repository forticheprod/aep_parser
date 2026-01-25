from __future__ import annotations

import abc


class FootageSource(abc.ABC):
    def __init__(self):
        pass

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return str(self.__dict__)

    @property
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return False
