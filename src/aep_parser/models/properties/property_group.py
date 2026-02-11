from __future__ import annotations

import typing
from dataclasses import dataclass

from .property_base import PropertyBase

if typing.TYPE_CHECKING:
    from .property import Property


@dataclass
class PropertyGroup(PropertyBase):
    """
    The `PropertyGroup` object represents a group of properties. It can contain
    `Property` objects and other `PropertyGroup` objects. Property groups can
    be nested to provide a parent-child hierarchy, with a `Layer` object at the
    top (root) down to a single `Property` object, such as the mask feather of
    the third mask. To traverse the group hierarchy, use `PropertyBase` methods
    and attributes; see `PropertyBase.propertyGroup()`. For examples of how to
    access properties and property groups, see `PropertyBase` object.

    Info:
        `PropertyGroup` is a subclass of `PropertyBase`. All methods and
        attributes of `PropertyBase` are available when working with
        `PropertyGroup`.

    Info:
        `PropertyGroup` is a base class for `MaskPropertyGroup`.
        `PropertyGroup` attributes and methods are available when working with
        layer or mask groups.

    See: https://ae-scripting.docsforadobe.dev/property/propertygroup/
    """

    is_effect: bool
    """When `True`, this property is an effect `PropertyGroup`."""

    properties: list[Property | PropertyGroup]
    """List of properties in this group."""

    def __iter__(self) -> typing.Iterator[Property | PropertyGroup]:
        """Return an iterator over the properties in this group."""
        return iter(self.properties)

    def get_property(
        self, index: int | None = None, name: str | None = None
    ) -> Property | PropertyGroup:
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
                raise ValueError(f"No property found with name '{defined_arg}'")
        else:
            raise ValueError("Either index or name must be provided to get a property.")
