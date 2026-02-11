from __future__ import annotations

import typing
from abc import ABC
from dataclasses import dataclass, field

if typing.TYPE_CHECKING:
    from ...kaitai import Aep
    from ..enums import AutoOrientType
    from ..items.composition import CompItem
    from ..properties.marker import MarkerValue
    from ..properties.property import Property
    from ..properties.property_group import PropertyGroup


@dataclass
class Layer(ABC):
    """
    The `Layer` object provides access to layers within compositions.

    Warning:
        In the ExtendScript API, `Layer` is a subclass of `PropertyGroup`,
        which is a subclass of `PropertyBase`. It is not the case here, as it
        made no sense conceptually.

    Info:
        `Layer` is the base class for `CameraLayer` object, `LightLayer`
        object and `AVLayer` object, so `Layer` attributes and methods are
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

    effects: list[PropertyGroup]
    """Contains a layer's effects (if any)."""

    enabled: bool
    """
    Corresponds to the video switch state of the layer in the Timeline panel.
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

    label: Aep.Label
    """
    The label color. Colors are represented by their number (0 for None, or 1
    to 16 for one of the preset colors in the Labels preferences).
    """

    layer_type: Aep.LayerType
    """The type of layer (footage, light, camera, text, shape)."""

    locked: bool
    """
    When `True`, the layer is locked. This corresponds to the lock toggle in
    the Layer panel.
    """

    markers: list[MarkerValue]
    """Contains a layer's markers."""

    name: str
    """The name of the layer."""

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

    parent_id: int | None
    """
    The ID of the layer's parent layer. `None` if the layer has no parent.
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

    text: PropertyGroup | None
    """Contains a layer's text properties (if any)."""

    time: float
    """
    The current time of the layer, expressed in composition time (seconds).
    """

    transform: list[Property]
    """Contains a layer's transform properties."""

    is_name_set: bool = field(init=False)

    # Set after parsing - reference to parent layer (not serialized)
    _parent: Layer | None = field(default=None, init=False, repr=False)

    @property
    def parent(self) -> Layer | None:
        """The parent layer for layer parenting. `None` if no parent."""
        return self._parent

    @parent.setter
    def parent(self, value: Layer | None) -> None:
        self._parent = value

    def __post_init__(self) -> None:
        """Set computed fields after initialization."""
        self.is_name_set = bool(self.name)
