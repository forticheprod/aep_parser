from __future__ import annotations

import typing
from dataclasses import dataclass, field

from .layer import Layer

if typing.TYPE_CHECKING:
    from ..enums import (
        BlendingMode,
        FrameBlendingType,
        LayerQuality,
        LayerSamplingQuality,
        TrackMatteType,
    )
    from ..items.item import Item


@dataclass
class AVLayer(Layer):
    """
    The `AVLayer` object provides an interface to those layers that contain
    `AVItem` objects (composition layers, footage layers, solid layers, text
    layers and sound layers).

    Info:
        `AVLayer` is a subclass of `Layer` object. All methods and attributes
        of `Layer` are available when working with `AVLayer`.

    Info:
        `AVLayer` is a base class for `TextLayer` object, so `AVLayer`
        attributes and methods are available when working with `TextLayer`
        objects.

    See: https://ae-scripting.docsforadobe.dev/layer/avlayer/
    """

    blending_mode: BlendingMode
    """The blending mode of the layer."""

    frame_blending_type: FrameBlendingType
    """The type of frame blending to perform when frame blending is enabled for the layer."""

    quality: LayerQuality
    """The layer's draft quality setting."""

    sampling_quality: LayerSamplingQuality
    """The layer's sampling method."""

    track_matte_type: TrackMatteType
    """Specifies the way the track matte is applied."""

    adjustment_layer: bool
    """When `True`, the layer is an adjustment layer."""

    audio_enabled: bool
    """When `True`, the layer's audio is enabled. This value corresponds to the audio toggle switch in the Timeline panel."""

    collapse_transformation: bool
    """`True` if collapse transformation is on for this layer."""

    effects_active: bool
    """`True` if the layer's effects are active, as indicated by the <f> icon next to it in the user interface."""

    environment_layer: bool
    """`True` if this is an environment layer in a Ray-traced 3D composition."""

    frame_blending: bool
    """`True` if frame blending is enabled for this layer."""

    guide_layer: bool
    """`True` if the layer is a guide layer."""

    motion_blur: bool
    """`True` if motion blur is enabled for the layer."""

    preserve_transparency: bool
    """`True` if preserve transparency is enabled for the layer."""

    three_d_layer: bool
    """`True` if this layer is a 3D layer."""

    time_remap_enabled: bool
    """`True` if time remapping is enabled for this layer."""

    source_id: int | None  # None for text layers (no source item)
    """The ID of the source item for this layer. `None` for a text layer."""

    # Set after parsing - reference to source item (not serialized)
    _source: Item | None = field(default=None, init=False, repr=False)

    @property
    def source(self) -> Item | None:
        """The source item for this layer."""
        return self._source

    @source.setter
    def source(self, value: Item) -> None:
        self._source = value
        # Also set name from source if layer has no explicit name
        if value is not None and not self.name:
            self.name = value.name

    @property
    def width(self) -> int:
        """The width of the layer in pixels (from source item)."""
        if self._source is not None:
            return getattr(self._source, "width", 0)
        return 0

    @property
    def height(self) -> int:
        """The height of the layer in pixels (from source item)."""
        if self._source is not None:
            return getattr(self._source, "height", 0)
        return 0

    @property
    def is_name_from_source(self) -> bool:
        """
        True if the layer has no expressly set name, but contains a named source.

        In this case, layer.name has the same value as layer.source.name.
        False if the layer has an expressly set name, or if the layer does not
        have a source.
        """
        return self._source is not None and not (self.is_name_set)
