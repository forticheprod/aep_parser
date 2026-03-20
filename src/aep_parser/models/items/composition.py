from __future__ import annotations

import typing
from typing import Any, List, cast

from ...descriptors import ChunkField, ChunkInstanceField
from ...reverses import (
    denormalize_values,
    reverse_fractional,
    reverse_frame_ticks,
    reverse_ratio,
)
from ...transforms import normalize_values
from ...validators import (
    validate_all,
    validate_gte_field,
    validate_number,
    validate_sequence,
)
from ..layers.av_layer import AVLayer
from ..layers.camera_layer import CameraLayer
from ..layers.light_layer import LightLayer
from ..layers.shape_layer import ShapeLayer
from ..layers.text_layer import TextLayer
from ..layers.three_d_model_layer import ThreeDModelLayer
from ..properties.marker import MarkerValue
from ..sources.file import FileSource
from ..sources.placeholder import PlaceholderSource
from ..sources.solid import SolidSource
from .av_item import AVItem
from .footage import FootageItem

if typing.TYPE_CHECKING:
    from aep_parser.enums import Label

    from ...kaitai.aep import Aep  # type: ignore[attr-defined]
    from ..layers.layer import Layer
    from ..properties.property import Property
    from .folder import FolderItem


# ---------------------------------------------------------------------------
# Reverse helpers
# ---------------------------------------------------------------------------


_reverse_frame_rate = reverse_fractional("frame_rate_integer", "frame_rate_fractional")
_reverse_pixel_aspect = reverse_ratio("pixel_ratio")
_reverse_display_start_time = reverse_ratio("display_start_time")
_reverse_display_start_frame = reverse_frame_ticks("display_start_time")
_reverse_duration = reverse_ratio("duration")
_reverse_frame_duration = reverse_frame_ticks("duration")
_reverse_work_area_start = reverse_ratio("in_point")


def _reverse_work_area_duration(value: float, body: Any) -> dict[str, int]:
    """Reverse work area duration: sets out_point = in_point + value."""
    _DIVISOR = 10000
    work_start = body.in_point_dividend / body.in_point_divisor
    return {
        "out_point_dividend": round((work_start + value) * _DIVISOR),
        "out_point_divisor": _DIVISOR,
    }


class CompItem(AVItem):
    """
    The `CompItem` object represents a composition, and allows you to
    manipulate and get information about it.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
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

    bg_color = ChunkField[list[float]](
        "_cdta",
        "bg_color",
        transform=normalize_values,
        reverse=denormalize_values,
        validate=validate_sequence(length=3, min=0.0, max=1.0),
    )
    """The background color of the composition. The three array values specify
the red, green, and blue components of the color. Read / Write."""

    draft3d = ChunkField[bool]("_cdta", "draft3d", transform=bool, reverse=bool)
    """When `True`, Draft 3D mode is enabled for the composition.
    Read / Write.

Warning:
    Deprecated in After Effects 2024 in favor of the new Draft 3D mode."""

    frame_blending = ChunkField[bool](
        "_cdta", "frame_blending", transform=bool, reverse=bool
    )
    """When `True`, frame blending is enabled for this Composition. Corresponds
    to the value of the Frame Blending button in the Composition panel.
    Read / Write."""

    hide_shy_layers = ChunkField[bool](
        "_cdta", "hide_shy_layers", transform=bool, reverse=bool
    )
    """When `True`, only layers with `shy` set to `False` are shown in the
    Timeline panel. When `False`, all layers are visible, including those
    whose `shy` value is `True`. Corresponds to the value of the Hide All
    Shy Layers button in the Composition panel. Read / Write."""

    motion_blur = ChunkField[bool]("_cdta", "motion_blur", transform=bool, reverse=bool)
    """When `True`, motion blur is enabled for the composition. Corresponds
    to the value of the Motion Blur button in the Composition panel.
    Read / Write."""

    preserve_nested_frame_rate = ChunkField[bool](
        "_cdta", "preserve_nested_frame_rate", transform=bool, reverse=bool
    )
    """When `True`, the frame rate of nested compositions is preserved in
    the current composition. Corresponds to the value of the "Preserve frame
    rate when nested or in render queue" option in the Advanced tab of the
    Composition Settings dialog box. Read / Write."""

    preserve_nested_resolution = ChunkField[bool](
        "_cdta", "preserve_nested_resolution", transform=bool, reverse=bool
    )
    """When `True`, the resolution of nested compositions is preserved in
    the current composition. Corresponds to the value of the "Preserve
    Resolution When Nested" option in the Advanced tab of the Composition
    Settings dialog box. Read / Write."""

    width = ChunkField[int](
        "_cdta", "width", reverse=int, validate=validate_number(min=4, max=30000, integer=True)
    )
    """The width of the item in pixels. Read / Write."""

    height = ChunkField[int](
        "_cdta", "height", reverse=int, validate=validate_number(min=4, max=30000, integer=True)
    )
    """The height of the item in pixels. Read / Write."""

    shutter_angle = ChunkField[int](
        "_cdta",
        "shutter_angle",
        reverse=int,
        validate=validate_number(min=0, max=720, integer=True),
    )
    """The shutter angle setting for the composition. This corresponds to the
    Shutter Angle setting in the Advanced tab of the Composition Settings
    dialog box. Read / Write."""

    shutter_phase = ChunkField[int](
        "_cdta",
        "shutter_phase",
        reverse=int,
        validate=validate_number(min=-360, max=360, integer=True),
    )
    """The shutter phase setting for the composition. This corresponds to the
    Shutter Phase setting in the Advanced tab of the Composition Settings
    dialog box. Read / Write."""

    resolution_factor = ChunkField[list[int]](
        "_cdta",
        "resolution_factor",
        transform=list,
        reverse=list,
        validate=validate_sequence(length=2, min=0.0, max=1.0),
    )
    """The x and y downsample resolution factors for rendering the
    composition. The two values in the array specify how many pixels to skip
    when sampling; the first number controls horizontal sampling, the second
    controls vertical sampling. Full resolution is [1, 1], half resolution
    is [2, 2], and quarter resolution is [4, 4]. The default is [1, 1].
    Read / Write."""

    motion_blur_adaptive_sample_limit = ChunkField[int](
        "_cdta",
        "motion_blur_adaptive_sample_limit",
        reverse=int,
        validate=validate_all(
            validate_number(min=2, max=256, integer=True),
            validate_gte_field("motion_blur_samples_per_frame"),
        ),
    )
    """The maximum number of motion blur samples of 2D layer motion. This
    corresponds to the Adaptive Sample Limit setting in the Advanced tab of
    the Composition Settings dialog box. Must be >= `samples_per_frame`.
    Read / Write."""

    motion_blur_samples_per_frame = ChunkField[int](
        "_cdta",
        "motion_blur_samples_per_frame",
        reverse=int,
        validate=validate_number(min=2, max=64, integer=True),
    )
    """The minimum number of motion blur samples per frame for Classic 3D
    layers, shape layers, and certain effects. This corresponds to the
    Samples Per Frame setting in the Advanced tab of the Composition
    Settings dialog box. Read / Write."""

    frame_rate = ChunkInstanceField[float](
        "_cdta",
        "frame_rate",
        reverse=_reverse_frame_rate,
        validate=validate_number(min=1.0, max=999.0),
        invalidates=[
            "frame_rate",
            "frame_duration",
            "frame_time",
            "frame_in_point",
            "frame_out_point",
            "display_start_frame",
        ],
    )
    """The frame rate of the item in frames-per-second. Read / Write."""

    duration = ChunkInstanceField[float](
        "_cdta",
        "duration",
        reverse=_reverse_duration,
        validate=validate_number(min=0.0, max=10800.0),
        invalidates=["duration", "frame_duration"],
    )
    """The duration of the item in seconds. Read / Write."""

    frame_duration = ChunkInstanceField[int](
        "_cdta",
        "frame_duration",
        transform=int,
        reverse=_reverse_frame_duration,
        validate=validate_number(min=1, integer=True),
        invalidates=["duration", "frame_duration"],
    )
    """The duration of the item in frames. Read / Write."""

    pixel_aspect = ChunkInstanceField[float](
        "_cdta",
        "pixel_aspect",
        reverse=_reverse_pixel_aspect,
        validate=validate_number(min=0.01, max=100.0),
        invalidates=["pixel_aspect"],
    )
    """The pixel aspect ratio of the item (1.0 is square). Read / Write."""

    time_scale = ChunkInstanceField[float]("_cdta", "time_scale")
    """The time scale, used as a divisor for keyframe time values. For
    integer frame rates (e.g. 24fps) this is a whole number. For non-integer
    frame rates (e.g. 29.97fps) this includes a fractional part (e.g.
    3.125). Read-only."""

    display_start_time = ChunkInstanceField[float](
        "_cdta",
        "display_start_time",
        reverse=_reverse_display_start_time,
        validate=validate_number(min=-10800.0, max=86340.0),
        invalidates=[
            "display_start_time",
            "display_start_frame",
            "in_point",
            "frame_in_point",
            "out_point",
            "frame_out_point",
            "work_area_start",
            "work_area_start_frame",
            "work_area_duration",
            "work_area_duration_frame",
        ],
    )
    """The time set as the beginning of the composition, in seconds. This
    is the equivalent of the Start Timecode or Start Frame setting in the
    Composition Settings dialog box. Read / Write."""

    display_start_frame = ChunkInstanceField[int](
        "_cdta",
        "display_start_frame",
        transform=int,
        reverse=_reverse_display_start_frame,
        invalidates=[
            "display_start_time",
            "display_start_frame",
            "in_point",
            "frame_in_point",
            "out_point",
            "frame_out_point",
            "work_area_start",
            "work_area_start_frame",
            "work_area_duration",
            "work_area_duration_frame",
        ],
    )
    """The frame value of the beginning of the composition. Read / Write."""

    in_point = ChunkInstanceField[float](
        "_cdta",
        "in_point",
    )
    """The composition "work area" start (seconds). Read-only."""

    frame_in_point = ChunkInstanceField[int](
        "_cdta",
        "frame_in_point",
        transform=int,
    )
    """The composition "work area" start (frames). Read-only."""

    out_point = ChunkInstanceField[float](
        "_cdta",
        "out_point",
    )
    """The composition "work area" end (seconds). Read-only."""

    frame_out_point = ChunkInstanceField[int](
        "_cdta",
        "frame_out_point",
        transform=int,
    )
    """The composition "work area" end (frames). Read-only."""

    work_area_start = ChunkInstanceField[float](
        "_cdta",
        "work_area_start",
        reverse=_reverse_work_area_start,
        invalidates=[
            "in_point",
            "frame_in_point",
            "work_area_start",
            "work_area_start_frame",
            "work_area_duration",
            "work_area_duration_frame",
        ],
    )
    """The work area start time relative to composition start.
    Read / Write."""

    work_area_start_frame = ChunkInstanceField[int](
        "_cdta",
        "work_area_start_frame",
        transform=int,
    )
    """The work area start frame relative to composition start.
    Read-only."""

    work_area_duration = ChunkInstanceField[float](
        "_cdta",
        "work_area_duration",
        reverse=_reverse_work_area_duration,
        invalidates=[
            "out_point",
            "frame_out_point",
            "work_area_start",
            "work_area_start_frame",
            "work_area_duration",
            "work_area_duration_frame",
        ],
    )
    """The work area duration in seconds. Read / Write."""

    work_area_duration_frame = ChunkInstanceField[int](
        "_cdta",
        "work_area_duration_frame",
        transform=int,
    )
    """The work area duration in frames. Read-only."""

    time = ChunkInstanceField[float]("_cdta", "time")
    """The playhead timestamp, in composition time (seconds). Read-only."""

    frame_time = ChunkInstanceField[int]("_cdta", "frame_time", transform=int)
    """The playhead timestamp, in composition time (frame). Read-only."""

    # ---- Chunk-backed descriptor (cdrp) ----

    drop_frame = ChunkField[bool](
        "_cdrp", "drop_frame", transform=bool, reverse=bool, default=False
    )
    """When `True`, timecode is displayed in drop-frame format. Only
    applicable when `frameRate` is 29.97 or 59.94. Read / Write."""

    # ---- Regular attributes set in __init__ ----

    layers: list[Layer]
    """All the [Layer][] objects for layers in this composition."""

    marker_property: Property | None
    """The composition's marker property."""

    def __init__(
        self,
        *,
        comment: str,
        id: int,
        label: Label,
        name: str,
        parent_folder: FolderItem | None,
        cdta: Aep.CdtaBody,
        cdrp: Aep.CdrpBody | None,
        layers: list[Layer] | None = None,
        marker_property: Property | None = None,
    ) -> None:
        self._cdta = cdta
        self._cdrp = cdrp

        # Skip AVItem's extra params - they're all descriptor-backed on
        # CompItem and read directly from the cdta chunk body.
        super().__init__(
            comment=comment,
            id=id,
            label=label,
            name=name,
            parent_folder=parent_folder,
            type_name="Composition",
        )

        self.layers: list[Layer] = layers if layers is not None else []
        self.marker_property = marker_property

        # Cached layer-type lists
        self._av_layers: list[AVLayer] | None = None
        self._composition_layers: list[AVLayer] | None = None
        self._footage_layers: list[AVLayer] | None = None
        self._file_layers: list[AVLayer] | None = None
        self._solid_layers: list[AVLayer] | None = None
        self._placeholder_layers: list[AVLayer] | None = None
        self._text_layers: list[TextLayer] | None = None
        self._shape_layers: list[ShapeLayer] | None = None
        self._camera_layers: list[CameraLayer] | None = None
        self._light_layers: list[LightLayer] | None = None
        self._three_d_model_layers: list[ThreeDModelLayer] | None = None
        self._null_layers: list[Layer] | None = None
        self._adjustment_layers: list[AVLayer] | None = None
        self._three_d_layers: list[AVLayer] | None = None
        self._guide_layers: list[AVLayer] | None = None
        self._solo_layers: list[Layer] | None = None

    @property
    def markers(self) -> list[MarkerValue]:
        """A flat list of [MarkerValue][] objects for this composition.

        Shortcut for accessing marker data without navigating the property
        tree.  Returns an empty list when the composition has no markers.

        Example:
            ```python
            for marker in comp.markers:
                print(marker.comment)
            ```
        """
        if self.marker_property is None:
            return []
        return cast(
            List[MarkerValue],  # Cannot use `list` for Py3.7`
            [kf.value for kf in self.marker_property.keyframes],
        )

    def __iter__(self) -> typing.Iterator[Layer]:
        """Return an iterator over the composition's layers."""
        return iter(self.layers)

    @property
    def num_layers(self) -> int:
        """The number of layers in the composition."""
        return len(self.layers)

    @property
    def active_camera(self) -> CameraLayer | None:
        """The front-most enabled camera layer, or `None`.

        Returns the first [CameraLayer][] that is active at the current
        composition time. The value is `None` when the composition
        contains no active camera layers.
        """
        for layer in self.camera_layers:
            if layer.active:
                return layer
        return None

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
    def three_d_model_layers(self) -> list[ThreeDModelLayer]:
        """A list of the 3D model layers in this composition."""
        if self._three_d_model_layers is None:
            self._three_d_model_layers = [
                layer for layer in self.layers if isinstance(layer, ThreeDModelLayer)
            ]
        return self._three_d_model_layers

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
