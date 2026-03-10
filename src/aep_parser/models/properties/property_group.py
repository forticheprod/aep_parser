from __future__ import annotations

import typing
from dataclasses import dataclass

from aep_parser.enums import PropertyType

from .property_base import PropertyBase

if typing.TYPE_CHECKING:
    from .property import Property


@dataclass
class PropertyGroup(PropertyBase):
    """
    The `PropertyGroup` object represents a group of properties. It can contain
    [Property][] objects and other `PropertyGroup` objects. Property groups can
    be nested to provide a parent-child hierarchy, with a [Layer][] object at the
    top (root) down to a single [Property][] object, such as the mask feather of
    the third mask. To traverse the group hierarchy, use [PropertyBase][] methods
    and attributes; see `PropertyBase.propertyGroup()`. For examples of how to
    access properties and property groups, see [PropertyBase][] object.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        effects = comp.layers[0].effects
        if effects is not None:
            for effect in effects:
                ...
        ```

    Info:
        `PropertyGroup` is a subclass of [PropertyBase][]. All methods and
        attributes of [PropertyBase][] are available when working with
        `PropertyGroup`.

    Info:
        `PropertyGroup` is a base class for [Layer][] and `MaskPropertyGroup`.
        `PropertyGroup` attributes and methods are available when working with
        layer or mask groups.

    See: https://ae-scripting.docsforadobe.dev/property/propertygroup/
    """

    properties: list[Property | PropertyGroup]
    """List of properties in this group."""

    @property
    def is_modified(self) -> bool:
        """`True` if any child property is modified.

        For indexed groups (such as Effects or Masks parades), the group
        is considered modified when it has any children — adding items to
        an indexed group is itself a modification.
        """
        if self.property_type == PropertyType.INDEXED_GROUP:
            return len(self.properties) > 0
        return any(child.is_modified for child in self.properties)

    def __iter__(self) -> typing.Iterator[Property | PropertyGroup]:
        """Return an iterator over the properties in this group."""
        return iter(self.properties)

    def __len__(self) -> int:
        """Return the number of child properties in this group."""
        return len(self.properties)

    def __getattr__(self, name: str) -> Property | PropertyGroup:
        """Look up a child property by attribute access.

        Converts the Python ``snake_case`` attribute name to match
        against the lowered, underscore-separated display names of
        child properties.  This allows natural syntax such as:

        ```python
        layer.transform.position.value
        layer.transform.anchor_point.value
        ```

        Note:
            Only invoked when normal attribute lookup has already
            failed, so dataclass fields and ``@property`` descriptors
            always take priority.
        """
        # Avoid infinite recursion during __init__ (before
        # ``properties`` has been set on the instance).
        try:
            properties: list[Property | PropertyGroup] = object.__getattribute__(
                self, "properties"
            )
        except AttributeError:
            raise AttributeError(name) from None
        for prop in properties:
            if prop.name.lower().replace(" ", "_") == name:
                return prop
        raise AttributeError(f"'{type(self).__name__}' has no property '{name}'")

    @property
    def num_properties(self) -> int:
        """The number of child properties in this group.

        Equivalent to ExtendScript ``PropertyGroup.numProperties``.
        """
        return len(self.properties)

    def __getitem__(self, key: int | str) -> Property | PropertyGroup:
        """Look up a child property by index or name.

        Supports both integer indices and string keys (display name or
        match name), mirroring ExtendScript's ``property()`` accessor with
        Python's ``[]`` operator.

        Example:
            ```python
            layer["ADBE Transform Group"]["ADBE Position"]
            layer["ADBE Masks"][0]
            layer[0]
            ```

        Args:
            key: An `int` index or a `str` display name / match name.

        Raises:
            KeyError: If the string key does not match any child.
            IndexError: If the integer index is out of range.
            TypeError: If *key* is neither `int` nor `str`.
        """
        if isinstance(key, int):
            return self.properties[key]
        if isinstance(key, str):
            for prop in self.properties:
                if prop.name == key or prop.match_name == key:
                    return prop
            raise KeyError(key)
        raise TypeError(f"Property key must be int or str, not {type(key).__name__}")

    def property(
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
        if index is not None:
            return self.properties[index]
        elif name is not None:
            return self[name]
        else:
            raise ValueError("Either index or name must be provided to get a property.")
