"""Mappings from binary values to ExtendScript enum values.

Binary values in AEP files often differ from ExtendScript API values.
This module provides the translation layer between Kaitai-parsed raw values
and the Python enum types that match ExtendScript.
"""

from __future__ import annotations

from ..models.enums import (
    AlphaMode,
    AutoOrientType,
    BitsPerChannel,
    BlendingMode,
    FieldSeparationType,
    FootageTimecodeDisplayStartType,
    FrameBlendingType,
    FramesCountType,
    KeyframeInterpolationType,
    LayerQuality,
    LayerSamplingQuality,
    LightType,
    TimeDisplayType,
    TrackMatteType,
)


def map_alpha_mode(alpha_mode_raw: int, has_alpha: bool) -> AlphaMode:
    """Map binary alpha_mode value to ExtendScript AlphaMode enum.

    Args:
        alpha_mode_raw: Raw value from sspc chunk.
        has_alpha: Whether the footage has an alpha channel.
    """
    if not has_alpha:
        return AlphaMode.IGNORE

    mapping = {
        0: AlphaMode.STRAIGHT,
        1: AlphaMode.PREMULTIPLIED,
        2: AlphaMode.IGNORE,
        3: AlphaMode.IGNORE,  # no_alpha treated as ignore
    }
    return mapping.get(alpha_mode_raw, AlphaMode.STRAIGHT)


def map_bits_per_channel(bits_per_channel_raw: int) -> BitsPerChannel:
    """Map binary bits_per_channel value to ExtendScript BitsPerChannel enum."""
    mapping = {
        0: BitsPerChannel.EIGHT,
        1: BitsPerChannel.SIXTEEN,
        2: BitsPerChannel.THIRTY_TWO,
    }
    return mapping.get(bits_per_channel_raw, BitsPerChannel.EIGHT)


def map_blending_mode(blending_mode_raw: int) -> BlendingMode:
    """Map binary blending_mode value to ExtendScript BlendingMode enum."""
    mapping = {
        2: BlendingMode.NORMAL,
        3: BlendingMode.DISSOLVE,
        4: BlendingMode.ADD,
        5: BlendingMode.MULTIPLY,
        6: BlendingMode.SCREEN,
        7: BlendingMode.OVERLAY,
        8: BlendingMode.SOFT_LIGHT,
        9: BlendingMode.HARD_LIGHT,
        10: BlendingMode.DARKEN,
        11: BlendingMode.LIGHTEN,
        12: BlendingMode.CLASSIC_DIFFERENCE,
        13: BlendingMode.HUE,
        14: BlendingMode.SATURATION,
        15: BlendingMode.COLOR,
        16: BlendingMode.LUMINOSITY,
        17: BlendingMode.STENCIL_ALPHA,
        18: BlendingMode.STENCIL_LUMA,
        19: BlendingMode.SILHOUETE_ALPHA,
        20: BlendingMode.SILHOUETTE_LUMA,
        21: BlendingMode.LUMINESCENT_PREMUL,
        22: BlendingMode.ALPHA_ADD,
        23: BlendingMode.CLASSIC_COLOR_DODGE,
        24: BlendingMode.CLASSIC_COLOR_BURN,
        25: BlendingMode.EXCLUSION,
        26: BlendingMode.DIFFERENCE,
        27: BlendingMode.COLOR_DODGE,
        28: BlendingMode.COLOR_BURN,
        29: BlendingMode.LINEAR_DODGE,
        30: BlendingMode.LINEAR_BURN,
        31: BlendingMode.LINEAR_LIGHT,
        32: BlendingMode.VIVID_LIGHT,
        33: BlendingMode.PIN_LIGHT,
        34: BlendingMode.HARD_MIX,
        35: BlendingMode.LIGHTER_COLOR,
        36: BlendingMode.DARKER_COLOR,
        37: BlendingMode.SUBTRACT,
        38: BlendingMode.DIVIDE,
    }
    return mapping.get(blending_mode_raw, BlendingMode.NORMAL)


def map_field_separation_type(
    field_separation_type_raw: int, field_order_raw: int
) -> FieldSeparationType:
    """Map binary field separation values to ExtendScript FieldSeparationType enum.

    Args:
        field_separation_type_raw: 0=off, 1=enabled.
        field_order_raw: 0=upper_field_first, 1=lower_field_first.
    """
    if field_separation_type_raw == 0:
        return FieldSeparationType.OFF
    if field_order_raw == 0:
        return FieldSeparationType.UPPER_FIELD_FIRST
    return FieldSeparationType.LOWER_FIELD_FIRST


def map_footage_timecode_display_start_type(
    ftcs_raw: int,
) -> FootageTimecodeDisplayStartType:
    """Map binary value to ExtendScript FootageTimecodeDisplayStartType enum."""
    mapping = {
        0: FootageTimecodeDisplayStartType.FTCS_START_0,
        1: FootageTimecodeDisplayStartType.FTCS_USE_SOURCE_MEDIA,
    }
    return mapping.get(ftcs_raw, FootageTimecodeDisplayStartType.FTCS_START_0)


def map_frame_blending_type(frame_blending_type_raw: int) -> FrameBlendingType:
    """Map binary frame_blending_type value to ExtendScript FrameBlendingType enum."""
    mapping = {
        0: FrameBlendingType.FRAME_MIX,
        1: FrameBlendingType.PIXEL_MOTION,
        2: FrameBlendingType.NO_FRAME_BLEND,
    }
    return mapping.get(frame_blending_type_raw, FrameBlendingType.NO_FRAME_BLEND)


def map_frames_count_type(frames_count_type_raw: int) -> FramesCountType:
    """Map binary value to ExtendScript FramesCountType enum."""
    mapping = {
        0: FramesCountType.FC_START_0,
        1: FramesCountType.FC_START_1,
        2: FramesCountType.FC_TIMECODE_CONVERSION,
    }
    return mapping.get(frames_count_type_raw, FramesCountType.FC_START_0)


def map_keyframe_interpolation_type(
    keyframe_interpolation_type_raw: int,
) -> KeyframeInterpolationType:
    """Map binary keyframe_interpolation_type value to ExtendScript enum."""
    mapping = {
        1: KeyframeInterpolationType.LINEAR,
        2: KeyframeInterpolationType.BEZIER,
        3: KeyframeInterpolationType.HOLD,
    }
    return mapping.get(keyframe_interpolation_type_raw, KeyframeInterpolationType.LINEAR)


def map_layer_quality(layer_quality_raw: int) -> LayerQuality:
    """Map binary layer_quality value to ExtendScript LayerQuality enum."""
    mapping = {
        0: LayerQuality.WIREFRAME,
        1: LayerQuality.DRAFT,
        2: LayerQuality.BEST,
    }
    return mapping.get(layer_quality_raw, LayerQuality.BEST)


def map_layer_sampling_quality(sampling_quality_raw: int) -> LayerSamplingQuality:
    """Map binary sampling_quality value to ExtendScript LayerSamplingQuality enum."""
    mapping = {
        0: LayerSamplingQuality.BILINEAR,
        1: LayerSamplingQuality.BICUBIC,
    }
    return mapping.get(sampling_quality_raw, LayerSamplingQuality.BILINEAR)


def map_time_display_type(time_display_type_raw: int) -> TimeDisplayType:
    """Map binary value to ExtendScript TimeDisplayType enum."""
    mapping = {
        0: TimeDisplayType.TIMECODE,
        1: TimeDisplayType.FRAMES,
    }
    return mapping.get(time_display_type_raw, TimeDisplayType.TIMECODE)


def map_track_matte_type(track_matte_type_raw: int) -> TrackMatteType:
    """Map binary track_matte_type value to ExtendScript TrackMatteType enum."""
    mapping = {
        0: TrackMatteType.NO_TRACK_MATTE,
        1: TrackMatteType.ALPHA,
        2: TrackMatteType.ALPHA_INVERTED,
        3: TrackMatteType.LUMA,
        4: TrackMatteType.LUMA_INVERTED,
    }
    return mapping.get(track_matte_type_raw, TrackMatteType.NO_TRACK_MATTE)


def map_auto_orient_type(auto_orient_type_raw: int) -> AutoOrientType:
    """Map binary auto_orient_type value to ExtendScript AutoOrientType enum."""
    mapping = {
        0: AutoOrientType.NO_AUTO_ORIENT,
        1: AutoOrientType.ALONG_PATH,
        2: AutoOrientType.CAMERA_OR_POINT_OF_INTEREST,
        3: AutoOrientType.CHARACTERS_TOWARD_CAMERA,
    }
    return mapping.get(auto_orient_type_raw, AutoOrientType.NO_AUTO_ORIENT)


def map_light_type(light_type_raw: int) -> LightType:
    """Map binary light_type value to ExtendScript LightType enum."""
    mapping = {
        0: LightType.PARALLEL,
        1: LightType.SPOT,
        2: LightType.POINT,
        3: LightType.AMBIENT,
    }
    return mapping.get(light_type_raw, LightType.PARALLEL)
