from __future__ import annotations

import typing
from abc import ABC
from dataclasses import dataclass, field

if typing.TYPE_CHECKING:
    from ...kaitai import Aep
    from ..enums import AutoOrientType
    from ..items.composition import CompItem
    from ..properties.marker import Marker
    from ..properties.property import Property
    from ..properties.property_group import PropertyGroup


@dataclass
class Layer(ABC):
    """
    Abstract base class for layers.

    Attributes:
        auto_orient: The type of automatic orientation to perform for the
            layer.
        comment: A descriptive comment for the layer.
        containing_comp: The composition that contains this layer. Set after
            parsing when the full project structure is available.
        effects: Contains a layer's effects (if any).
        enabled: Corresponds to the video switch state of the layer in the
            Timeline panel.
        frame_in_point: The "in" point of the layer, expressed in
            composition time (frames). This is the first frame where the
            layer becomes visible. The binary format stores this relative
            to start_time; parsed value is absolute composition time.
        frame_out_point: The "out" point of the layer, expressed in
            composition time (frames). This is the first frame where the
            layer is no longer visible. Clamped to composition duration
            to match ExtendScript behavior.
        frame_start_time: The start time of the layer, expressed in
            composition time (frames). This determines where the layer's
            first frame of content appears in the composition timeline.
        in_point: The "in" point of the layer, expressed in composition
            time (seconds). This is the time at which the layer starts
            being visible in the composition. The binary format stores
            this relative to start_time as a signed integer; parsed value
            is absolute composition time.
        label: The label color. Colors are represented by their number
            (0 for None, or 1 to 16 for one of the preset colors in the
            Labels preferences).
        layer_id: Unique and persistent identification number used
            internally to identify a Layer between sessions.
        layer_type: The type of layer (footage, light, camera, text, shape).
        locked: When true, the layer is locked. This corresponds to the
            lock toggle in the Layer panel.
        markers: Contains a layer's markers.
        name: The name of the layer.
        null_layer: When true, the layer was created as a null object.
        out_point: The "out" point of the layer, expressed in composition
            time (seconds). This is the time at which the layer stops
            being visible in the composition. Clamped to composition
            duration to match ExtendScript API behavior (a layer's
            out_point cannot exceed its containing composition's duration).
            The binary format stores this relative to start_time.
        parent_id: The ID of the layer's parent layer. None if the layer
            has no parent.
        shy: When true, the layer is "shy", meaning that it is hidden in
            the Layer panel if the composition's "Hide all shy layers"
            option is toggled on.
        solo: When true, the layer is soloed.
        start_time: The start time of the layer, expressed in composition
            time (seconds).
        stretch: The layer's time stretch, expressed as a percentage. A
            value of 100 means no stretch. Values between 0 and 1 are set
            to 1, and values between -1 and 0 (not including 0) are set
            to -1.
        text: Contains a layer's text properties (if any).
        time: The current time of the layer, expressed in composition time
            (seconds).
        transform: Contains a layer's transform properties.
    """

    auto_orient: AutoOrientType
    comment: str
    containing_comp: CompItem | None = field(repr=False)
    effects: list[PropertyGroup]
    enabled: bool
    frame_in_point: int
    frame_out_point: int
    frame_start_time: int
    in_point: float
    label: Aep.Label
    layer_id: int
    layer_type: Aep.LayerType
    locked: bool
    markers: list[Marker]
    name: str
    null_layer: bool
    out_point: float
    parent_id: int | None
    start_time: float
    shy: bool
    solo: bool
    stretch: float | None
    text: PropertyGroup | None
    time: float
    transform: list[Property]
    is_name_set: bool = field(init=False)

    # Set after parsing - reference to parent layer (not serialized)
    _parent: Layer | None = field(default=None, init=False, repr=False)

    @property
    def parent(self) -> Layer | None:
        """The parent layer for layer parenting. None if no parent."""
        return self._parent

    @parent.setter
    def parent(self, value: Layer | None) -> None:
        self._parent = value

    def __post_init__(self) -> None:
        """Set computed fields after initialization."""
        self.is_name_set = bool(self.name)
