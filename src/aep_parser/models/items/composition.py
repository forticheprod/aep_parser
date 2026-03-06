from __future__ import annotations

import typing
from dataclasses import dataclass, field
from typing import cast

from ..layers.av_layer import AVLayer
from ..layers.camera_layer import CameraLayer
from ..layers.light_layer import LightLayer
from ..layers.shape_layer import ShapeLayer
from ..layers.text_layer import TextLayer
from ..sources.file import FileSource
from ..sources.placeholder import PlaceholderSource
from ..sources.solid import SolidSource
from .av_item import AVItem
from .footage import FootageItem

if typing.TYPE_CHECKING:
    from ..layers.layer import Layer
    from ..properties.marker import MarkerValue


@dataclass(eq=False)
class CompItem(AVItem):
    """
    The `CompItem` object represents a composition, and allows you to
    manipulate and get information about it.

    Example:
        ```python
        import aep_parser

        app = aep_parser.parse("project.aep")
        comp = app.project.compositions[0]
        print(comp.frame_rate)
        for layer in comp:
            ...
        ```

    Info:
        [Item][] is the base class for [AVItem][] object and for [FolderItem][]
        object, which are in turn the base classes for various other item
        types, so [Item][] attributes and methods are available when working with
        all of these item types.

    See: https://ae-scripting.docsforadobe.dev/item/compitem/"""

    bg_color: list[float]
    """
    The background color of the composition. The three array values specify
    the red, green, and blue components of the color.
    """

    display_start_frame: int
    """The frame value of the beginning of the composition."""

    draft3d: bool
    """
    When `True`, Draft 3D mode is enabled for the composition. This
    improves preview speed by disabling certain 3D rendering features.

    Warning:
        Deprecated in After Effects 2024 in favor of the new Draft 3D mode.
    """

    drop_frame: bool
    """
    When `True`, timecode is displayed in drop-frame format. Only applicable
    when `frameRate` is 29.97 or 59.94.
    """

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
    """All the [Layer][] objects for layers in this composition."""

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

    time_scale: float
    """
    The time scale, used as a divisor for keyframe time values. For integer
    frame rates (e.g. 24fps) this is a whole number. For non-integer frame
    rates (e.g. 29.97fps) this includes a fractional part (e.g. 3.125).
    """

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

    _av_layers: list[AVLayer] | None = field(default=None, init=False, repr=False)
    _composition_layers: list[AVLayer] | None = field(
        default=None, init=False, repr=False
    )
    _footage_layers: list[AVLayer] | None = field(default=None, init=False, repr=False)
    _file_layers: list[AVLayer] | None = field(default=None, init=False, repr=False)
    _solid_layers: list[AVLayer] | None = field(default=None, init=False, repr=False)
    _placeholder_layers: list[AVLayer] | None = field(
        default=None, init=False, repr=False
    )
    _text_layers: list[TextLayer] | None = field(default=None, init=False, repr=False)
    _shape_layers: list[ShapeLayer] | None = field(default=None, init=False, repr=False)
    _camera_layers: list[CameraLayer] | None = field(
        default=None, init=False, repr=False
    )
    _light_layers: list[LightLayer] | None = field(default=None, init=False, repr=False)
    _null_layers: list[Layer] | None = field(default=None, init=False, repr=False)
    _adjustment_layers: list[AVLayer] | None = field(
        default=None, init=False, repr=False
    )
    _three_d_layers: list[AVLayer] | None = field(default=None, init=False, repr=False)
    _guide_layers: list[AVLayer] | None = field(default=None, init=False, repr=False)
    _solo_layers: list[Layer] | None = field(default=None, init=False, repr=False)

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
        elif index is not None:
            return self.layers[index]
        elif other_layer and rel_index:
            return self.layers[self.layers.index(other_layer) + rel_index]
        raise ValueError(
            "Must specify one of name, index, or other_layer and rel_index"
        )

    @property
    def av_layers(self) -> list[AVLayer]:
        """A list of all [AVLayer][] objects in this composition."""
        if self._av_layers is None:
            self._av_layers = [
                layer for layer in self.layers if isinstance(layer, AVLayer)
            ]
        return self._av_layers

    @property
    def composition_layers(self) -> list[AVLayer]:
        """A list of the composition layers whose source are compositions."""
        if self._composition_layers is None:
            self._composition_layers = [
                layer
                for layer in self.av_layers
                if layer.source is not None and layer.source.is_composition
            ]
        return self._composition_layers

    @property
    def footage_layers(self) -> list[AVLayer]:
        """A list of the composition layers whose source are footages."""
        if self._footage_layers is None:
            self._footage_layers = [
                layer
                for layer in self.av_layers
                if layer.source is not None and layer.source.is_footage
            ]
        return self._footage_layers

    @property
    def file_layers(self) -> list[AVLayer]:
        """A list of the layers whose source are file footages."""
        if self._file_layers is None:
            self._file_layers = [
                layer
                for layer in self.footage_layers
                if isinstance(cast(FootageItem, layer.source).main_source, FileSource)
            ]
        return self._file_layers

    @property
    def solid_layers(self) -> list[AVLayer]:
        """A list of the layers whose source are solids."""
        if self._solid_layers is None:
            self._solid_layers = [
                layer
                for layer in self.footage_layers
                if isinstance(cast(FootageItem, layer.source).main_source, SolidSource)
            ]
        return self._solid_layers

    @property
    def placeholder_layers(self) -> list[AVLayer]:
        """A list of the layers whose source are placeholders."""
        if self._placeholder_layers is None:
            self._placeholder_layers = [
                layer
                for layer in self.footage_layers
                if isinstance(
                    cast(FootageItem, layer.source).main_source,
                    PlaceholderSource,
                )
            ]
        return self._placeholder_layers

    @property
    def text_layers(self) -> list[TextLayer]:
        """A list of the text layers in this composition."""
        if self._text_layers is None:
            self._text_layers = [
                layer for layer in self.layers if isinstance(layer, TextLayer)
            ]
        return self._text_layers

    @property
    def shape_layers(self) -> list[ShapeLayer]:
        """A list of the shape layers in this composition."""
        if self._shape_layers is None:
            self._shape_layers = [
                layer for layer in self.layers if isinstance(layer, ShapeLayer)
            ]
        return self._shape_layers

    @property
    def camera_layers(self) -> list[CameraLayer]:
        """A list of the camera layers in this composition."""
        if self._camera_layers is None:
            self._camera_layers = [
                layer for layer in self.layers if isinstance(layer, CameraLayer)
            ]
        return self._camera_layers

    @property
    def light_layers(self) -> list[LightLayer]:
        """A list of the light layers in this composition."""
        if self._light_layers is None:
            self._light_layers = [
                layer for layer in self.layers if isinstance(layer, LightLayer)
            ]
        return self._light_layers

    @property
    def null_layers(self) -> list[Layer]:
        """A list of the null layers in this composition."""
        if self._null_layers is None:
            self._null_layers = [layer for layer in self.layers if layer.null_layer]
        return self._null_layers

    @property
    def adjustment_layers(self) -> list[AVLayer]:
        """A list of the adjustment layers in this composition."""
        if self._adjustment_layers is None:
            self._adjustment_layers = [
                layer for layer in self.av_layers if layer.adjustment_layer
            ]
        return self._adjustment_layers

    @property
    def three_d_layers(self) -> list[AVLayer]:
        """A list of the 3D layers in this composition."""
        if self._three_d_layers is None:
            self._three_d_layers = [
                layer for layer in self.av_layers if layer.three_d_layer
            ]
        return self._three_d_layers

    @property
    def guide_layers(self) -> list[AVLayer]:
        """A list of the guide layers in this composition."""
        if self._guide_layers is None:
            self._guide_layers = [
                layer for layer in self.av_layers if layer.guide_layer
            ]
        return self._guide_layers

    @property
    def solo_layers(self) -> list[Layer]:
        """A list of the soloed layers in this composition."""
        if self._solo_layers is None:
            self._solo_layers = [layer for layer in self.layers if layer.solo]
        return self._solo_layers
