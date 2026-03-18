from __future__ import annotations

import typing
from typing import List, cast

from ...descriptors import ChunkField, ChunkFlagField, ChunkInstanceField
from ...validators import validate_number, validate_one_of, validate_sequence
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

    from ...kaitai.aep import Aep
    from ..layers.layer import Layer
    from ..properties.property import Property
    from .folder import FolderItem


# ---------------------------------------------------------------------------
# Pixel aspect ratios allowed by After Effects (Composition Settings).
# ---------------------------------------------------------------------------

PIXEL_ASPECT_RATIOS: tuple[float, ...] = (
    1.0,    # Square Pixels
    0.91,   # D1/DV NTSC
    1.21,   # D1/DV NTSC Widescreen
    1.09,   # D1/DV PAL
    1.46,   # D1/DV PAL Widescreen
    1.33,   # HDV 1080/DVCPRO HD 720
    1.5,    # DVCPRO HD 1080
    2.0,    # Anamorphic 2:1
)


# ---------------------------------------------------------------------------
# Transform / reverse helpers
# ---------------------------------------------------------------------------


def normalize_color(raw: list[int]) -> list[float]:
    """Convert 0-255 integer list to 0.0-1.0 float list."""
    return [c / 255 for c in raw]


def denormalize_color(value: list[float]) -> list[int]:
    """Convert 0.0-1.0 float list to 0-255 integer list."""
    return [round(c * 255) for c in value]


def _reverse_frame_rate(value: float) -> dict[str, int]:
    """Decompose a float frame rate into integer + fractional parts."""
    integer = int(value)
    fractional = round((value - integer) * 65536)
    return {"frame_rate_integer": integer, "frame_rate_fractional": fractional}


def _reverse_pixel_aspect(value: float) -> dict[str, int]:
    """Decompose pixel aspect ratio into width/height ratio."""
    # AE stores pixel_ratio_width / pixel_ratio_height
    # Use a large denominator for precision
    height = 100
    width = round(value * height)
    return {"pixel_ratio_width": width, "pixel_ratio_height": height}


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

    # ---- Chunk-backed descriptors (cdta) ----

    bg_color = ChunkField(
        "_cdta",
        "bg_color",
        transform=normalize_color,
        reverse=denormalize_color,
        validate=validate_sequence(length=3, min=0.0, max=1.0),
        doc="""The background color of the composition. The three array values specify
the red, green, and blue components of the color.""",
    )

    draft3d = ChunkFlagField(
        "_cdta",
        "draft3d",
        doc="""When `True`, Draft 3D mode is enabled for the composition.

Warning:
    Deprecated in After Effects 2024 in favor of the new Draft 3D mode.""",
    )

    frame_blending = ChunkFlagField(
        "_cdta",
        "frame_blending",
        doc="""When `True`, frame blending is enabled for this Composition. Corresponds to
the value of the Frame Blending button in the Composition panel.""",
    )

    hide_shy_layers = ChunkFlagField(
        "_cdta",
        "hide_shy_layers",
        doc="""When `True`, only layers with `shy` set to `False` are shown in the
Timeline panel. When `False`, all layers are visible, including those whose
`shy` value is `True`. Corresponds to the value of the Hide All Shy Layers
button in the Composition panel.""",
    )

    motion_blur = ChunkFlagField(
        "_cdta",
        "motion_blur",
        doc="""When `True`, motion blur is enabled for the composition. Corresponds to
the value of the Motion Blur button in the Composition panel.""",
    )

    preserve_nested_frame_rate = ChunkFlagField(
        "_cdta",
        "preserve_nested_frame_rate",
        doc="""When `True`, the frame rate of nested compositions is preserved in the
current composition. Corresponds to the value of the "Preserve frame rate
when nested or in render queue" option in the Advanced tab of the
Composition Settings dialog box.""",
    )

    preserve_nested_resolution = ChunkFlagField(
        "_cdta",
        "preserve_nested_resolution",
        doc="""When `True`, the resolution of nested compositions is preserved in the
current composition. Corresponds to the value of the "Preserve Resolution
When Nested" option in the Advanced tab of the Composition Settings dialog
box.""",
    )

    width = ChunkField(
        "_cdta",
        "width",
        doc="The width of the item in pixels.",
    )

    height = ChunkField(
        "_cdta",
        "height",
        doc="The height of the item in pixels.",
    )

    shutter_angle = ChunkField(
        "_cdta",
        "shutter_angle",
        doc="""The shutter angle setting for the composition. This corresponds to the
Shutter Angle setting in the Advanced tab of the Composition Settings
dialog box.""",
    )

    shutter_phase = ChunkField(
        "_cdta",
        "shutter_phase",
        doc="""The shutter phase setting for the composition. This corresponds to the
Shutter Phase setting in the Advanced tab of the Composition Settings
dialog box.""",
    )

    resolution_factor = ChunkField(
        "_cdta",
        "resolution_factor",
        transform=list,
        validate=validate_sequence(length=2, min=0.0, max=1.0),
        doc="""The x and y downsample resolution factors for rendering the composition.
The two values in the array specify how many pixels to skip when sampling;
the first number controls horizontal sampling, the second controls vertical
sampling. Full resolution is [1, 1], half resolution is [2, 2], and quarter
resolution is [4, 4]. The default is [1, 1].""",
    )

    motion_blur_adaptive_sample_limit = ChunkField(
        "_cdta",
        "motion_blur_adaptive_sample_limit",
        doc="""The maximum number of motion blur samples of 2D layer motion. This
corresponds to the Adaptive Sample Limit setting in the Advanced tab of
the Composition Settings dialog box.""",
    )

    motion_blur_samples_per_frame = ChunkField(
        "_cdta",
        "motion_blur_samples_per_frame",
        doc="""The minimum number of motion blur samples per frame for Classic 3D layers,
shape layers, and certain effects. This corresponds to the Samples Per
Frame setting in the Advanced tab of the Composition Settings dialog box.""",
    )

    # ---- Chunk-backed descriptors (cdta instances — computed) ----

    frame_rate = ChunkInstanceField(
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
        doc="The frame rate of the item in frames-per-second.",
    )

    duration = ChunkInstanceField(
        "_cdta",
        "duration",
        doc="The duration of the item in seconds. Still footages have a duration of 0.",
    )

    frame_duration = ChunkInstanceField(
        "_cdta",
        "frame_duration",
        transform=int,
        doc="The duration of the item in frames. Still footages have a duration of 0.",
    )

    pixel_aspect = ChunkInstanceField(
        "_cdta",
        "pixel_aspect",
        reverse=_reverse_pixel_aspect,
        validate=validate_one_of(PIXEL_ASPECT_RATIOS),
        invalidates=["pixel_aspect"],
        doc="The pixel aspect ratio of the item (1.0 is square).",
    )

    time_scale = ChunkInstanceField(
        "_cdta",
        "time_scale",
        doc="""The time scale, used as a divisor for keyframe time values. For integer
frame rates (e.g. 24fps) this is a whole number. For non-integer frame
rates (e.g. 29.97fps) this includes a fractional part (e.g. 3.125).

Note:
    Read-only. Derived from the composition's frame rate.""",
    )

    display_start_time = ChunkInstanceField(
        "_cdta",
        "display_start_time",
        doc="""The time set as the beginning of the composition, in seconds. This is the
equivalent of the Start Timecode or Start Frame setting in the Composition
Settings dialog box.""",
    )

    display_start_frame = ChunkInstanceField(
        "_cdta",
        "display_start_frame",
        transform=int,
        doc="The frame value of the beginning of the composition.",
    )

    in_point = ChunkInstanceField(
        "_cdta",
        "in_point",
        doc='The composition "work area" start (seconds).',
    )

    frame_in_point = ChunkInstanceField(
        "_cdta",
        "frame_in_point",
        transform=int,
        doc='The composition "work area" start (frames).',
    )

    out_point = ChunkInstanceField(
        "_cdta",
        "out_point",
        doc='The composition "work area" end (seconds).',
    )

    frame_out_point = ChunkInstanceField(
        "_cdta",
        "frame_out_point",
        transform=int,
        doc='The composition "work area" end (frames).',
    )

    time = ChunkInstanceField(
        "_cdta",
        "time",
        doc="The playhead timestamp, in composition time (seconds).",
    )

    frame_time = ChunkInstanceField(
        "_cdta",
        "frame_time",
        transform=int,
        doc="The playhead timestamp, in composition time (frame).",
    )

    # ---- Chunk-backed descriptor (cdrp) ----

    drop_frame = ChunkFlagField(
        "_cdrp",
        "drop_frame",
        default=False,
        doc="""When `True`, timecode is displayed in drop-frame format. Only applicable
when `frameRate` is 29.97 or 59.94.""",
    )

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

        # Skip AVItem's extra params — they're all descriptor-backed on
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
