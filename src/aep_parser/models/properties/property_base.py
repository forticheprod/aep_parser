from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


@dataclass
class PropertyBase(ABC):
    """Abstract base class for both [Property][] and [PropertyGroup][].

    Info:
        `PropertyBase` is the base class for both [Property][] and
        [PropertyGroup][], so `PropertyBase` attributes and methods are available
        when working with properties and property groups.

    See: https://ae-scripting.docsforadobe.dev/property/propertybase/
    """

    enabled: bool
    """Corresponds to the setting of the eyeball icon."""

    match_name: str
    """
    A special name for the property used to build unique naming paths. The
    match name is not displayed, but you can refer to it in scripts. Every
    property has a unique match-name identifier.
    """

    name: str
    """Display name of the property."""

    @property
    def active(self) -> bool:
        """Same as enabled."""
        return self.enabled

    @property
    def is_modified(self) -> bool:
        """`True` if this property has been changed since its creation."""
        # TODO
        return False
