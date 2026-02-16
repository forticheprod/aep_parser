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
    FastPreviewType,
    FieldSeparationType,
    FootageTimecodeDisplayStartType,
    FrameBlendingType,
    ViewerType,
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


def map_frame_blending_type(
    frame_blending_type_raw: int, frame_blending_enabled: bool
) -> FrameBlendingType:
    """Map binary frame_blending_type value to ExtendScript FrameBlendingType enum.

    In the binary format, frame_blending_type is stored as a 1-bit value:
    - 0 = FRAME_MIX (default when frame blending is enabled)
    - 1 = PIXEL_MOTION

    However, when frame_blending is disabled (False), the returned type
    should always be NO_FRAME_BLEND (4012), regardless of the bit value.

    Args:
        frame_blending_type_raw: The raw 1-bit value from the binary.
        frame_blending_enabled: Whether frame blending is enabled on the layer.
    """
    if not frame_blending_enabled:
        return FrameBlendingType.NO_FRAME_BLEND

    mapping = {
        0: FrameBlendingType.FRAME_MIX,
        1: FrameBlendingType.PIXEL_MOTION,
    }
    return mapping.get(frame_blending_type_raw, FrameBlendingType.FRAME_MIX)


def map_auto_orient_type(
    auto_orient_along_path: bool,
    camera_or_poi_auto_orient: bool,
    three_d_layer: bool,
    characters_toward_camera: int,
) -> AutoOrientType:
    """Derive the AutoOrientType from binary ldta data bits.

    The auto-orient type is stored across multiple non-contiguous bits in
    the binary format rather than as a single value:

    - ALONG_PATH: auto_orient_along_path bit is set
    - CAMERA_OR_POINT_OF_INTEREST: camera_or_poi_auto_orient AND three_d_layer are set
    - CHARACTERS_TOWARD_CAMERA: characters_toward_camera bits equal 3 (0b11)
    - NO_AUTO_ORIENT: none of the above conditions are met

    Args:
        auto_orient_along_path: The auto_orient_along_path bit from ldta.
        camera_or_poi_auto_orient: The camera_or_poi_auto_orient bit from ldta.
        three_d_layer: Whether the layer is a 3D layer.
        characters_toward_camera: The 2-bit characters_toward_camera value from ldta.
    """
    if auto_orient_along_path:
        return AutoOrientType.ALONG_PATH
    elif camera_or_poi_auto_orient and three_d_layer:
        return AutoOrientType.CAMERA_OR_POINT_OF_INTEREST
    elif characters_toward_camera == 3:
        return AutoOrientType.CHARACTERS_TOWARD_CAMERA
    else:
        return AutoOrientType.NO_AUTO_ORIENT


def map_fast_preview_type(
    adaptive: bool,
    wireframe: bool,
) -> FastPreviewType:
    """Derive the FastPreviewType from individual fips bit flags.

    Args:
        adaptive: Whether the adaptive resolution bit is set.
        wireframe: Whether the wireframe bit is set.
    """
    if wireframe:
        return FastPreviewType.FP_WIREFRAME
    if adaptive:
        return FastPreviewType.FP_ADAPTIVE_RESOLUTION
    return FastPreviewType.FP_OFF


def map_viewer_type_from_string(label: str) -> ViewerType | None:
    """Map a viewer panel type label string to a ViewerType enum.

    The `fitt` chunk stores the inner tab type as an ASCII string
    (e.g. `"AE Composition"`). This function converts that string
    to the corresponding [ViewerType][aep_parser.models.enums.ViewerType] value.

    Args:
        label: The panel type label from the `fitt` chunk.

    Returns:
        The matching [ViewerType][aep_parser.models.enums.ViewerType], or `None` if the label is
        not recognised.
    """
    mapping = {
        "AE Composition": ViewerType.VIEWER_COMPOSITION,
        "AE Layer": ViewerType.VIEWER_LAYER,
        "AE Footage": ViewerType.VIEWER_FOOTAGE,
    }
    return mapping.get(label, ViewerType.VIEWER_COMPOSITION)
