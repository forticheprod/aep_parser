from __future__ import annotations

import typing

from aep_parser.enums import (
    BlendingMode,
    FrameBlendingType,
    LayerQuality,
    LayerSamplingQuality,
    TrackMatteType,
)

from ...enums.mappings import map_frame_blending_type
from ...kaitai.descriptors import ChunkField
from .layer import Layer

if typing.TYPE_CHECKING:
    from aep_parser.enums import AutoOrientType

    from ...kaitai.aep import Aep  # type: ignore[attr-defined]
    from ..items.composition import CompItem
    from ..items.item import Item
    from ..properties.property import Property
    from ..properties.property_group import PropertyGroup


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

    # ---- Chunk-backed descriptors (ldta) ----

    adjustment_layer = ChunkField[bool]("_ldta", "adjustment_layer", reverse=int)
    """When `True`, the layer is an adjustment layer. Read / Write."""

    audio_enabled = ChunkField[bool]("_ldta", "audio_enabled", reverse=int)
    """When `True`, the layer's audio is enabled. This value corresponds
    to the audio toggle switch in the Timeline panel. Read / Write."""

    blending_mode = ChunkField[BlendingMode](
        "_ldta",
        "blending_mode",
        transform=BlendingMode.from_binary,
        reverse=BlendingMode.to_binary,
    )
    """The blending mode of the layer. Read / Write."""

    collapse_transformation = ChunkField[bool]("_ldta", "collapse_transformation", reverse=int)
    """`True` if collapse transformation is on for this layer.
    Read / Write."""

    effects_active = ChunkField[bool]("_ldta", "effects_active", reverse=int)
    """`True` if the layer's effects are active, as indicated by the
    <f> icon next to it in the user interface. Read / Write."""

    environment_layer = ChunkField[bool]("_ldta", "environment_layer", reverse=int)
    """`True` if this is an environment layer in a Ray-traced 3D
    composition. Read / Write."""

    frame_blending = ChunkField[bool]("_ldta", "frame_blending")
    """`True` if frame blending is enabled for this layer. Read-only."""

    guide_layer = ChunkField[bool]("_ldta", "guide_layer", reverse=int)
    """`True` if the layer is a guide layer. Read / Write."""

    motion_blur = ChunkField[bool]("_ldta", "motion_blur", reverse=int)
    """`True` if motion blur is enabled for the layer. Read / Write."""

    preserve_transparency = ChunkField[bool](
        "_ldta", "preserve_transparency", transform=bool, reverse=int
    )
    """`True` if preserve transparency is enabled for the layer.
    Read / Write."""

    quality = ChunkField[LayerQuality](
        "_ldta",
        "quality",
        transform=LayerQuality.from_binary,
        reverse=LayerQuality.to_binary,
    )
    """The layer's draft quality setting. Read / Write."""

    sampling_quality = ChunkField[LayerSamplingQuality](
        "_ldta",
        "sampling_quality",
        transform=LayerSamplingQuality.from_binary,
        reverse=LayerSamplingQuality.to_binary,
    )
    """The layer's sampling method. Read / Write."""

    three_d_layer = ChunkField[bool]("_ldta", "three_d_layer", reverse=int)
    """`True` if this layer is a 3D layer. Read / Write."""

    three_d_per_char = ChunkField[bool]("_ldta", "three_d_per_char", reverse=int)
    """`True` if this layer has the Enable Per-character 3D switch set,
    allowing its characters to be animated off the plane of the text
    layer. Applies only to text layers. Read / Write."""

    track_matte_type = ChunkField[TrackMatteType](
        "_ldta",
        "track_matte_type",
        transform=TrackMatteType.from_binary,
        reverse=TrackMatteType.to_binary,
    )
    """Specifies the way the track matte is applied. Read / Write."""

    _source_id = ChunkField[int]("_ldta", "source_id", reverse=int)
    """The ID of the source item for this layer. 0 for a text layer."""

    # ---- Regular attributes set in __init__ ----

    _matte_layer_id: int
    """
    The ID of the layer used as a track matte for this layer.
    `0` when no track matte is applied.
    """

    def __init__(
        self,
        *,
        _ldta: Aep.LdtaBody,
        name: str,
        comment: str,
        containing_comp: CompItem,
        properties: list[Property | PropertyGroup],
        auto_orient: AutoOrientType,
        layer_type: str,
        match_name: str,
        _matte_layer_id: int,
    ) -> None:
        super().__init__(
            _ldta=_ldta,
            name=name,
            comment=comment,
            containing_comp=containing_comp,
            properties=properties,
            auto_orient=auto_orient,
            layer_type=layer_type,
            match_name=match_name,
        )
        self._matte_layer_id = _matte_layer_id
        self._source: Item | None = None
        self._track_matte_layer: AVLayer | None = None
        self._is_track_matte: bool = False

    @property
    def frame_blending_type(self) -> FrameBlendingType:
        """The type of frame blending for the layer."""
        return map_frame_blending_type(
            self._ldta.frame_blending_type,
            self._ldta.frame_blending,
        )

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
