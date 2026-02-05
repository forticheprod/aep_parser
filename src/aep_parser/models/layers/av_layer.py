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
    An AVLayer object represents an audiovisual layer within a composition.

    Attributes:
        adjustment_layer: When true, the layer is an adjustment layer.
        audio_enabled: When true, the layer's audio is enabled. This value
            corresponds to the audio toggle switch in the Timeline panel.
        blending_mode: The blending mode of the layer. See Blending modes.
        collapse_transformation: True if collapse transformation is on for
            this layer.
        effects_active: True if the layer's effects are active, as
            indicated by the <f> icon next to it in the user interface.
        environment_layer: True if this is an environment layer in a
            Ray-traced 3D composition. Setting this attribute to true
            automatically makes the layer 3D (three_d_layer becomes true).
        frame_blending: True if frame blending is enabled for this layer.
        frame_blending_type: The type of frame blending to perform when frame
            blending is enabled for the layer.
        guide_layer: True if the layer is a guide layer.
        motion_blur: True if motion blur is enabled for the layer.
        preserve_transparency: True if preserve transparency is enabled for
            the layer.
        quality: The layer's draft quality setting.
        sampling_quality: The layer's sampling method.
        source: The source AVItem for this layer. Set after parsing when the
            full project structure is available.
        source_id: The ID of the source item for this layer. None for a text
            layer.
        three_d_layer: True if this layer is a 3D layer.
        time_remap_enabled: True if time remapping is enabled for this layer.
        track_matte_type: Specifies the way the track matte is applied.
    """

    # Required fields - always provided by parser
    blending_mode: BlendingMode
    frame_blending_type: FrameBlendingType
    quality: LayerQuality
    sampling_quality: LayerSamplingQuality
    track_matte_type: TrackMatteType
    adjustment_layer: bool
    audio_enabled: bool
    collapse_transformation: bool
    effects_active: bool
    environment_layer: bool
    frame_blending: bool
    guide_layer: bool
    motion_blur: bool
    preserve_transparency: bool
    three_d_layer: bool
    time_remap_enabled: bool
    source_id: int | None  # None for text layers (no source item)

    # Set after parsing - reference to source item (not serialized)
    _source: Item | None = field(default=None, init=False, repr=False)

    @property
    def source(self) -> Item | None:
        """The source item for this layer."""
        return self._source

    @source.setter
    def source(self, value: Item | None) -> None:
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
