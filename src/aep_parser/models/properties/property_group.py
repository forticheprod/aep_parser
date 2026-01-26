from __future__ import annotations

import typing
from dataclasses import dataclass, field

from .property_base import PropertyBase

if typing.TYPE_CHECKING:
    from .property import Property


@dataclass
class PropertyGroup(PropertyBase):
    """
    Group of properties.

    Attributes:
        is_effect: When true, this property is an effect PropertyGroup.
    """

    is_effect: bool = False
    properties: list[Property] = field(default_factory=list)

    @property
    def elided(self) -> bool:
        """Return True if this property group is elided (not an effect)."""
        return not self.is_effect

    def __iter__(self) -> typing.Iterator[Property]:
        """Return an iterator over the properties in this group."""
        return iter(self.properties)

    def get_property(
        self, index: int | None = None, name: str | None = None
    ) -> Property | None:
        """
        Find and return a child property of this group.

        The property can be specified by either its index or name (match name
        or display name).

        Args:
            index: The index of the property to return.
            name: The name of the property to return.
        """
        defined_arg = index or name
        if defined_arg:
            if isinstance(defined_arg, (int, float)):
                return self.properties[defined_arg]
            elif isinstance(defined_arg, str):
                for prop in self.properties:
                    if prop.name == defined_arg or prop.match_name == defined_arg:
                        return prop
        return None
