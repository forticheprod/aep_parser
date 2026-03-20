from __future__ import annotations

import typing
from typing import Any, List, cast

from aep_parser.enums import Label

from ...descriptors import ChunkField, ChunkInstanceField
from ...reverses import reverse_ratio
from ..properties.marker import MarkerValue
from ..properties.property import Property
from ..properties.property_group import PropertyGroup

if typing.TYPE_CHECKING:
    from aep_parser.enums import AutoOrientType

    from ...kaitai.aep import Aep  # type: ignore[attr-defined]
    from ..items.composition import CompItem


_reverse_start_time = reverse_ratio("start_time")


def _reverse_stretch(value: float, _body: Any) -> dict[str, int]:
    """Decompose stretch (percentage) into dividend/divisor."""
    _TIME_DIVISOR = 10000
    if value == 0:
        return {"stretch_dividend": 0, "stretch_divisor": 0}
    return {
        "stretch_dividend": round(value * _TIME_DIVISOR / 100.0),
        "stretch_divisor": _TIME_DIVISOR,
    }


class Layer(PropertyGroup):
    """
    The `Layer` object provides access to layers within compositions.

    Info:
        `Layer` is a subclass of [PropertyGroup][], which is a subclass of
        [PropertyBase][aep_parser.models.properties.property_base.PropertyBase]. All
        methods and attributes of [PropertyGroup][], in addition to those listed below,
        are available when working with `Layer` objects.

    Info:
        `Layer` is the base class for [CameraLayer][] object, [LightLayer][]
        object and [AVLayer][] object, so `Layer` attributes and methods are
        available when working with all layer types.

    See: https://ae-scripting.docsforadobe.dev/layer/layer/
    """

    # ---- Chunk-backed descriptors (ldta) ----

    id = ChunkField[int]("_ldta", "layer_id")
    """Unique and persistent identification number used internally to
    identify a Layer between sessions. Read-only."""

    label = ChunkField[Label](
        "_ldta", "label", transform=lambda v: Label(int(v)), reverse=int
    )
    """The label color. Colors are represented by their number (0 for None,
    or 1 to 16 for one of the preset colors in the Labels preferences).
    Read / Write."""

    locked = ChunkField[bool]("_ldta", "locked", reverse=int)
    """When `True`, the layer is locked. This corresponds to the lock toggle
    in the Layer panel. Read / Write."""

    null_layer = ChunkField[bool]("_ldta", "null_layer")
    """When `True`, the layer was created as a null object. Read-only."""

    _parent_id = ChunkField[int]("_ldta", "parent_id", reverse=int)
    """The ID of the layer's parent layer. `0` if the layer has no parent."""

    shy = ChunkField[bool]("_ldta", "shy", reverse=int)
    """When `True`, the layer is "shy", meaning that it is hidden in the
    Layer panel if the composition's "Hide all shy layers" option is
    toggled on. Read / Write."""

    solo = ChunkField[bool]("_ldta", "solo", reverse=int)
    """When `True`, the layer is soloed. Read / Write."""

    start_time = ChunkInstanceField[float](
        "_ldta",
        "start_time",
        reverse=_reverse_start_time,
        invalidates=["start_time"],
    )
    """The start time of the layer, expressed in composition time (seconds).
    Read / Write."""

    stretch = ChunkInstanceField[float](
        "_ldta",
        "stretch",
        reverse=_reverse_stretch,
        invalidates=["stretch"],
    )
    """The layer's time stretch, expressed as a percentage. A value of 100
    means no stretch. Values between 0 and 1 are set to 1, and values
    between -1 and 0 (not including 0) are set to -1. Read / Write."""

    # ---- Regular attributes set in __init__ ----

    auto_orient: AutoOrientType
    """The type of automatic orientation to perform for the layer."""

    comment: str
    """A descriptive comment for the layer."""

    containing_comp: CompItem
    """
    The composition that contains this layer. Set after parsing when the full
    project structure is available.
    """

    layer_type: str
    """The type of layer. Matches ExtendScript `layerType` values:
    `"AVLayer"`, `"LightLayer"`, `"CameraLayer"`, or `"Layer"`."""

    time: float
    """
    The current time of the layer, expressed in composition time (seconds).
    """

    is_name_set: bool

    in_point: float
    """The "in" point of the layer, expressed in composition time (seconds)."""

    out_point: float
    """The "out" point of the layer, expressed in composition time (seconds)."""

    frame_in_point: int
    """The "in" point of the layer, expressed in composition time (frames)."""

    frame_out_point: int
    """The "out" point of the layer, expressed in composition time (frames)."""

    frame_start_time: int
    """The start time of the layer, expressed in composition time (frames)."""

    # Use identity-based equality to avoid comparing all fields recursively,
    # which could produce unexpected results or hit circular references.
    __eq__ = object.__eq__
    __hash__ = object.__hash__

    def __init__(
        self,
        *,
        _ldta: Aep.LdtaBody,
        name: str,
        comment: str,
        containing_comp: CompItem,
        properties: list[Property | PropertyGroup],
        auto_orient: AutoOrientType,
        layer_type: str,
        match_name: str,
    ) -> None:
        self._ldta = _ldta

        super().__init__(
            enabled=_ldta.enabled,
            match_name=match_name,
            name=name,
            property_depth=0,
            properties=properties,
        )

        self.auto_orient = auto_orient
        self.comment = comment
        self.containing_comp = containing_comp
        self.layer_type = layer_type
        self.time = 0
        self.is_name_set = bool(name)
        self._parent: Layer | None = None

        # Compute absolute time points from binary relative values
        stretch = _ldta.stretch
        stretch_factor = stretch / 100.0 if stretch != 0.0 else 1.0
        self.in_point = _ldta.start_time + _ldta.in_point * stretch_factor
        self.out_point = _ldta.start_time + _ldta.out_point * stretch_factor
        self.frame_in_point = round(self.in_point * containing_comp.frame_rate)
        self.frame_out_point = round(self.out_point * containing_comp.frame_rate)
        self.frame_start_time = round(_ldta.start_time * containing_comp.frame_rate)

    @property
    def index(self) -> int:
        """The 0-based index position of the layer in its containing comp.

        Warning:
            Unlike ExtendScript (1-based), this uses Python's 0-based
            convention so that `comp.layers[layer.index]` works directly.
        """
        return self.containing_comp.layers.index(self)

    @property
    def has_video(self) -> bool:
        """`True` if the layer has a video switch in the Timeline panel.

        Always `False` for [CameraLayer][] and [LightLayer][] objects.
        """
        return False

    @property
    def active(self) -> bool:
        """
        When `True`, the layer is active at the current time.

        Overrides [PropertyBase.active][] to evaluate
        [active_at_time][] at [time][].
        """
        return self.active_at_time(self.time)

    @property
    def marker(self) -> Property | None:
        """The layer's marker property.

        A [Property][aep_parser.models.properties.property.Property] with
        `match_name="ADBE Marker"` whose keyframes hold marker values.
        `None` when the layer has no markers.
        """
        try:
            prop = self["ADBE Marker"]
        except KeyError:
            return None
        return cast(Property, prop)

    @property
    def markers(self) -> list[MarkerValue]:
        """A flat list of [MarkerValue][] objects for this layer.

        Shortcut for accessing marker data without navigating the property
        tree. Returns an empty list when the layer has no markers.

        Example:
            ```python
            for marker in layer.markers:
                print(marker.comment)
            ```
        """
        if self.marker is None:
            return []
        return cast(
            List[MarkerValue],  # Cannot use `list` for Py3.7`
            [kf.value for kf in self.marker.keyframes],
        )

    @property
    def transform(self) -> PropertyGroup:
        """
        Contains a layer's transform properties.

        This is the Transform `PropertyGroup` (match name
        `ADBE Transform Group`). Individual transform properties (Position,
        Scale, Rotation, etc.) are accessible via
        [properties][PropertyGroup.properties].
        """
        group = self["ADBE Transform Group"]
        assert isinstance(group, PropertyGroup)
        return group

    @property
    def effects(self) -> PropertyGroup | None:
        """
        Contains a layer's effects.

        This is the Effects `PropertyGroup` (match name `ADBE Effect Parade`).
        Each child in [properties][PropertyGroup.properties] is itself a
        [PropertyGroup][] representing one effect. `None` when the layer has no
        effects.
        """
        try:
            group = self["ADBE Effect Parade"]
        except KeyError:
            return None
        if not isinstance(group, PropertyGroup) or not group.properties:
            return None
        return group

    @property
    def masks(self) -> PropertyGroup | None:
        """
        Contains a layer's masks.

        This is the Masks `PropertyGroup` (match name `ADBE Mask Parade`).
        Each child in [properties][PropertyGroup.properties] is itself a
        [PropertyGroup][] representing one mask. `None` when the layer has no
        masks.
        """
        try:
            group = self["ADBE Mask Parade"]
        except KeyError:
            return None
        if not isinstance(group, PropertyGroup) or not group.properties:
            return None
        return group

    @property
    def text(self) -> PropertyGroup | None:
        """Contains a layer's text properties (if any)."""
        try:
            group = self["ADBE Text Properties"]
        except KeyError:
            return None
        if isinstance(group, PropertyGroup):
            return group
        return None

    @property
    def parent(self) -> Layer | None:
        """The parent layer for layer parenting. `None` if no parent."""
        return self._parent

    @parent.setter
    def parent(self, value: Layer | None) -> None:
        self._parent = value

    def active_at_time(self, time: float) -> bool:
        """Return whether the layer is active at the given time.

        For this method to return `True`, three conditions must be met:

        1. The layer must be `enabled`.
        2. No other layer in the [containing_comp][] may be soloed unless
           this layer is also [solo][].
        3. *time* must fall between [in_point][] (inclusive) and
           [out_point][] (exclusive).

        Args:
            time: The time in seconds.
        """
        if not self.enabled:
            return False

        any_solo = any(layer.solo for layer in self.containing_comp.layers)
        if any_solo and not self.solo:
            return False

        if time < self.in_point or time >= self.out_point:
            return False

        return True

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"enabled={self.enabled!r}, "
            f"match_name={self.match_name!r}, "
            f"name={self.name!r})"
        )
