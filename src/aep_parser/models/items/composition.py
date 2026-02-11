from __future__ import annotations

import typing
from dataclasses import dataclass, field
from typing import cast

from .av_item import AVItem

if typing.TYPE_CHECKING:
    from ..layers.av_layer import AVLayer
    from ..layers.layer import Layer
    from ..properties.marker import MarkerValue


@dataclass
class CompItem(AVItem):
    """
    The `CompItem` object represents a composition, and allows you to
    manipulate and get information about it.

    Info:
        `Item` is the base class for `AVItem` object and for `FolderItem`
        object, which are in turn the base classes for various other item
        types, so `Item` attributes and methods are available when working with
        all of these item types.

    See: https://ae-scripting.docsforadobe.dev/item/compitem/"""

    bg_color: list[float]
    """
    The background color of the composition. The three array values specify
    the red, green, and blue components of the color.
    """

    display_start_frame: int
    """The frame value of the beginning of the composition."""

    display_start_time: float
    """
    The time set as the beginning of the composition, in seconds. This is the
    equivalent of the Start Timecode or Start Frame setting in the Composition
    Settings dialog box.
    """

    frame_blending: bool
    """
    When `True`, frame blending is enabled for this Composition. Corresponds to
    the value of the Frame Blending button in the Composition panel.
    """

    hide_shy_layers: bool
    """
    When `True`, only layers with `shy` set to `False` are shown in the
    Timeline panel. When `False`, all layers are visible, including those whose
    `shy` value is `True`. Corresponds to the value of the Hide All Shy Layers
    button in the Composition panel.
    """

    layers: list[Layer]
    """All the `Layer` objects for layers in this composition."""

    markers: list[MarkerValue]
    """All the composition's markers."""

    motion_blur: bool
    """
    When `True`, motion blur is enabled for the composition. Corresponds to
    the value of the Motion Blur button in the Composition panel.
    """

    motion_blur_adaptive_sample_limit: int
    """
    The maximum number of motion blur samples of 2D layer motion. This
    corresponds to the Adaptive Sample Limit setting in the Advanced tab of
    the Composition Settings dialog box.
    """

    motion_blur_samples_per_frame: int
    """
    The minimum number of motion blur samples per frame for Classic 3D layers,
    shape layers, and certain effects. This corresponds to the Samples Per
    Frame setting in the Advanced tab of the Composition Settings dialog box.
    """

    preserve_nested_frame_rate: bool
    """
    When `True`, the frame rate of nested compositions is preserved in the
    current composition. Corresponds to the value of the "Preserve frame rate
    when nested or in render queue" option in the Advanced tab of the
    Composition Settings dialog box.
    """

    preserve_nested_resolution: bool
    """
    When `True`, the resolution of nested compositions is preserved in the
    current composition. Corresponds to the value of the "Preserve Resolution
    When Nested" option in the Advanced tab of the Composition Settings dialog
    box.
    """

    shutter_angle: int
    """
    The shutter angle setting for the composition. This corresponds to the
    Shutter Angle setting in the Advanced tab of the Composition Settings
    dialog box.
    """

    shutter_phase: int
    """
    The shutter phase setting for the composition. This corresponds to the
    Shutter Phase setting in the Advanced tab of the Composition Settings
    dialog box.
    """

    resolution_factor: list[int]
    """
    The x and y downsample resolution factors for rendering the composition.
    The two values in the array specify how many pixels to skip when sampling;
    the first number controls horizontal sampling, the second controls vertical
    sampling. Full resolution is [1, 1], half resolution is [2, 2], and quarter
    resolution is [4, 4]. The default is [1, 1].
    """

    time_scale: int
    """The time scale, used as a divisor for some time values."""

    in_point: float
    """The composition "work area" start (seconds)."""

    frame_in_point: int
    """The composition "work area" start (frames)."""

    out_point: float
    """The composition "work area" end (seconds)."""

    frame_out_point: int
    """The composition "work area" end (frames)."""

    frame_time: int
    """The playhead timestamp, in composition time (frame)."""

    time: float
    """The playhead timestamp, in composition time (seconds)."""

    _composition_layers: list[AVLayer] | None = field(
        default=None, init=False, repr=False
    )
    _footage_layers: list[AVLayer] | None = field(
        default=None, init=False, repr=False
    )

    @property
    def work_area_start(self) -> float:
        """The work area start time relative to composition start."""
        return self.in_point - self.display_start_time

    @property
    def work_area_start_frame(self) -> int:
        """The work area start frame relative to composition start."""
        return self.frame_in_point - self.display_start_frame

    @property
    def work_area_duration(self) -> float:
        """The work area duration in seconds."""
        return self.out_point - self.in_point

    @property
    def work_area_duration_frame(self) -> int:
        """The work area duration in frames."""
        return self.frame_out_point - self.frame_in_point

    def __iter__(self) -> typing.Iterator[Layer]:
        """Return an iterator over the composition's layers."""
        return iter(self.layers)

    def layer(
        self,
        name: str | None = None,
        index: int | None = None,
        other_layer: Layer | None = None,
        rel_index: int | None = None,
    ) -> Layer:
        """
        Get a Layer object by name, index, or relative to another layer.

        Args:
            name: The name of the layer to return.
            index: The index position of the layer to return.
            other_layer: A Layer object to use as a reference for the relative
                index position of the layer to return.
            rel_index: The index position of the layer relative to the
                other_layer to return.
        """
        if name:
            for layer in self.layers:
                if layer.name == name:
                    return layer
            raise ValueError(f"Layer with name '{name}' not found")
        elif index:
            return self.layers[index]
        elif other_layer and rel_index:
            return self.layers[self.layers.index(other_layer) + rel_index]
        raise ValueError("Must specify one of name, index, or other_layer and rel_index")

    @property
    def composition_layers(self) -> list[AVLayer]:
        """A list of the composition layers whose source are compositions."""
        if self._composition_layers is None:
            self._composition_layers = [
                cast(AVLayer, layer) for layer in self.layers
                if hasattr(layer, "source") and layer.source is not None
                and layer.source.is_composition
            ]
        return self._composition_layers

    @property
    def footage_layers(self) -> list[AVLayer]:
        """A list of the composition layers whose source are footages."""
        if self._footage_layers is None:
            self._footage_layers = [
                cast(AVLayer, layer) for layer in self.layers
                if hasattr(layer, "source") and layer.source is not None
                and layer.source.is_footage
            ]
        return self._footage_layers
