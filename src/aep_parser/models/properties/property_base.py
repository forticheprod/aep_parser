from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


@dataclass
class PropertyBase(ABC):
    """
    Abstract base class for both Property and PropertyGroup.

    Attributes:
        match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can
            refer to it in scripts. Every property has a unique match-name
            identifier.
        name: Display name of the property.
        enabled: Corresponds to the setting of the eyeball icon.
    """

    match_name: str
    name: str
    enabled: bool | None = None

    @property
    def active(self) -> bool | None:
        """Same as enabled."""
        return self.enabled

    @property
    def is_modified(self) -> bool | None:
        """True if this property has been changed since its creation."""
        # TODO
        return None
