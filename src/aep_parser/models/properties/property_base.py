from __future__ import annotations

import abc


class PropertyBase(abc.ABC):
    def __init__(
        self,
        match_name: str,
        name: str,
        enabled: bool | None = None,
    ):
        """
        Base class for both Property and PropertyGroup.

        Args:
            match_name: A special name for the property used to build unique
                naming paths. The match name is not displayed, but you can
                refer to it in scripts. Every property has a unique match-name
                identifier.
            name: Display name of the property.
            enabled: Corresponds to the setting of the eyeball icon.
        """
        self.match_name = match_name
        self.name = name
        # I did not implement self.parent_property as this would cause infinite
        # recursion when trying to print the object and we would have to override repr,
        # copy.deepcopy(self.__dict__) then override parent_property and it slows things
        # down quite a bit
        self.enabled = enabled

    def __repr__(self) -> str:
        """Return the string representation of the property."""
        return str(self.__dict__)

    @property
    def active(self) -> bool | None:
        """Same as enabled."""
        return self.enabled

    @property
    def is_modified(self) -> bool | None:
        """True if this property has been changed since its creation."""
        # TODO
        pass
