from __future__ import annotations

import typing
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, cast

from aep_parser.enums import PropertyType

if typing.TYPE_CHECKING:
    from .property_group import PropertyGroup


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

    property_depth: int
    """
    The number of levels of parent groups between this property and the
    containing layer. The value is 0 for a layer.
    """

    # Set after initialization
    selected: bool = field(init=False, default=False)
    """
    When `True`, the property is selected.
    """

    elided: bool = field(init=False, default=False)
    """
    When `True`, the property is not shown in the UI. An elided property is
    still present in the timeline but hidden from view.
    """

    is_effect: bool = field(init=False, default=False)
    """When `True`, this property is an effect [PropertyGroup][]."""

    is_mask: bool = field(init=False, default=False)
    """When `True`, this property is a mask [PropertyGroup][]."""

    parent_property: PropertyGroup | None = field(init=False, default=None, repr=False)
    """
    The parent [PropertyGroup][] of this property, or `None` for top-level
    layer property groups.
    """

    property_type: PropertyType = field(init=False, default=PropertyType.NAMED_GROUP)
    """
    The type of this property. One of `PropertyType.PROPERTY`,
    `PropertyType.NAMED_GROUP`, or `PropertyType.INDEXED_GROUP`.
    """

    @property
    def active(self) -> bool:
        """Same as enabled."""
        return self.enabled

    @property
    def property_index(self) -> int | None:
        """The 0-based position of this property within its parent group.

        Returns `None` for layers (property depth 0).

        Warning:
            Unlike ExtendScript (1-based), this uses Python's 0-based
            convention so that `group.properties[prop.property_index]`
            works directly.
        """
        if self.property_depth == 0 or self.parent_property is None:
            return None
        return self.parent_property.properties.index(cast(Any, self))

    @property
    def can_set_enabled(self) -> bool:
        """`True` if the `enabled` attribute value can be set.

        This is `True` for all layers, effect property groups, shape
        vector groups, and text path options.
        """
        if self.property_depth == 0:
            return True
        if self.is_effect:
            return True
        mn = self.match_name
        if mn.startswith("ADBE Vector") or mn == "ADBE Text Path Options":
            return True
        return False

    @property
    def is_modified(self) -> bool:
        """`True` if this property has been changed since its creation.

        A property is considered modified if its value differs from the
        default, if it has keyframes, or if an expression is enabled.
        A property group is modified if any of its children are modified,
        or if it is an indexed group with children (adding items to an
        indexed group like Effects or Masks is itself a modification).
        """
        return False
