from __future__ import annotations

import typing
from typing import Any, cast

from py_aep.enums import PropertyType

from ...data.match_names import MATCH_NAME_TO_NICE_NAME
from ...kaitai.descriptors import ChunkField
from ...kaitai.utils import propagate_check

if typing.TYPE_CHECKING:
    from ...kaitai import Aep
    from .property_group import PropertyGroup

_TDSN_SENTINEL = "-_0_/-"


class PropertyBase:
    """Abstract base class for both [Property][] and [PropertyGroup][].

    Info:
        `PropertyBase` is the base class for both [Property][] and
        [PropertyGroup][], so `PropertyBase` attributes and methods are available
        when working with properties and property groups.

    See: https://ae-scripting.docsforadobe.dev/property/propertybase/
    """

    match_name: str
    """A special name for the property used to build unique naming paths. The
    match name is not displayed, but you can refer to it in scripts. Every
    property has a unique match-name identifier. Read-only."""

    property_depth: int
    """The number of levels of parent groups between this property and the
    containing layer. The value is 0 for a layer. Read-only."""

    elided: bool
    """When `True`, the property is not shown in the UI. An elided property is
    still present in the timeline but hidden from view."""

    is_effect: bool
    """When `True`, this property is an effect [PropertyGroup][]."""

    is_mask: bool
    """When `True`, this property is a mask [PropertyGroup][]."""

    property_type: PropertyType
    """The type of this property. One of `PropertyType.PROPERTY`,
    `PropertyType.NAMED_GROUP`, or `PropertyType.INDEXED_GROUP`.
    Read-only."""

    parent_property: PropertyGroup | None
    """The parent [PropertyGroup][] of this property, or `None` for
    top-level layer property groups. Read-only."""

    enabled = ChunkField.bool("_tdsb", "enabled", default=True)
    """Corresponds to the setting of the eyeball icon. Read / Write."""

    def __init__(
        self,
        *,
        _tdsb: Aep.TdsbBody | None,
        _name_utf8: Aep.Utf8Body | None = None,
        match_name: str,
        property_depth: int,
        auto_name: str | None = None,
    ) -> None:
        self._tdsb = _tdsb
        self._name_utf8 = _name_utf8
        self.match_name = match_name
        self._auto_name = auto_name
        self.property_depth = property_depth

        self._ewot_entry: Aep.EwotEntry | None = None

        self.__dict__["_selected"] = False

        self.elided = False
        self.is_effect = False
        self.is_mask = False
        self.parent_property = None
        self.property_type = PropertyType.NAMED_GROUP

    @property
    def selected(self) -> bool:
        """When `True`, the property is selected. Read / Write."""
        if self._ewot_entry is not None:
            return bool(self._ewot_entry.selected)
        return bool(self.__dict__.get("_selected", False))

    @selected.setter
    def selected(self, value: bool) -> None:
        if self._ewot_entry is not None:
            self._ewot_entry.selected = int(value)
            propagate_check(self._ewot_entry)
        else:
            self.__dict__["_selected"] = value

    @property
    def auto_name(self) -> str:
        """The automatic (display) name derived from `match_name`."""
        if self._auto_name is not None:
            return self._auto_name
        return MATCH_NAME_TO_NICE_NAME.get(self.match_name, self.match_name)

    @property
    def name(self) -> str:
        """Display name of the property. Read / Write."""
        if self._name_utf8 is not None:
            text: str = self._name_utf8.contents.split("\0")[0]
            if text and text != _TDSN_SENTINEL:
                return text
        return self.auto_name

    @name.setter
    def name(self, value: str) -> None:
        if self._name_utf8 is None:
            # Synthesized property - materialize to create the tdsn chunk.
            materialize = getattr(self, "_materialize", None)
            if materialize is not None:
                materialize()
        if self._name_utf8 is not None:
            self._name_utf8.contents = value + "\0"
            propagate_check(self._name_utf8)

    @property
    def is_name_set(self) -> bool:
        """`True` if the name has been explicitly set by the user. Read-only."""
        if self._name_utf8 is not None:
            text: str = self._name_utf8.contents.split("\0")[0]
            return bool(text) and text != _TDSN_SENTINEL
        return False

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
        Read-only.
        """
        if self.property_depth == 0 or self.parent_property is None:
            return None
        return self.parent_property.properties.index(cast(Any, self))

    @property
    def can_set_enabled(self) -> bool:
        """`True` if the `enabled` attribute value can be set.

        This is `True` for all layers, effect property groups, shape
        vector groups, and text path options. Read-only.
        """
        if self.property_depth == 0:
            return True
        if self.is_effect:
            return True
        mn = self.match_name
        if mn == "ADBE Text Path Options":
            return True
        if mn.startswith("ADBE Vector") and mn not in (
            "ADBE Vectors Group",
            "ADBE Vector Transform Group",
            "ADBE Vector Repeater Transform",
        ):
            return self.property_type in (
                PropertyType.NAMED_GROUP,
                PropertyType.INDEXED_GROUP,
            )
        return False

    @property
    def _containing_layer(self) -> Any:
        """Walk up the parent_property chain to find the containing layer.

        Returns the Layer object (detected by having `_ldta`), or `None`
        if the property is not attached to a layer.
        """
        node = self.parent_property
        while node is not None:
            if hasattr(node, "_ldta"):
                return node
            node = node.parent_property
        return None

    def _is_in_effect(self) -> bool:
        """Check if this property is inside an effect PropertyGroup."""
        node = self.parent_property
        while node is not None:
            if node.is_effect:
                return True
            if hasattr(node, "_ldta"):
                break
            node = node.parent_property
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
