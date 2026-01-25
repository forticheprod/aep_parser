from __future__ import annotations

import typing

from .av_item import AVItem

if typing.TYPE_CHECKING:
    from ..layers.av_layer import AVLayer
    from ..layers.layer import Layer
    from ..properties.marker import Marker


class CompItem(AVItem):
    def __init__(
        self,
        bg_color: list[float],
        display_start_frame: int,
        display_start_time: float,
        frame_blending: bool,
        hide_shy_layers: bool,
        layers: list[Layer],
        markers: list[Marker],
        motion_blur: bool,
        motion_blur_adaptive_sample_limit: int,
        motion_blur_samples_per_frame: int,
        preserve_nested_frame_rate: bool,
        preserve_nested_resolution: bool,
        shutter_angle: int,
        shutter_phase: int,
        resolution_factor: list[int],
        time_scale: int,
        in_point: float,
        frame_in_point: int,
        out_point: float,
        frame_out_point: int,
        frame_time: int,
        time: float,
        *args,
        **kwargs,
    ):
        """
        Object storing information about a composition.

        Args:
            bg_color: The background color of the composition. The three array
                values specify the red, green, and blue components of the color.
            display_start_frame: The frame value of the beginning of the
                composition.
            display_start_time: The time set as the beginning of the composition,
                in seconds. This is the equivalent of the Start Timecode or Start
                Frame setting in the Composition Settings dialog box.
            frame_blending: When true, frame blending is enabled for this
                Composition. Corresponds to the value of the Frame Blending
                button in the Composition panel.
            hide_shy_layers: When true, only layers with shy set to false are
                shown in the Timeline panel. When false, all layers are visible,
                including those whose shy value is true. Corresponds to the value
                of the Hide All Shy Layers button in the Composition panel.
            layers: All the Layer objects for layers in this composition.
            markers: All the composition's markers.
            motion_blur: When true, motion blur is enabled for the composition.
                Corresponds to the value of the Motion Blur button in the
                Composition panel.
            motion_blur_adaptive_sample_limit: The maximum number of motion blur
                samples of 2D layer motion. This corresponds to the Adaptive
                Sample Limit setting in the Advanced tab of the Composition
                Settings dialog box.
            motion_blur_samples_per_frame: The minimum number of motion blur
                samples per frame for Classic 3D layers, shape layers, and
                certain effects. This corresponds to the Samples Per Frame
                setting in the Advanced tab of the Composition Settings dialog
                box.
            preserve_nested_frame_rate: When true, the frame rate of nested
                compositions is preserved in the current composition. Corresponds
                to the value of the "Preserve frame rate when nested or in render
                queue" option in the Advanced tab of the Composition Settings
                dialog box.
            preserve_nested_resolution: When true, the resolution of nested
                compositions is preserved in the current composition. Corresponds
                to the value of the "Preserve Resolution When Nested" option in
                the Advanced tab of the Composition Settings dialog box.
            shutter_angle: The shutter angle setting for the composition. This
                corresponds to the Shutter Angle setting in the Advanced tab of
                the Composition Settings dialog box.
            shutter_phase: The shutter phase setting for the composition. This
                corresponds to the Shutter Phase setting in the Advanced tab of
                the Composition Settings dialog box.
            resolution_factor: The x and y downsample resolution factors for
                rendering the composition. The two values in the array specify
                how many pixels to skip when sampling; the first number controls
                horizontal sampling, the second controls vertical sampling. Full
                resolution is [1, 1], half resolution is [2, 2], and quarter
                resolution is [4, 4]. The default is [1, 1].
            time_scale: The time scale, used as a divisor for some time values.
            in_point: The composition "work area" start (seconds).
            frame_in_point: The composition "work area" start (frames).
            out_point: The composition "work area" end (seconds).
            frame_out_point: The composition "work area" end (frames).
            frame_time: The playhead timestamp, in composition time (frame).
            time: The playhead timestamp, in composition time (seconds).
        """
        super().__init__(*args, **kwargs)
        self.bg_color = bg_color
        self.display_start_frame = display_start_frame
        self.display_start_time = display_start_time
        self.frame_blending = frame_blending
        self.hide_shy_layers = hide_shy_layers
        self.layers = layers
        self.markers = markers
        self.motion_blur = motion_blur
        self.motion_blur_adaptive_sample_limit = motion_blur_adaptive_sample_limit
        self.motion_blur_samples_per_frame = motion_blur_samples_per_frame
        self.preserve_nested_frame_rate = preserve_nested_frame_rate
        self.preserve_nested_resolution = preserve_nested_resolution
        self.resolution_factor = resolution_factor
        self.shutter_angle = shutter_angle
        self.shutter_phase = shutter_phase
        self.time_scale = time_scale
        self.in_point = in_point
        self.work_area_start = in_point - display_start_time
        self.frame_in_point = frame_in_point
        self.work_area_start_frame = frame_in_point - display_start_frame
        self.out_point = out_point
        self.frame_out_point = frame_out_point
        self.time = time
        self.frame_time = frame_time
        self.work_area_duration = self.out_point - self.in_point
        self.work_area_duration_frame = self.frame_out_point - self.frame_in_point
        self._composition_layers = None
        self._footage_layers = None

    def __iter__(self) -> typing.Iterator[Layer]:
        """Return an iterator over the composition's layers."""
        return iter(self.layers)

    def layer(
        self,
        name: str | None = None,
        index: int | None = None,
        other_layer: Layer | None = None,
        rel_index: int | None = None,
    ) -> Layer | None:
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
            return None
        elif index:
            return self.layers[index]
        elif other_layer and rel_index:
            return self.layers[self.layers.index(other_layer) + rel_index]
        else:
            return None

    @property
    def composition_layers(self) -> list[AVLayer]:
        """A list of the composition layers whose source are compositions."""
        if self._composition_layers is None:
            self._composition_layers = [
                layer for layer in self.layers if layer.source_is_composition
            ]
        return self._composition_layers

    @property
    def footage_layers(self) -> list[AVLayer]:
        """A list of the composition layers whose source are footages."""
        if self._footage_layers is None:
            self._footage_layers = [
                layer for layer in self.layers if layer.source_is_footage
            ]
        return self._footage_layers
