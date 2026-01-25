from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from ...kaitai.aep import Aep
    from ..properties.marker import Marker
    from ..properties.property import Property
    from ..properties.property_group import PropertyGroup


class Layer:
    def __init__(
        self,
        auto_orient: bool,
        comment: str,
        effects: list[PropertyGroup],
        enabled: bool,
        frame_in_point: int,
        frame_out_point: int,
        frame_start_time: int,
        in_point: float,
        label: Aep.Label,
        layer_id: int,
        layer_type: Aep.LayerType,
        locked: bool,
        markers: list[Marker],
        name: str,
        null_layer: bool,
        out_point: float,
        parent_id: int | None,
        start_time: float,
        shy: bool,
        solo: bool,
        stretch: float | None,
        text: PropertyGroup | list,
        time: float,
        transform: list[Property],
        containing_comp_id: int | None = None,
    ):
        """
        Base class for layers.

        Args:
            auto_orient: The type of automatic orientation to perform for the
                layer.
            comment: A descriptive comment for the layer.
            containing_comp_id: The ID of the composition that contains this
                layer.
            effects: Contains a layer's effects (if any).
            enabled: Corresponds to the video switch state of the layer in the
                Timeline panel.
            frame_in_point: The "in" point of the layer, expressed in
                composition time (frames).
            frame_out_point: The "out" point of the layer, expressed in
                composition time (frames).
            frame_start_time: The start time of the layer, expressed in
                composition time (frames).
            in_point: The "in" point of the layer, expressed in composition
                time (seconds).
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
                time (seconds).
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
        self.enabled = enabled
        self.auto_orient = auto_orient
        self.comment = comment
        self.frame_in_point = frame_in_point
        self.frame_out_point = frame_out_point
        self.frame_start_time = frame_start_time
        self.in_point = in_point
        self.is_name_set = bool(name)
        self.layer_id = layer_id
        self.layer_type = layer_type
        self.label = label
        self.locked = locked
        self.name = name
        self.null_layer = null_layer
        self.out_point = out_point
        self.parent_id = parent_id
        self.shy = shy
        self.solo = solo
        self.start_time = start_time
        self.stretch = stretch
        self.time = time
        self.transform = transform
        self.effects = effects
        self.text = text
        self.markers = markers
        self.containing_comp_id = containing_comp_id

    def __repr__(self) -> str:
        return str(self.__dict__)
