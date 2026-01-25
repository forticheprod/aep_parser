from __future__ import annotations

import typing

from .layer import Layer

if typing.TYPE_CHECKING:
    from ...kaitai.aep import Aep


class AVLayer(Layer):
    def __init__(
        self,
        adjustment_layer: bool,
        audio_enabled: bool,
        blending_mode: int,
        collapse_transformation: bool,
        effects_active: bool,
        environment_layer: bool,
        frame_blending: bool,
        frame_blending_type: Aep.FrameBlendingType,
        guide_layer: bool,
        motion_blur: bool,
        preserve_transparency: bool,
        quality: Aep.LayerQuality,
        sampling_quality: Aep.SamplingQuality,
        source_id: int | None,
        three_d_layer: bool,
        track_matte_type: Aep.TrackMatteType,
        time_remap_enabled: bool | None = None,
        height: int = 0,
        width: int = 0,
        *args,
        **kwargs,
    ):
        """
        An AVLayer object represents an audiovisual layer within a composition.

        Args:
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
        super().__init__(*args, **kwargs)
        self.adjustment_layer = adjustment_layer
        self.audio_enabled = audio_enabled
        self.blending_mode = blending_mode
        self.collapse_transformation = collapse_transformation
        self.effects_active = effects_active
        self.environment_layer = environment_layer
        self.frame_blending = frame_blending
        self.frame_blending_type = frame_blending_type
        self.guide_layer = guide_layer
        self.height = height
        self.motion_blur = motion_blur
        self.preserve_transparency = preserve_transparency
        self.quality = quality
        self.sampling_quality = sampling_quality
        self.source_id = source_id
        self.three_d_layer = three_d_layer
        self.time_remap_enabled = time_remap_enabled
        self.track_matte_type = track_matte_type
        self.width = width
        self.source_is_composition = None
        self.source_is_footage = None

    @property
    def is_name_from_source(self) -> bool:
        """
        True if the layer has no expressly set name, but contains a named source.

        In this case, layer.name has the same value as layer.source.name.
        False if the layer has an expressly set name, or if the layer does not
        have a source.
        """
        return bool(self.source_id) and not (self.is_name_set)
