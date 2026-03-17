from __future__ import annotations

import typing
from dataclasses import dataclass, field

from aep_parser.enums import TrackMatteType

from .layer import Layer

if typing.TYPE_CHECKING:
    from aep_parser.enums import (
        BlendingMode,
        FrameBlendingType,
        LayerQuality,
        LayerSamplingQuality,
    )

    from ..items.item import Item


@dataclass(eq=False)
class AVLayer(Layer):
    """
    The `AVLayer` object provides an interface to those layers that contain
    [AVItem][] objects (composition layers, footage layers, solid layers, text
    layers and sound layers).

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        layer = comp.file_layers[0]
        print(layer.source)
        ```

    Info:
        `AVLayer` is a subclass of [Layer][] object. All methods and attributes
        of [Layer][] are available when working with `AVLayer`.

    Info:
        `AVLayer` is a base class for [TextLayer][] object, so `AVLayer`
        attributes and methods are available when working with [TextLayer][]
        objects.

    See: https://ae-scripting.docsforadobe.dev/layer/avlayer/
    """

    adjustment_layer: bool
    """When `True`, the layer is an adjustment layer."""

    audio_enabled: bool
    """When `True`, the layer's audio is enabled. This value corresponds to the audio toggle switch in the Timeline panel."""

    blending_mode: BlendingMode
    """The blending mode of the layer."""

    collapse_transformation: bool
    """`True` if collapse transformation is on for this layer."""

    effects_active: bool
    """`True` if the layer's effects are active, as indicated by the <f> icon next to it in the user interface."""

    environment_layer: bool
    """`True` if this is an environment layer in a Ray-traced 3D composition."""

    frame_blending: bool
    """`True` if frame blending is enabled for this layer."""

    frame_blending_type: FrameBlendingType
    """The type of frame blending to perform when frame blending is enabled for the layer."""

    guide_layer: bool
    """`True` if the layer is a guide layer."""

    motion_blur: bool
    """`True` if motion blur is enabled for the layer."""

    preserve_transparency: bool
    """`True` if preserve transparency is enabled for the layer."""

    quality: LayerQuality
    """The layer's draft quality setting."""

    sampling_quality: LayerSamplingQuality
    """The layer's sampling method."""

    three_d_layer: bool
    """`True` if this layer is a 3D layer."""

    three_d_per_char: bool
    """
    `True` if this layer has the Enable Per-character 3D switch set, allowing
    its characters to be animated off the plane of the text layer. Applies
    only to text layers.
    """

    track_matte_type: TrackMatteType
    """Specifies the way the track matte is applied."""

    _source_id: int
    """The ID of the source item for this layer. 0 for a text layer."""

    _matte_layer_id: int
    """
    The ID of the layer used as a track matte for this layer.
    ``0`` when no track matte is applied.
    """

    # Set after parsing - reference to source item (not serialized)
    _source: Item | None = field(default=None, init=False, repr=False)

    # Set after parsing - track matte references (not serialized)
    _track_matte_layer: AVLayer | None = field(default=None, init=False, repr=False)
    _is_track_matte: bool = field(default=False, init=False, repr=False)

    @property
    def source(self) -> Item | None:
        """The source item for this layer. `None` for a text layer."""
        return self._source

    @source.setter
    def source(self, value: Item) -> None:
        self._source = value
        # Also set name from source if layer has no explicit name
        if value is not None and not self.name:
            self.name = value.name

    @property
    def has_video(self) -> bool:
        """`True` if the layer has a video component.

        An `AVLayer` has video when its [source][] has video, or when the
        layer has no external source (text and shape layers always render
        video).
        """
        if self._source is None:
            return True
        return bool(getattr(self._source, "has_video", True))

    @property
    def can_set_collapse_transformation(self) -> bool:
        """`True` if it is possible to set the
        [collapse_transformation][AVLayer.collapse_transformation] value.

        Returns `True` for pre-composition layers and solid layers.
        """
        from ..items.composition import CompItem
        from ..items.footage import FootageItem
        from ..sources.solid import SolidSource

        if self._source is None:
            return False
        if isinstance(self._source, CompItem):
            return True
        if isinstance(self._source, FootageItem):
            ms = self._source.main_source
            if isinstance(ms, SolidSource):
                return True
        return False

    @property
    def can_set_time_remap_enabled(self) -> bool:
        """`True` if it is possible to enable time remapping on this layer.

        Time remapping can be enabled when the layer's source has a
        non-zero duration (i.e. it is not a still image or text layer).
        """
        if self._source is None:
            return False
        duration = getattr(self._source, "duration", 0)
        return duration > 0

    @property
    def time_remap_enabled(self) -> bool:
        """`True` if time remapping is enabled for this layer."""
        try:
            prop = self["ADBE Time Remapping"]
        except KeyError:
            return False
        return bool(prop.animated)

    @property
    def width(self) -> int:
        """The width of the layer in pixels.

        Returns the source item's width if available, otherwise falls back
        to the containing composition's width (matches ExtendScript behavior
        for source-less layers like text and shape layers).
        """
        if self._source is not None:
            return getattr(self._source, "width", 0)
        return self.containing_comp.width

    @property
    def height(self) -> int:
        """The height of the layer in pixels.

        Returns the source item's height if available, otherwise falls back
        to the containing composition's height (matches ExtendScript behavior
        for source-less layers like text and shape layers).
        """
        if self._source is not None:
            return getattr(self._source, "height", 0)
        return self.containing_comp.height

    @property
    def has_track_matte(self) -> bool:
        """
        `True` if this layer has track matte. When true, this layer's `track_matte_type`
        value controls how the matte is applied.
        """
        return self.track_matte_type != TrackMatteType.NO_TRACK_MATTE

    @property
    def is_track_matte(self) -> bool:
        """`True` if this layer is being used as a track matte."""
        return self._is_track_matte

    @property
    def track_matte_layer(self) -> AVLayer | None:
        """The track matte layer for this layer. Returns `None` if this layer has no track matte layer."""
        return self._track_matte_layer

    @property
    def is_name_from_source(self) -> bool:
        """
        True if the layer has no expressly set name, but contains a named source.

        In this case, layer.name has the same value as layer.source.name.
        False if the layer has an expressly set name, or if the layer does not
        have a source.
        """
        return self._source is not None and not (self.is_name_set)
