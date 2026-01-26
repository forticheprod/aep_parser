from __future__ import annotations

import typing
from dataclasses import dataclass, field

from .layer import Layer

if typing.TYPE_CHECKING:
    from ...kaitai.aep import Aep


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
        frame_blending_type: The type of frame blending to perform when
            frame blending is enabled for the layer.
        guide_layer: True if the layer is a guide layer.
        height: The height of the layer in pixels.
        motion_blur: True if motion blur is enabled for the layer.
        preserve_transparency: True if preserve transparency is enabled for
            the layer.
        quality: The layer's draft quality setting.
        sampling_quality: The layer's sampling method.
        source_id: The ID of the source item for this layer. None for a
            text layer.
        three_d_layer: True if this layer is a 3D layer.
        time_remap_enabled: True if time remapping is enabled for this
            layer.
        track_matte_type: Specifies the way the track matte is applied.
        width: The width of the layer in pixels.
    """

    adjustment_layer: bool = False
    audio_enabled: bool = False
    blending_mode: int = 0
    collapse_transformation: bool = False
    effects_active: bool = False
    environment_layer: bool = False
    frame_blending: bool = False
    frame_blending_type: Aep.FrameBlendingType | None = None
    guide_layer: bool = False
    height: int = 0
    motion_blur: bool = False
    preserve_transparency: bool = False
    quality: Aep.LayerQuality | None = None
    sampling_quality: Aep.SamplingQuality | None = None
    source_id: int | None = None
    three_d_layer: bool = False
    time_remap_enabled: bool | None = None
    track_matte_type: Aep.TrackMatteType | None = None
    width: int = 0
    source_is_composition: bool | None = field(default=None, init=False)
    source_is_footage: bool | None = field(default=None, init=False)

    @property
    def is_name_from_source(self) -> bool:
        """
        True if the layer has no expressly set name, but contains a named source.

        In this case, layer.name has the same value as layer.source.name.
        False if the layer has an expressly set name, or if the layer does not
        have a source.
        """
        return bool(self.source_id) and not (self.is_name_set)
