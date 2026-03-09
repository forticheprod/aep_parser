from __future__ import annotations

import typing
from dataclasses import dataclass, field

from aep_parser.enums import Label

from ..properties.property_group import PropertyGroup

if typing.TYPE_CHECKING:
    from aep_parser.enums import AutoOrientType

    from ..items.composition import CompItem
    from ..properties.marker import MarkerValue


@dataclass(eq=False)
class Layer(PropertyGroup):
    """
    The `Layer` object provides access to layers within compositions.

    In the ExtendScript API, `Layer` is a subclass of [PropertyGroup][], which
    is a subclass of
    [PropertyBase][aep_parser.models.properties.property_base.PropertyBase].
    This hierarchy is reflected here: `Layer` inherits from [PropertyGroup][],
    giving access to all [PropertyBase][] and [PropertyGroup][] attributes and
    methods.

    Info:
        `Layer` is the base class for [CameraLayer][] object, [LightLayer][]
        object and [AVLayer][] object, so `Layer` attributes and methods are
        available when working with all layer types.

    See: https://ae-scripting.docsforadobe.dev/layer/layer/
    """

    auto_orient: AutoOrientType
    """The type of automatic orientation to perform for the layer."""

    comment: str
    """A descriptive comment for the layer."""

    containing_comp: CompItem = field(repr=False)
    """
    The composition that contains this layer. Set after parsing when the full
    project structure is available.
    """

    frame_in_point: int
    """
    The "in" point of the layer, expressed in composition time (frames). This
    is the first frame where the layer becomes visible. The binary format
    stores this relative to `start_time`; parsed value is absolute composition
    time.
    """

    frame_out_point: int
    """
    The "out" point of the layer, expressed in composition time (frames). This
    is the first frame where the layer is no longer visible. Clamped to
    composition duration to match ExtendScript behavior.
    """

    frame_start_time: int
    """
    The start time of the layer, expressed in composition time (frames). This
    determines where the layer's first frame of content appears in the
    composition timeline.
    """

    id: int
    """
    Unique and persistent identification number used internally to identify a
    Layer between sessions.
    """

    in_point: float
    """
    The "in" point of the layer, expressed in composition time (seconds). This
    is the time at which the layer starts being visible in the composition.
    The binary format stores this relative to `start_time` as a signed integer;
    parsed value is absolute composition time.
    """

    label: Label
    """
    The label color. Colors are represented by their number (0 for None, or 1
    to 16 for one of the preset colors in the Labels preferences).
    """

    layer_type: str
    """The type of layer (footage, light, camera, text, shape)."""

    locked: bool
    """
    When `True`, the layer is locked. This corresponds to the lock toggle in
    the Layer panel.
    """

    markers: list[MarkerValue]
    """Contains a layer's markers."""

    null_layer: bool
    """When `True`, the layer was created as a null object."""

    out_point: float
    """
    The "out" point of the layer, expressed in composition time (seconds).
    This is the time at which the layer stops being visible in the composition.
    Clamped to composition duration to match ExtendScript API behavior (a
    layer's `out_point` cannot exceed its containing composition's duration).
    The binary format stores this relative to `start_time`.
    """

    _parent_id: int
    """
    The ID of the layer's parent layer. `0` if the layer has no parent.
    """

    start_time: float
    """The start time of the layer, expressed in composition time (seconds)."""

    shy: bool
    """
    When `True`, the layer is "shy", meaning that it is hidden in the Layer
    panel if the composition's "Hide all shy layers" option is toggled on.
    """

    solo: bool
    """When `True`, the layer is soloed."""

    stretch: float
    """
    The layer's time stretch, expressed as a percentage. A value of 100 means
    no stretch. Values between 0 and 1 are set to 1, and values between -1 and
    0 (not including 0) are set to -1.
    """

    time: float
    """
    The current time of the layer, expressed in composition time (seconds).
    """

    is_name_set: bool = field(init=False)

    # Set after parsing - reference to parent layer (not serialized)
    _parent: Layer | None = field(default=None, init=False, repr=False)

    # Use identity-based equality to avoid comparing all fields recursively,
    # which could produce unexpected results or hit circular references.
    __eq__ = object.__eq__
    __hash__ = object.__hash__

    @property
    def active(self) -> bool:
        """
        When `True`, the layer is active at the current time.

        Overrides [PropertyBase.active][] to evaluate
        [active_at_time][] at [time][].
        """
        return self.active_at_time(self.time)

    @property
    def transform(self) -> PropertyGroup:
        """
        Contains a layer's transform properties.

        This is the Transform `PropertyGroup` (match name
        ``ADBE Transform Group``). Individual transform properties (Position,
        Scale, Rotation, etc.) are accessible via
        [properties][PropertyGroup.properties].
        """
        return self["ADBE Transform Group"]

    @property
    def effects(self) -> PropertyGroup | None:
        """
        Contains a layer's effects.

        This is the Effects `PropertyGroup` (match name ``ADBE Effect Parade``).
        Each child in [properties][PropertyGroup.properties] is itself a
        [PropertyGroup][] representing one effect. `None` when the layer has no
        effects.
        """
        try:
            group = self["ADBE Effect Parade"]
        except KeyError:
            return None
        return group if group.properties else None

    @property
    def masks(self) -> PropertyGroup | None:
        """
        Contains a layer's masks.

        This is the Masks `PropertyGroup` (match name ``ADBE Mask Parade``).
        Each child in [properties][PropertyGroup.properties] is itself a
        [PropertyGroup][] representing one mask. `None` when the layer has no
        masks.
        """
        try:
            group = self["ADBE Mask Parade"]
        except KeyError:
            return None
        return group if group.properties else None

    @property
    def text(self) -> PropertyGroup | None:
        """Contains a layer's text properties (if any)."""
        try:
            return self["ADBE Text Properties"]
        except KeyError:
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

        For this method to return ``True``, three conditions must be met:

        1. The layer must be [enabled][].
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

    def __post_init__(self) -> None:
        """Set computed fields after initialization."""
        self.is_name_set = bool(self.name)
