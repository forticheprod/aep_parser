from __future__ import annotations

import typing

from .property_base import PropertyBase

if typing.TYPE_CHECKING:
    from .property import Property


class PropertyGroup(PropertyBase):
    def __init__(self, is_effect: bool, *args, **kwargs):
        """
        Group of properties.

        Args:
            is_effect: When true, this property is an effect PropertyGroup.
        """
        super().__init__(*args, **kwargs)
        self.is_effect = is_effect

        self.properties = []
        self.enabled = True
        self.elided = not is_effect  # there might be more than that

    def __iter__(self) -> typing.Iterator[Property]:
        """Return an iterator over the properties in this group."""
        return iter(self.properties)

    def get_property(
        self, index: int | None = None, name: str | None = None
    ) -> Property | None:
        """
        Find and return a child property of this group.

        The property can be specified by either its index or name (match name or display
        name).

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
