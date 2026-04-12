from __future__ import annotations

import typing
from typing import TYPE_CHECKING

from aep_parser.data.match_names import MATCH_NAME_TO_NICE_NAME
from aep_parser.enums import PropertyType

from ...kaitai.proxy import ProxyBody
from ...kaitai.utils import create_chunk, create_tdsb_chunk
from .overrides import _PROPERTY_MIN_MAX
from .property import Property
from .property_base import PropertyBase
from .specs import (
    _GROUP_CHILD_SPECS,
    _LAYER_STYLE_CHILD_SPECS,
    _USE_VALUE,
    _GroupSpec,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ...kaitai import Aep
    from .specs import _GroupSpec, _PropSpec


_INDEXED_GROUP_MATCH_NAMES: set[str] = {
    "ADBE Effect Parade",
    "ADBE Mask Parade",
    "ADBE Effect Mask Parade",
    "ADBE Text Animators",
}


class PropertyGroup(PropertyBase):
    """The `PropertyGroup` object represents a group of properties. It can contain
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
    """List of properties in this group. Read-only."""

    def __init__(
        self,
        *,
        _tdgp: Aep.ListBody | None = None,
        _tdsb: Aep.TdsbBody | None,
        _name_utf8: Aep.Utf8Body | None = None,
        _fnam_utf8: Aep.Utf8Body | None = None,
        match_name: str,
        property_depth: int,
        properties: list[Property | PropertyGroup],
        auto_name: str | None = None,
    ) -> None:
        super().__init__(
            _tdsb=_tdsb,
            _name_utf8=_name_utf8,
            match_name=match_name,
            property_depth=property_depth,
            auto_name=auto_name,
        )

        self._tdgp = _tdgp
        self._fnam_utf8 = _fnam_utf8

        self.properties = properties

        for child in self.properties:
            child.parent_property = self

        if match_name in _INDEXED_GROUP_MATCH_NAMES:
            self.property_type = PropertyType.INDEXED_GROUP

        if match_name in ("ADBE Effect Mask Parade", "ADBE Vectors Group"):
            self.elided = True
        elif match_name == "ADBE Text Animators" and not properties:
            self.elided = True

    @property
    def auto_name(self) -> str:
        """The automatic (display) name derived from `match_name`."""
        if self._auto_name is not None:
            return self._auto_name
        if self._fnam_utf8 is not None:
            name: str = self._fnam_utf8.contents.split("\0")[0]
            return name
        return MATCH_NAME_TO_NICE_NAME.get(self.match_name, self.match_name)

    def _materialize_group(self) -> None:
        """Replace ProxyBody backing with real Kaitai chunks.

        Creates a tdmn + LIST:tdgp in the parent's _tdgp, with a
        group-level tdsb inside. After this, child properties can
        materialize into this group's _tdgp.
        """
        if not isinstance(self._tdsb, ProxyBody):
            return

        parent = self.parent_property
        if parent is None:
            return

        # Recurse: ensure parent group is materialized first.
        if hasattr(parent, "_materialize_group"):
            parent._materialize_group()

        parent_tdgp = parent._tdgp
        if parent_tdgp is None:
            return

        proxy_tdsb = self._tdsb

        # 1. tdmn with this group's match name.
        create_chunk(
            parent_tdgp,
            "tdmn",
            "Utf8Body",
            contents=self.match_name + "\x00",
        )

        # 2. LIST:tdgp container.
        tdgp_chunk = create_chunk(
            parent_tdgp,
            "LIST",
            "ListBody",
            list_type="tdgp",
            chunks=[],
        )
        tdgp_body = tdgp_chunk.body

        # 3. Group-level tdsb inside the new tdgp.
        tdsb_chunk = create_tdsb_chunk(tdgp_body, proxy_tdsb)

        # 4. "ADBE Group End" sentinel.
        create_chunk(
            parent_tdgp,
            "tdmn",
            "Utf8Body",
            contents="ADBE Group End\x00",
        )

        # Replace proxy references with real chunk bodies.
        self._tdsb = tdsb_chunk.body
        self._tdgp = tdgp_body

    def __iter__(self) -> typing.Iterator[Property | PropertyGroup]:
        """Return an iterator over the properties in this group."""
        return iter(self.properties)

    def __len__(self) -> int:
        """Return the number of child properties in this group."""
        return len(self.properties)

    def __getattr__(self, name: str) -> Property | PropertyGroup:
        """Look up a child property by attribute access.

        Converts the Python `snake_case` attribute name to match
        against the lowered, underscore-separated display names of
        child properties.  This allows natural syntax such as:

        ```python
        layer.transform.position.value
        layer.transform.anchor_point.value
        ```

        Note:
            Only invoked when normal attribute lookup has already
            failed, so dataclass fields and `@property` descriptors
            always take priority.
        """
        # Avoid infinite recursion during __init__ (before
        # `properties` has been set on the instance).
        try:
            object.__getattribute__(self, "properties")
        except AttributeError:
            raise AttributeError(name) from None
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' has no property '{name}'"
            ) from None

    def __getitem__(self, key: int | str) -> Property | PropertyGroup:
        """Look up a child property by index or name.

        Supports both integer indices and string keys (display name or
        match name), mirroring ExtendScript's `property()` accessor with
        Python's `[]` operator.

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
                if (
                    prop.name == key
                    or prop.match_name == key
                    or prop.name.lower().replace(" ", "_") == key
                ):
                    return prop
            raise KeyError(key)
        raise TypeError(f"Property key must be int or str, not {type(key).__name__}")

    @property
    def is_modified(self) -> bool:
        """`True` if any child property is modified.

        For indexed groups (such as Effects or Masks parades), the group
        is considered modified when it has any children - adding items to
        an indexed group is itself a modification.  Shape vector groups
        (Contents) follow the same rule.
        """
        if self.property_type == PropertyType.INDEXED_GROUP and not self.is_effect:
            return len(self.properties) > 0
        if self.match_name == "ADBE Vectors Group" and len(self.properties) > 0:
            return True
        return any(child.is_modified for child in self.properties)

    @property
    def num_properties(self) -> int:
        """The number of child properties in this group.

        Equivalent to ExtendScript `PropertyGroup.numProperties`.
        """
        return len(self.properties)

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

    def _fill_from_specs(
        self,
        specs: Sequence[_PropSpec | _GroupSpec],
    ) -> None:
        """Fill missing children using *specs* in canonical order.

        Existing children are preserved and reordered.  Missing children
        are synthesized via `Property.from_spec` (for `_PropSpec`) or as
        empty `PropertyGroup` instances (for `_GroupSpec`).

        Args:
            specs: Ordered list of child property specifications.
        """
        existing: dict[str, Property | PropertyGroup] = {}
        for child in self.properties:
            existing[child.match_name] = child

        child_depth = self.property_depth + 1
        ordered: list[Property | PropertyGroup] = []
        for spec in specs:
            if spec.match_name in existing:
                child = existing[spec.match_name]
                child._auto_name = spec.name
                if not isinstance(spec, _GroupSpec) and isinstance(child, Property):
                    child.__dict__["_color"] = spec.color
                    if spec.min_value is not None:
                        child._min_value_fallback = spec.min_value
                    if spec.max_value is not None:
                        child._max_value_fallback = spec.max_value
                    if spec.can_vary_over_time is not None:
                        child._can_vary_over_time = spec.can_vary_over_time
                    if child.default_value is None:
                        dv = (
                            spec.value
                            if spec.default_value is _USE_VALUE
                            else spec.default_value
                        )
                        if dv is not None:
                            child.default_value = dv
                ordered.append(child)
            elif isinstance(spec, _GroupSpec):
                group = PropertyGroup(
                    _tdsb=ProxyBody(
                        enabled=1,
                        locked_ratio=0,
                        roto_bezier=0,
                        dimensions_separated=0,
                    ),
                    match_name=spec.match_name,
                    auto_name=spec.name,
                    property_depth=child_depth,
                    properties=[],
                )
                group.parent_property = self
                ordered.append(group)
            else:
                prop = Property.from_spec(spec, child_depth)
                prop.parent_property = self
                ordered.append(prop)

        # Preserve existing PropertyGroup children not covered by specs
        # (e.g. Dashes/Taper/Wave inside Stroke, Contents/Transform in
        # Vector Group).
        spec_match_names = {s.match_name for s in specs}
        for child in self.properties:
            if (
                isinstance(child, PropertyGroup)
                and child.match_name not in spec_match_names
            ):
                ordered.append(child)

        self.properties = ordered  # type: ignore[assignment]

    def _apply_min_max_bounds(self) -> None:
        """Set `min_value`/`max_value` on properties with known bounds.

        Walks all children recursively and applies overrides from
        `_PROPERTY_MIN_MAX` unconditionally.  Uses fallback fields
        so the binary tdum/tduM chunks are not mutated.
        """
        for child in self.properties:
            if isinstance(child, Property):
                bounds = _PROPERTY_MIN_MAX.get(child.match_name)
                if bounds is not None:
                    child._min_value_fallback = bounds[0]
                    child._max_value_fallback = bounds[1]
            elif isinstance(child, PropertyGroup):
                child._apply_min_max_bounds()

    def _synthesize_children(self) -> None:
        """Synthesize missing children in this standard property group.

        Dispatches to `_fill_from_specs` for groups with known canonical
        children, or to a specialized handler for layer styles.
        """
        specs = _GROUP_CHILD_SPECS.get(self.match_name)
        if specs is not None:
            self._fill_from_specs(specs)
            # Don't return: recurse into preserved sub-groups below.

        if self.match_name == "ADBE Layer Styles":
            for child in self.properties:
                if isinstance(child, PropertyGroup):
                    child_specs = _LAYER_STYLE_CHILD_SPECS.get(child.match_name)
                    if child_specs is not None:
                        child._fill_from_specs(child_specs)

        for child in self.properties:
            if isinstance(child, PropertyGroup):
                child._synthesize_children()
