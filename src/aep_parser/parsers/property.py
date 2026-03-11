from __future__ import annotations

import io
import logging
import math
import struct
from contextlib import suppress
from typing import Any

from ..cos import CosParser
from ..enums import (
    KeyframeInterpolationType,
    Label,
    PropertyControlType,
    PropertyType,
    PropertyValueType,
)
from ..kaitai import Aep
from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)
from ..models.properties.keyframe import Keyframe
from ..models.properties.keyframe_ease import KeyframeEase
from ..models.properties.mask_property_group import MaskPropertyGroup
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from ..models.properties.shape_value import ShapeValue
from .match_names import MATCH_NAME_TO_NICE_NAME
from .text import parse_btdk_cos
from .utils import (
    get_chunks_by_match_name,
    parse_ldat_items,
)

logger = logging.getLogger(__name__)

# Match names whose binary values are stored as 0–1 fractions but
# ExtendScript reports as 0–100 percentages.  Values (static + keyframe)
# are multiplied by 100 after extraction from the binary.
_PERCENT_MATCH_NAMES: set[str] = {
    "ADBE Opacity",
    "ADBE Scale",
    "ADBE Mask Opacity",
}

# Map of property match names to their units text in After Effects.
# Extracted from ExtendScript JSON exports across all sample files.
_UNITS_TEXT_MAP: dict[str, str] = {
    "ADBE Ambient Coefficient": "percent",
    "ADBE Anchor Point": "pixels",
    "ADBE Audio Levels": "dB",
    "ADBE Camera Aperture": "pixels",
    "ADBE Camera Blur Level": "percent",
    "ADBE Camera Focus Distance": "pixels",
    "ADBE Camera Zoom": "pixels",
    "ADBE Cartoonify-0012": "percent",
    "ADBE Diffuse Coefficient": "percent",
    "ADBE Drop Shadow-0002": "percent",
    "ADBE Drop Shadow-0003": "degrees",
    "ADBE Effect Mask Opacity": "percent",
    "ADBE Emboss-0001": "degrees",
    "ADBE Emboss-0004": "percent",
    "ADBE Fill-0005": "percent",
    "ADBE FreePin3 PosPin Position": "pixels",
    "ADBE FreePin3 PosPin Rotation": "degrees",
    "ADBE FreePin3 PosPin Scale": "percent",
    "ADBE FreePin3 PosPin Vtx Offset": "pixels",
    "ADBE Fresnel Coefficient": "percent",
    "ADBE Geometry2-0001": "pixels",
    "ADBE Geometry2-0002": "pixels",
    "ADBE Geometry2-0006": "degrees",
    "ADBE Geometry2-0007": "degrees",
    "ADBE Glo2-0002": "percent",
    "ADBE Glo2-0009": "percent",
    "ADBE Glo2-0010": "degrees",
    "ADBE Glo2-0011": "percent",
    "ADBE Global Altitude2": "degrees",
    "ADBE Global Angle2": "degrees",
    "ADBE Glossiness Coefficient": "percent",
    "ADBE HUE SATURATION-0004": "degrees",
    "ADBE HUE SATURATION-0005": "pixels",
    "ADBE HUE SATURATION-0006": "pixels",
    "ADBE HUE SATURATION-0008": "degrees",
    "ADBE HUE SATURATION-0010": "pixels",
    "ADBE Hole Bevel Depth": "percent",
    "ADBE Invert-0002": "percent",
    "ADBE Iris Rotation": "degrees",
    "ADBE Iris Roundness": "percent",
    "ADBE Layer Fill Opacity2": "percent",
    "ADBE Lens Flare-0001": "pixels",
    "ADBE Lens Flare-0002": "percent",
    "ADBE Lens Flare-0003": "percent",
    "ADBE Light Backgd Blur": "percent",
    "ADBE Light Backgd Opacity": "percent",
    "ADBE Light Cone Angle": "degrees",
    "ADBE Light Cone Feather 2": "percent",
    "ADBE Light Intensity": "percent",
    "ADBE Light Shadow Darkness": "percent",
    "ADBE Light Shadow Diffusion": "pixels",
    "ADBE Light Transmission": "percent",
    "ADBE Mask Feather": "pixels",
    "ADBE Mask Offset": "pixels",
    "ADBE Mask Opacity": "percent",
    "ADBE Metal Coefficient": "percent",
    "ADBE Noise Alpha2-0002": "percent",
    "ADBE Noise Alpha2-0005": "degrees",
    "ADBE Opacity": "percent",
    "ADBE Orientation": "degrees",
    "ADBE Paint Anchor Point": "pixels",
    "ADBE Paint Angle": "degrees",
    "ADBE Paint Begin": "percent",
    "ADBE Paint Clone Position": "pixels",
    "ADBE Paint End": "percent",
    "ADBE Paint Flow": "percent",
    "ADBE Paint Hardness": "percent",
    "ADBE Paint Opacity": "percent",
    "ADBE Paint Position": "pixels",
    "ADBE Paint Rotation": "degrees",
    "ADBE Paint Roundness": "percent",
    "ADBE Paint Scale": "percent",
    "ADBE Paint Tip Spacing": "percent",
    "ADBE Plane Curvature": "percent",
    "ADBE Position": "pixels",
    "ADBE Position_0": "pixels",
    "ADBE Position_1": "pixels",
    "ADBE Position_2": "pixels",
    "ADBE Reflection Coefficient": "percent",
    "ADBE Rotate X": "degrees",
    "ADBE Rotate Y": "degrees",
    "ADBE Rotate Z": "degrees",
    "ADBE Roughen Edges-0006": "pixels",
    "ADBE Roughen Edges-0007": "pixels",
    "ADBE Roughen Edges-0009": "degrees",
    "ADBE Scale": "percent",
    "ADBE Shininess Coefficient": "percent",
    "ADBE Simple Choker-0002": "pixels",
    "ADBE Specular Coefficient": "percent",
    "ADBE Text Anchor Point Align": "percent",
    "ADBE Time Remapping": "seconds",
    "ADBE Tint-0003": "percent",
    "ADBE Transp Rolloff": "percent",
    "ADBE Transparency Coefficient": "percent",
    "ADBE Turbulent Displace-0004": "pixels",
    "ADBE Turbulent Displace-0005": "percent",
    "ADBE Turbulent Displace-0006": "degrees",
    "ADBE Vec3D Back Ambient": "percent",
    "ADBE Vec3D Back Diffuse": "percent",
    "ADBE Vec3D Back Fresnel": "percent",
    "ADBE Vec3D Back Gloss": "percent",
    "ADBE Vec3D Back Metal": "percent",
    "ADBE Vec3D Back Reflection": "percent",
    "ADBE Vec3D Back Shininess": "percent",
    "ADBE Vec3D Back Specular": "percent",
    "ADBE Vec3D Back XparRoll": "percent",
    "ADBE Vec3D Back Xparency": "percent",
    "ADBE Vec3D Bevel Ambient": "percent",
    "ADBE Vec3D Bevel Diffuse": "percent",
    "ADBE Vec3D Bevel Fresnel": "percent",
    "ADBE Vec3D Bevel Gloss": "percent",
    "ADBE Vec3D Bevel Metal": "percent",
    "ADBE Vec3D Bevel Reflection": "percent",
    "ADBE Vec3D Bevel Shininess": "percent",
    "ADBE Vec3D Bevel Specular": "percent",
    "ADBE Vec3D Bevel XparRoll": "percent",
    "ADBE Vec3D Bevel Xparency": "percent",
    "ADBE Vec3D Front Ambient": "percent",
    "ADBE Vec3D Front Diffuse": "percent",
    "ADBE Vec3D Front Fresnel": "percent",
    "ADBE Vec3D Front Gloss": "percent",
    "ADBE Vec3D Front Metal": "percent",
    "ADBE Vec3D Front Reflection": "percent",
    "ADBE Vec3D Front Shininess": "percent",
    "ADBE Vec3D Front Specular": "percent",
    "ADBE Vec3D Front XparRoll": "percent",
    "ADBE Vec3D Front Xparency": "percent",
    "ADBE Vec3D Side Ambient": "percent",
    "ADBE Vec3D Side Diffuse": "percent",
    "ADBE Vec3D Side Fresnel": "percent",
    "ADBE Vec3D Side Gloss": "percent",
    "ADBE Vec3D Side Metal": "percent",
    "ADBE Vec3D Side Reflection": "percent",
    "ADBE Vec3D Side Shininess": "percent",
    "ADBE Vec3D Side Specular": "percent",
    "ADBE Vec3D Side XparRoll": "percent",
    "ADBE Vec3D Side Xparency": "percent",
    "ADBE Vector Anchor": "pixels",
    "ADBE Vector Ellipse Position": "pixels",
    "ADBE Vector Fill Opacity": "percent",
    "ADBE Vector Group Opacity": "percent",
    "ADBE Vector Position": "pixels",
    "ADBE Vector Rect Position": "pixels",
    "ADBE Vector Rotation": "degrees",
    "ADBE Vector Scale": "percent",
    "ADBE Vector Skew Axis": "degrees",
    "ADBE Vector Star Inner Roundess": "percent",
    "ADBE Vector Star Outer Roundess": "percent",
    "ADBE Vector Star Position": "pixels",
    "ADBE Vector Star Rotation": "degrees",
    "ADBE Vector Stroke Opacity": "percent",
    "ADBE Vector Taper End Ease": "percent",
    "ADBE Vector Taper End Length": "percent",
    "ADBE Vector Taper End Width": "percent",
    "ADBE Vector Taper Start Ease": "percent",
    "ADBE Vector Taper Start Length": "percent",
    "ADBE Vector Taper Start Width": "percent",
    "ADBE Vector Taper Wave Amount": "percent",
    "ADBE Vector Taper Wave Phase": "degrees",
    "CC RepeTile-0006": "percent",
    "CC Sphere-0002": "degrees",
    "CC Sphere-0003": "degrees",
    "CC Sphere-0004": "degrees",
    "CC Sphere-0007": "pixels",
    "CC Sphere-0012": "pixels",
    "CC Sphere-0013": "degrees",
    "CC Threshold RGB-0007": "percent",
    "CC Toner-0004": "percent",
    "CC Vector Blur-0002": "pixels",
    "CC Vector Blur-0003": "degrees",
    "DRFL Depth of Field-0015": "degrees",
    "DRFL Depth of Field-0031": "degrees",
    "DRFL Depth of Field-0038": "degrees",
    "DRFL Depth of Field-0045": "degrees",
    "DRFL Depth of Field-0056": "pixels",
    "Keylight 906-0038": "pixels",
    "Keylight 906-0039": "pixels",
    "Keylight 906-0057": "pixels",
    "Keylight 906-0058": "pixels",
    "S_Blur-0054": "percent",
    "S_Blur-0527": "percent",
    "S_Blur-0528": "percent",
    "S_BlurDirectional-0051": "percent",
    "S_BlurDirectional-0052": "percent",
    "S_BlurDirectional-0057": "percent",
    "S_BlurDirectional-0058": "percent",
    "S_BlurDirectional-0059": "percent",
    "S_BlurDirectional-0527": "percent",
    "S_BlurDirectional-0528": "percent",
    "S_BlurDirectional-0543": "pixels",
    "S_EdgeAwareBlur-0527": "percent",
    "S_EdgeAwareBlur-0528": "percent",
    "S_EmbossGlass-0050": "pixels",
    "S_EmbossGlass-0053": "percent",
    "S_EmbossGlass-0059": "percent",
    "S_EmbossGlass-0061": "percent",
    "S_EmbossGlass-0062": "percent",
    "S_EmbossGlass-0063": "percent",
    "S_EmbossGlass-0527": "percent",
    "S_EmbossGlass-0528": "percent",
    "S_Flicker-0056": "percent",
    "S_Flicker-0057": "percent",
    "S_Flicker-0058": "percent",
    "S_Gradient-0050": "pixels",
    "S_Gradient-0051": "pixels",
    "S_Gradient-0527": "percent",
    "S_Gradient-0528": "percent",
    "S_HalfTone-0052": "percent",
    "S_HalfTone-0055": "percent",
    "S_HalfTone-0059": "percent",
    "S_HalfTone-0060": "percent",
    "S_HalfTone-0527": "percent",
    "S_HalfTone-0528": "percent",
    "S_HalfToneColor-0052": "percent",
    "S_HalfToneColor-0055": "percent",
    "S_HalfToneColor-0057": "pixels",
    "S_HalfToneColor-0058": "percent",
    "S_HalfToneColor-0059": "percent",
    "S_HalfToneColor-0060": "percent",
    "S_HalfToneColor-0061": "percent",
    "S_HalfToneColor-0062": "percent",
    "S_HalfToneColor-0063": "percent",
    "S_HalfToneColor-0064": "percent",
    "S_HalfToneColor-0065": "percent",
    "S_HalfToneColor-0527": "percent",
    "S_HalfToneColor-0528": "percent",
    "S_Invert-0061": "pixels",
    "S_Invert-0527": "percent",
    "S_Invert-0528": "percent",
    "S_RackDefocus-0056": "percent",
    "S_RackDefocus-0104": "percent",
    "S_RackDefocus-0105": "percent",
    "S_RackDefocus-0112": "percent",
    "S_RackDefocus-0113": "percent",
    "S_RackDefocus-0114": "percent",
    "S_RackDefocus-0527": "percent",
    "S_RackDefocus-0528": "percent",
    "S_Shake-0052": "percent",
    "S_Shake-0063": "percent",
    "S_Shake-0068": "percent",
    "S_Shake-0073": "percent",
    "S_Shake-0078": "percent",
    "S_Shake-0103": "percent",
    "S_Shake-0104": "percent",
    "S_Shake-0105": "percent",
    "S_Shake-0527": "percent",
    "S_Shake-0528": "percent",
    "S_Sharpen-0050": "percent",
    "S_Sharpen-0102": "percent",
    "S_Sharpen-0103": "percent",
    "S_Sharpen-0104": "percent",
    "S_Sharpen-0527": "percent",
    "S_Sharpen-0528": "percent",
    "S_Threshold-0056": "percent",
    "S_Threshold-0527": "percent",
    "S_Threshold-0528": "percent",
    "S_WarpChroma-0050": "percent",
    "S_WarpChroma-0051": "pixels",
    "S_WarpChroma-0053": "percent",
    "S_WarpChroma-0054": "percent",
    "S_WarpChroma-0055": "percent",
    "S_WarpChroma-0057": "percent",
    "S_WarpChroma-0058": "percent",
    "S_WarpChroma-0059": "percent",
    "S_WarpChroma-0527": "percent",
    "S_WarpChroma-0528": "percent",
    "S_WarpTransform-0050": "percent",
    "S_WarpTransform-0051": "percent",
    "S_WarpTransform-0052": "pixels",
    "S_WarpTransform-0054": "percent",
    "S_WarpTransform-0055": "percent",
    "S_WarpTransform-0056": "percent",
    "S_WarpTransform-0100": "percent",
    "S_WarpTransform-0101": "percent",
    "S_WarpTransform-0527": "percent",
    "S_WarpTransform-0528": "percent",
    "bevelEmboss/highlightOpacity": "percent",
    "bevelEmboss/localLightingAltitude": "degrees",
    "bevelEmboss/localLightingAngle": "degrees",
    "bevelEmboss/shadowOpacity": "percent",
    "bevelEmboss/strengthRatio": "percent",
    "chromeFX/localLightingAngle": "degrees",
    "chromeFX/opacity": "percent",
    "dropShadow/chokeMatte": "percent",
    "dropShadow/localLightingAngle": "degrees",
    "dropShadow/noise": "percent",
    "dropShadow/opacity": "percent",
    "frameFX/opacity": "percent",
    "gradientFill/angle": "degrees",
    "gradientFill/gradientSmoothness": "percent",
    "gradientFill/offset": "pixels",
    "gradientFill/opacity": "percent",
    "gradientFill/scale": "percent",
    "innerGlow/chokeMatte": "percent",
    "innerGlow/gradientSmoothness": "percent",
    "innerGlow/inputRange": "percent",
    "innerGlow/noise": "percent",
    "innerGlow/opacity": "percent",
    "innerGlow/shadingNoise": "percent",
    "innerShadow/chokeMatte": "percent",
    "innerShadow/localLightingAngle": "degrees",
    "innerShadow/noise": "percent",
    "innerShadow/opacity": "percent",
    "outerGlow/chokeMatte": "percent",
    "outerGlow/gradientSmoothness": "percent",
    "outerGlow/inputRange": "percent",
    "outerGlow/noise": "percent",
    "outerGlow/opacity": "percent",
    "outerGlow/shadingNoise": "percent",
    "patternFill/opacity": "percent",
    "patternFill/phase": "pixels",
    "patternFill/scale": "percent",
    "solidFill/opacity": "percent",
}

# Match names that correspond to indexed groups in After Effects.
INDEXED_GROUP_MATCH_NAMES = {
    "ADBE Effect Parade",
    "ADBE Mask Parade",
    "ADBE Effect Mask Parade",
}


def parse_property_group(
    tdgp_chunk: Aep.Chunk,
    group_match_name: str,
    time_scale: float,
    property_depth: int,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    frame_rate: float,
) -> PropertyGroup:
    """
    Parse a property group.

    Args:
        tdgp_chunk: The TDGP chunk to parse.
        group_match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized. An indexed group
            (`PropertyBase.property_type == PropertyType.indexed_group`)
            may not have a name value, but always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        property_depth: The nesting depth of this group (0 = layer level).
        effect_param_defs: Project-level effect parameter definitions, used as
            fallback when layer-level parT chunks are missing.
        frame_rate: The frame rate of the parent composition.
    """
    name = MATCH_NAME_TO_NICE_NAME.get(group_match_name, group_match_name)
    child_depth = property_depth + 1

    properties: list[Property | PropertyGroup] = []
    chunks_by_sub_prop = get_chunks_by_match_name(tdgp_chunk)
    for match_name, sub_prop_chunks in chunks_by_sub_prop.items():
        # Find the first LIST chunk; non-LIST chunks (e.g. mkif for masks)
        # are auxiliary data that we skip when determining the property type.
        try:
            first_chunk = find_by_type(
                chunks=sub_prop_chunks, chunk_type="LIST"
            )
        except ChunkNotFoundError:
            continue
        # Effects can share a match name when the same effect type is applied
        # multiple times. Iterate all LIST chunks for sspc and tdgp; other
        # types use the first chunk (additional chunks are auxiliary data).
        if first_chunk.list_type == "sspc":
            for chunk in filter_by_list_type(
                chunks=sub_prop_chunks, list_type="sspc"
            ):
                sub_prop: Property | PropertyGroup = parse_effect(
                    sspc_chunk=chunk,
                    group_match_name=match_name,
                    time_scale=time_scale,
                    property_depth=child_depth,
                    effect_param_defs=effect_param_defs,
                    frame_rate=frame_rate,
                )
                properties.append(sub_prop)
        elif first_chunk.list_type == "tdgp":
            if match_name == "ADBE Mask Atom":
                # Pair each mask tdgp chunk with its mkif (mask info) chunk
                for tdgp_c, mkif_c in zip(
                    filter_by_list_type(
                        chunks=sub_prop_chunks, list_type="tdgp"
                    ),
                    filter_by_type(
                        chunks=sub_prop_chunks, chunk_type="mkif"
                    ),
                ):
                    sub_prop = _parse_mask_atom(
                        tdgp_chunk=tdgp_c,
                        mkif_chunk=mkif_c,
                        time_scale=time_scale,
                        property_depth=child_depth,
                        effect_param_defs=effect_param_defs,
                        frame_rate=frame_rate,
                    )
                    properties.append(sub_prop)
                # Append 1-based index to mask names (e.g. "Mask 1", "Mask 2")
                mask_count = 0
                for p in properties:
                    if isinstance(p, MaskPropertyGroup):
                        mask_count += 1
                        p.name = f"Mask {mask_count}"
            else:
                # Indexed groups (e.g. effects) can share a match name.
                for tdgp_c in filter_by_list_type(
                    chunks=sub_prop_chunks, list_type="tdgp"
                ):
                    sub_prop = parse_property_group(
                        tdgp_chunk=tdgp_c,
                        group_match_name=match_name,
                        time_scale=time_scale,
                        property_depth=child_depth,
                        effect_param_defs=effect_param_defs,
                        frame_rate=frame_rate,
                    )
                    properties.append(sub_prop)
        elif first_chunk.list_type == "tdbs":
            sub_prop = parse_property(
                tdbs_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                frame_rate=frame_rate,
            )
            properties.append(sub_prop)
        elif first_chunk.list_type == "otst":
            sub_prop = parse_orientation(
                otst_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                frame_rate=frame_rate,
            )
            properties.append(sub_prop)
        elif first_chunk.list_type == "btds":
            sub_prop = parse_text_document(
                btds_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                frame_rate=frame_rate,
            )
            properties.append(sub_prop)
        elif first_chunk.list_type == "om-s":
            # TODO: temporarily disabled for debugging
            pass
        else:
            logger.warning(
                "Skipping unsupported property list type '%s' "
                "(match name '%s')",
                first_chunk.list_type,
                match_name,
            )

    # Try to read the group-level enabled flag from its tdsb chunk.
    # Leaf properties always have a tdsb; groups may or may not.
    group_enabled = True
    with suppress(ChunkNotFoundError):
        group_tdsb = find_by_type(chunks=tdgp_chunk.chunks, chunk_type="tdsb")
        group_enabled = group_tdsb.data.enabled

    prop_group = PropertyGroup(
        enabled=group_enabled,
        match_name=group_match_name,
        name=name,
        property_depth=property_depth,
        properties=properties,
    )

    # Set parent reference on all children
    for child in properties:
        child.parent_property = prop_group

    # Mark indexed groups
    if group_match_name in INDEXED_GROUP_MATCH_NAMES:
        prop_group.property_type = PropertyType.INDEXED_GROUP

    # Mark special group types
    if group_match_name == "ADBE Effect Mask Parade":
        prop_group.elided = True
    return prop_group


def _parse_mask_atom(
    tdgp_chunk: Aep.Chunk,
    mkif_chunk: Aep.Chunk,
    time_scale: float,
    property_depth: int,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    frame_rate: float,
) -> MaskPropertyGroup:
    """Parse a mask atom into a MaskPropertyGroup.

    Combines the child properties from the tdgp chunk with the mask-specific
    attributes (inverted, locked, mask_mode, color, mask_feather_falloff,
    mask_motion_blur) parsed from the mkif chunk, and the rotoBezier flag
    from the ADBE Mask Shape tdsb chunk.

    Args:
        tdgp_chunk: The tdgp chunk for this mask atom.
        mkif_chunk: The mkif (mask info) chunk containing mask attributes.
        time_scale: The time scale of the parent composition.
        property_depth: The nesting depth of this group.
        effect_param_defs: Project-level effect parameter definitions.
        frame_rate: The frame rate of the parent composition.
    """
    from ..enums import MaskFeatherFalloff, MaskMode, MaskMotionBlur

    base = parse_property_group(
        tdgp_chunk=tdgp_chunk,
        group_match_name="ADBE Mask Atom",
        time_scale=time_scale,
        property_depth=property_depth,
        effect_param_defs=effect_param_defs,
        frame_rate=frame_rate,
    )

    # Extract rotoBezier from ADBE Mask Shape tdsb (byte 0).
    roto_bezier = False
    chunks_by_mn = get_chunks_by_match_name(tdgp_chunk)
    mask_shape_chunks = chunks_by_mn.get("ADBE Mask Shape", [])
    for chunk in mask_shape_chunks:
        if (
            chunk.chunk_type == "LIST"
            and chunk.list_type == "om-s"
        ):
            with suppress(ChunkNotFoundError):
                tdbs = find_by_list_type(
                    chunks=chunk.chunks, list_type="tdbs"
                )
                tdsb = find_by_type(
                    chunks=tdbs.chunks, chunk_type="tdsb"
                )
                roto_bezier = bool(tdsb.data.roto_bezier)
            break

    mask_group = MaskPropertyGroup(
        enabled=base.enabled,
        match_name=base.match_name,
        name=base.name,
        property_depth=base.property_depth,
        properties=base.properties,
        color=[
            mkif_chunk.color_red / 255.0,
            mkif_chunk.color_green / 255.0,
            mkif_chunk.color_blue / 255.0,
        ],
        inverted=bool(mkif_chunk.inverted),
        locked=bool(mkif_chunk.locked),
        mask_feather_falloff=MaskFeatherFalloff.from_binary(
            int(mkif_chunk.mask_feather_falloff)
        ),
        mask_mode=MaskMode.from_binary(int(mkif_chunk.mode)),
        mask_motion_blur=MaskMotionBlur.from_binary(
            int(mkif_chunk.mask_motion_blur)
        ),
        roto_bezier=roto_bezier,
    )
    mask_group.property_type = base.property_type
    mask_group.is_mask = True
    # Fix parent references so children point to the new mask_group
    for child in mask_group.properties:
        child.parent_property = mask_group
    return mask_group


def parse_orientation(
    otst_chunk: Aep.Chunk,
    match_name: str,
    time_scale: float,
    property_depth: int,
    frame_rate: float,
) -> Property:
    """
    Parse an orientation property.

    Args:
        otst_chunk: The OTST chunk to parse.
        match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        property_depth: The nesting depth of this property (0 = layer level).
        frame_rate: The frame rate of the parent composition.
    """
    tdbs_chunk = find_by_list_type(chunks=otst_chunk.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
        property_depth=property_depth,
        frame_rate=frame_rate,
    )
    # Orientation uses an angle dial control.  ExtendScript reports
    # propertyValueType as ThreeD_SPATIAL and isSpatial as True, even
    # though the binary stores is_spatial=False.
    prop.property_control_type = PropertyControlType.ANGLE
    prop.property_value_type = PropertyValueType.ThreeD_SPATIAL
    prop.is_spatial = True
    prop.dimensions = 3
    prop.vector = True

    # The cdat inside OTST stores doubles as little-endian, unlike the
    # rest of the big-endian RIFX file.  Re-read the raw bytes as LE.
    try:
        cdat_chunk = find_by_type(
            chunks=tdbs_chunk.chunks, chunk_type="cdat"
        )
        n = cdat_chunk.len_data // 8
        values = list(struct.unpack(f"<{n}d", cdat_chunk._raw_data))
        while len(values) < 3:
            values.append(0.0)
        prop.value = values[:3]
    except ChunkNotFoundError:
        prop.value = None

    # Animated orientation keyframes store their 3-component values
    # in otky → otda chunks (big-endian, one otda per keyframe),
    # a sibling of tdbs inside otst.  The standard _parse_keyframes()
    # reads from tdbs which only has 1D orientation data, so we
    # override each keyframe's value with the full 3D otda data.
    try:
        otky_chunk = find_by_list_type(
            chunks=otst_chunk.chunks, list_type="otky"
        )
        otda_chunks = filter_by_type(
            chunks=otky_chunk.chunks, chunk_type="otda"
        )
        for idx, kf in enumerate(prop.keyframes):
            if idx < len(otda_chunks):
                n = otda_chunks[idx].len_data // 8
                kf.value = list(
                    struct.unpack(f">{n}d", otda_chunks[idx]._raw_data)
                )
    except ChunkNotFoundError:
        pass

    return prop


def _parse_shape_shap(shap_chunk: Aep.Chunk) -> ShapeValue:
    """Parse a single shape path from a ``shap`` LIST chunk.

    Each ``shap`` LIST contains:
    - ``shph`` chunk: shape header with closed flag and bounding box
    - ``list`` LIST:  contains ``lhd3`` (point count/size) and ``ldat``
      (raw normalized bezier points)

    Points in ``ldat`` are stored as big-endian ``(f4 x, f4 y)`` pairs,
    normalized to the ``[0, 1]`` range of the bounding box.  Every three
    consecutive points form a cycle:
    ``vertex, out_tangent, in_tangent_of_next_vertex``.

    Args:
        shap_chunk: A ``shap`` LIST chunk.

    Returns:
        A [ShapeValue][] with absolute coordinates and tangent offsets.
    """
    shph_chunk = find_by_type(chunks=shap_chunk.chunks, chunk_type="shph")
    list_chunk = find_by_list_type(chunks=shap_chunk.chunks, list_type="list")

    # Bounding box from shape header
    tl_x = shph_chunk.top_left_x
    tl_y = shph_chunk.top_left_y
    br_x = shph_chunk.bottom_right_x
    br_y = shph_chunk.bottom_right_y
    closed = shph_chunk.closed

    # Read raw bezier points from ldat
    lhd3 = find_by_type(chunks=list_chunk.chunks, chunk_type="lhd3")
    ldat = find_by_type(chunks=list_chunk.chunks, chunk_type="ldat")

    point_count = lhd3.count
    raw_bytes = ldat.items

    # Parse (f4 x, f4 y) pairs — big-endian
    points: list[tuple[float, float]] = []
    for i in range(point_count):
        offset = i * 8
        px, py = struct.unpack_from(">ff", raw_bytes, offset)
        points.append((px, py))

    # De-interleave into vertex / out_tangent / in_tangent triples.
    # Raw order per cycle of 3:  vertex, out_tangent, in_tangent_of_next
    # Following python-lottie:
    #   vertex      = points[i]
    #   out_tangent = points[i + 1]
    #   in_tangent  = points[(i - 1) % len(points)]
    vertices: list[list[float]] = []
    in_tangents: list[list[float]] = []
    out_tangents: list[list[float]] = []

    for i in range(0, len(points), 3):
        vx = tl_x * (1 - points[i][0]) + br_x * points[i][0]
        vy = tl_y * (1 - points[i][1]) + br_y * points[i][1]

        ox = tl_x * (1 - points[i + 1][0]) + br_x * points[i + 1][0]
        oy = tl_y * (1 - points[i + 1][1]) + br_y * points[i + 1][1]

        in_idx = (i - 1) % len(points)
        ix = tl_x * (1 - points[in_idx][0]) + br_x * points[in_idx][0]
        iy = tl_y * (1 - points[in_idx][1]) + br_y * points[in_idx][1]

        vertices.append([vx, vy])
        # Tangents as offsets relative to vertex
        in_tangents.append([ix - vx, iy - vy])
        out_tangents.append([ox - vx, oy - vy])

    return ShapeValue(
        closed=closed,
        vertices=vertices,
        in_tangents=in_tangents,
        out_tangents=out_tangents,
    )


def parse_shape(
    oms_chunk: Aep.Chunk,
    match_name: str,
    time_scale: float,
    property_depth: int,
    frame_rate: float,
) -> Property:
    """Parse a shape/mask-path property from an ``om-s`` LIST chunk.

    An ``om-s`` LIST contains:
    - ``tdbs`` LIST: standard property metadata (timing, keyframes, etc.)
    - ``omks`` LIST: shape keyframe values (one ``shap`` per keyframe,
      or one ``shap`` for static shapes)

    Args:
        oms_chunk: The ``om-s`` LIST chunk to parse.
        match_name: The property match name.
        time_scale: Time scale divisor of the parent composition.
        property_depth: Nesting depth of this property.
        frame_rate: The frame rate of the parent composition.

    Returns:
        A [Property][] with ``property_value_type`` set to
        [SHAPE][aep_parser.enums.PropertyValueType.SHAPE] and ``value``
        set to a [ShapeValue][].
    """
    tdbs_chunk = find_by_list_type(chunks=oms_chunk.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
        property_depth=property_depth,
        frame_rate=frame_rate,
    )

    prop.property_value_type = PropertyValueType.SHAPE
    prop.is_spatial = True
    # Shape properties always carry a value (from omks), even though
    # tdb4 may report no_value=True (there is no cdat for shapes).
    prop.no_value = False

    # Collect shape values from omks → shap LISTs
    try:
        omks_chunk = find_by_list_type(
            chunks=oms_chunk.chunks, list_type="omks"
        )
        shape_values: list[ShapeValue] = []
        for shap_chunk in filter_by_list_type(
            chunks=omks_chunk.chunks, list_type="shap"
        ):
            shape_values.append(_parse_shape_shap(shap_chunk))
    except (ChunkNotFoundError, Exception):
        logger.debug("Could not parse omks shape data for %s", match_name)
        return prop

    # Assign static value (first shape)
    if shape_values:
        prop.value = shape_values[0]

    # Assign shape values to keyframes by index
    for idx, kf in enumerate(prop.keyframes):
        if idx < len(shape_values):
            kf.value = shape_values[idx]

    return prop


def parse_text_document(
    btds_chunk: Aep.Chunk,
    match_name: str,
    time_scale: float,
    property_depth: int,
    frame_rate: float,
) -> Property:
    """
    Parse a text document property.

    Args:
        btds_chunk: The BTDS chunk to parse.
        match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        property_depth: The nesting depth of this property (0 = layer level).
        frame_rate: The frame rate of the parent composition.
    """
    tdbs_chunk = find_by_list_type(chunks=btds_chunk.chunks, list_type="tdbs")
    prop = parse_property(
        tdbs_chunk=tdbs_chunk,
        match_name=match_name,
        time_scale=time_scale,
        property_depth=property_depth,
        frame_rate=frame_rate,
    )

    try:
        btdk_chunk = find_by_list_type(
            chunks=btds_chunk.chunks,
            list_type="btdk",
        )
        parser = CosParser(
            io.BytesIO(btdk_chunk.binary_data),
            len(btdk_chunk.binary_data),
        )
        cos_data = parser.parse()
        if not isinstance(cos_data, dict):
            raise TypeError("Expected dict from COS parser")
        text_documents, _fonts = parse_btdk_cos(cos_data)
        if text_documents:
            prop.value = text_documents[0]
    except (ChunkNotFoundError, Exception):
        logger.debug("Could not parse btdk COS data for %s", match_name)

    return prop


def _determine_property_types(
    no_value: bool,
    color: bool,
    integer: bool,
    vector: bool,
    dimensions: int,
    is_spatial: bool,
    match_name: str,
    name: str,
    animated: bool,
) -> tuple[PropertyControlType, PropertyValueType]:
    """Determine property control and value types from tdb4 flags.

    Uses the combination of boolean flags from the tdb4 chunk to determine
    the property control type (e.g., scalar, color, boolean) and value type
    (e.g., one_d, two_d_spatial, color).

    Args:
        no_value: Whether the property has no value.
        color: Whether the property is a color.
        integer: Whether the property is an integer.
        vector: Whether the property is a vector.
        dimensions: Number of dimensions.
        is_spatial: Whether the property is spatial.
        match_name: The property match name (for debug output).
        name: The property display name (for debug output).
        animated: Whether the property is animated (for debug output).

    Returns:
        Tuple of (property_control_type, property_value_type).
    """
    property_control_type = PropertyControlType.UNKNOWN
    property_value_type = PropertyValueType.UNKNOWN

    if no_value:
        property_value_type = PropertyValueType.NO_VALUE
    if color:
        property_control_type = PropertyControlType.COLOR
        property_value_type = PropertyValueType.COLOR
    elif integer:
        property_control_type = PropertyControlType.BOOLEAN
        property_value_type = PropertyValueType.OneD
    elif vector:
        if dimensions == 1:
            property_control_type = PropertyControlType.SCALAR
            property_value_type = PropertyValueType.OneD
        elif dimensions == 2:
            property_control_type = PropertyControlType.TWO_D
            property_value_type = (
                PropertyValueType.TwoD_SPATIAL
                if is_spatial
                else PropertyValueType.TwoD
            )
        elif dimensions == 3:
            property_control_type = PropertyControlType.THREE_D
            property_value_type = (
                PropertyValueType.ThreeD_SPATIAL
                if is_spatial
                else PropertyValueType.ThreeD
            )

    if property_control_type == PropertyControlType.UNKNOWN:
        logger.warning(
            "Could not determine type for property %s"
            " | name: %s"
            " | dimensions: %s"
            " | animated: %s"
            " | integer: %s"
            " | is_spatial: %s"
            " | vector: %s"
            " | no_value: %s"
            " | color: %s",
            match_name,
            name,
            dimensions,
            animated,
            integer,
            is_spatial,
            vector,
            no_value,
            color,
        )

    return property_control_type, property_value_type


def parse_property(
    tdbs_chunk: Aep.Chunk,
    match_name: str,
    time_scale: float,
    property_depth: int,
    frame_rate: float,
) -> Property:
    """
    Parse a property.

    Args:
        tdbs_chunk: The TDBS chunk to parse.
        match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        property_depth: The nesting depth of this property (0 = layer level).
        frame_rate: The frame rate of the parent composition.
    """
    tdbs_child_chunks = tdbs_chunk.chunks

    tdsb_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="tdsb")

    locked_ratio = tdsb_chunk.locked_ratio
    enabled = tdsb_chunk.enabled
    # ExtendScript only reports dimensionsSeparated=True on the
    # Position property ("ADBE Position") when separation is active.
    # The binary stores the flag on many other properties, but
    # ExtendScript ignores it for non-Position properties and for
    # the individual dimension children ("ADBE Position_0" etc.).
    is_position_parent = match_name == "ADBE Position"
    dimensions_separated = (
        tdsb_chunk.dimensions_separated if is_position_parent else False
    )

    user_name = _get_user_defined_name(tdbs_chunk)
    if user_name is not None:
        name = user_name
    else:
        name = MATCH_NAME_TO_NICE_NAME.get(match_name, match_name)

    tdb4_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="tdb4")

    is_spatial = tdb4_chunk.is_spatial
    raw_expression_enabled = tdb4_chunk.expression_enabled
    animated = tdb4_chunk.animated
    dimensions = tdb4_chunk.dimensions
    integer = tdb4_chunk.integer
    vector = tdb4_chunk.vector
    no_value = tdb4_chunk.no_value
    color = tdb4_chunk.color

    property_control_type, property_value_type = _determine_property_types(
        no_value=no_value,
        color=color,
        integer=integer,
        vector=vector,
        dimensions=dimensions,
        is_spatial=is_spatial,
        match_name=match_name,
        name=name,
        animated=animated,
    )

    try:
        cdat_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="cdat")
        values = cdat_chunk.value[:dimensions]
        # ExtendScript returns a scalar for 1D non-color properties
        if not values:
            value = None
        elif dimensions == 1 and not color:
            value = values[0]
        else:
            value = values
    except ChunkNotFoundError:
        value = None

    try:
        utf8_chunk = find_by_type(chunks=tdbs_child_chunks, chunk_type="Utf8")
        expression = str_contents(utf8_chunk)
    except ChunkNotFoundError:
        expression = ""

    # The binary stores expression_enabled=True on properties that inherit
    # the flag from a sibling (e.g. when Position has an expression, the
    # binary copies the flag to Orientation, X/Y Rotation, etc.).
    # ExtendScript only reports True when the property actually has an
    # expression string.  Separated-dimension children (X/Y/Z Position)
    # also inherit the parent's flag.
    expression_enabled = raw_expression_enabled and bool(expression)

    keyframes = _parse_keyframes(
        tdbs_child_chunks, time_scale, is_spatial, frame_rate=frame_rate
    )

    # Convert 0–1 fraction to 0–100 percentage for properties that
    # ExtendScript reports in percent (e.g. Opacity, Scale).
    if match_name in _PERCENT_MATCH_NAMES:
        if isinstance(value, (int, float)):
            value = value * 100.0
        elif isinstance(value, list):
            value = [v * 100.0 for v in value]
        for kf in keyframes:
            if isinstance(kf.value, (int, float)):
                kf.value = kf.value * 100.0
            elif isinstance(kf.value, list):
                kf.value = [v * 100.0 for v in kf.value]
            # Temporal ease speed is in property units / second.
            # For percent properties the binary stores fractions, so
            # scale speeds by 100 to match ExtendScript's percent/sec.
            for ease in kf.in_temporal_ease:
                ease.speed = ease.speed * 100.0
            for ease in kf.out_temporal_ease:
                ease.speed = ease.speed * 100.0

    # Compute temporal ease for LINEAR/HOLD keyframes.  Must run after
    # percent scaling so that computed speeds use final property units.
    _compute_linear_hold_ease(keyframes, is_spatial, frame_rate)

    return Property(
        animated=animated,
        color=color,
        dimensions_separated=dimensions_separated,
        dimensions=dimensions,
        enabled=enabled,
        expression_enabled=expression_enabled,
        expression=expression,
        integer=integer,
        is_spatial=is_spatial,
        keyframes=keyframes,
        locked_ratio=locked_ratio,
        match_name=match_name,
        name=name,
        no_value=no_value,
        property_control_type=property_control_type,
        property_depth=property_depth,
        property_value_type=property_value_type,
        units_text=_UNITS_TEXT_MAP.get(match_name, ""),
        value=value,
        vector=vector,
    )


def _parse_keyframes(
    tdbs_child_chunks: list[Aep.Chunk],
    time_scale: float,
    is_spatial: bool,
    frame_rate: float,
) -> list[Keyframe]:
    """Parse keyframes from a property's child chunks.

    Args:
        tdbs_child_chunks: The child chunks of the TDBS chunk.
        time_scale: The time scale of the parent composition.
        is_spatial: Whether the property is spatial.
        frame_rate: The frame rate of the parent composition.
    """
    try:
        list_chunk = find_by_list_type(chunks=tdbs_child_chunks, list_type="list")
    except ChunkNotFoundError:
        return []

    kf_items = parse_ldat_items(list_chunk, is_spatial=is_spatial)

    keyframes: list[Keyframe] = []
    for kf in kf_items:
        kf_data = kf.kf_data
        in_ease, out_ease = _extract_temporal_ease(kf_data)
        in_tangent, out_tangent = _extract_spatial_tangents(kf_data)
        keyframes.append(
            Keyframe(
                auto_bezier=kf.auto_bezier,
                continuous_bezier=kf.continuous_bezier,
                frame_time=round(kf.time_raw / time_scale),
                in_interpolation_type=KeyframeInterpolationType.from_binary(
                    kf.in_interpolation_type
                ),
                out_interpolation_type=KeyframeInterpolationType.from_binary(
                    kf.out_interpolation_type
                ),
                label=Label(int(kf.label)),
                roving_across_time=kf.roving_across_time,
                value=_extract_keyframe_value(kf),
                in_temporal_ease=in_ease,
                out_temporal_ease=out_ease,
                in_spatial_tangent=in_tangent,
                out_spatial_tangent=out_tangent,
            )
        )
    return keyframes


def _extract_temporal_ease(
    kf_data: object,
) -> tuple[list[KeyframeEase], list[KeyframeEase]]:
    """Extract in/out temporal ease from a keyframe data payload.

    Returns:
        A ``(in_ease, out_ease)`` tuple.  Each element is a list of
        [KeyframeEase][] objects — one per dimension for
        multi-dimensional properties, or a single element for scalar /
        spatial types.  Returns ``([], [])`` when the keyframe type
        carries no ease data (e.g. markers).
    """
    if not hasattr(kf_data, "in_speed"):
        return [], []

    # kf_multi_dimensional stores speed/influence as arrays (one per
    # dimension); kf_position, kf_color and kf_no_value store scalars.
    if isinstance(kf_data.in_speed, list):
        in_ease = [
            KeyframeEase(speed=s, influence=inf * 100)
            for s, inf in zip(kf_data.in_speed, kf_data.in_influence)
        ]
        out_ease = [
            KeyframeEase(speed=s, influence=inf * 100)
            for s, inf in zip(kf_data.out_speed, kf_data.out_influence)
        ]
    else:
        in_ease = [
            KeyframeEase(
                speed=kf_data.in_speed,
                influence=kf_data.in_influence * 100,
            )
        ]
        out_ease = [
            KeyframeEase(
                speed=kf_data.out_speed,
                influence=kf_data.out_influence * 100,
            )
        ]
    return in_ease, out_ease


def _extract_spatial_tangents(
    kf_data: object,
) -> tuple[list[float] | None, list[float] | None]:
    """Extract in/out spatial tangent vectors from a keyframe data payload.

    Returns:
        A ``(in_tangent, out_tangent)`` tuple.  Each is a list of floats
        (one per dimension) for spatial keyframe types (``kf_position``),
        or ``None`` for non-spatial types.
    """
    if hasattr(kf_data, "tan_in"):
        return list(kf_data.tan_in), list(kf_data.tan_out)
    return None, None


def _extract_keyframe_value(
    kf: Aep.LdatItem,
) -> list[float] | float | None:
    """Extract the value from a keyframe's data payload.

    Returns a scalar for 1-dimensional properties, a list for
    multi-dimensional or color properties, and ``None`` when the
    keyframe type carries no value (e.g. markers).
    """
    kf_data = kf.kf_data
    if not hasattr(kf_data, "value"):
        return None
    values = list(kf_data.value)
    if len(values) == 1:
        return values[0]
    return values


def _segment_speed(
    kf_a: Keyframe,
    kf_b: Keyframe,
    is_spatial: bool,
    frame_rate: float,
) -> list[float]:
    """Compute the constant speed between two adjacent keyframes.

    For spatial properties a single scalar speed (magnitude of the velocity
    vector) is returned.  For non-spatial multi-dimensional properties a
    per-dimension speed list is returned.  For 1-D properties a single-element
    list is returned.

    Args:
        kf_a: The earlier keyframe.
        kf_b: The later keyframe.
        is_spatial: Whether the property is spatial.
        frame_rate: The composition frame rate.

    Returns:
        A list of speed values, one per temporal-ease dimension.
    """
    frame_delta = kf_b.frame_time - kf_a.frame_time
    if frame_delta == 0:
        return [0.0]

    time_seconds = frame_delta / frame_rate
    val_a = kf_a.value
    val_b = kf_b.value

    # Non-numeric values (None, ShapeValue) cannot produce a speed.
    if not isinstance(val_a, (int, float, list)):
        return [0.0]
    if not isinstance(val_b, (int, float, list)):
        return [0.0]

    if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
        return [(float(val_b) - float(val_a)) / time_seconds]

    if isinstance(val_a, list) and isinstance(val_b, list):
        if is_spatial:
            distance = math.sqrt(
                sum((b - a) ** 2 for a, b in zip(val_a, val_b))
            )
            return [distance / time_seconds]
        else:
            return [
                (b - a) / time_seconds for a, b in zip(val_a, val_b)
            ]

    return [0.0]


def _compute_linear_hold_ease(
    keyframes: list[Keyframe],
    is_spatial: bool,
    frame_rate: float,
) -> None:
    """Fill temporal ease for LINEAR and HOLD keyframes with ExtendScript values.

    For BEZIER interpolation the binary stores actual ease values that are
    already parsed.  For LINEAR and HOLD interpolation the binary stores
    zeros, but ExtendScript computes and reports default values:

    - **Influence** is always ``100 / 6`` (approx. 16.667 %).
    - **Speed** for LINEAR equals the constant rate of change between
      adjacent keyframes (*value delta / time in seconds*).  For spatial
      properties a single scalar speed is reported (the magnitude of the
      velocity vector).
    - **Speed** for HOLD is always ``0``.

    Modifies *keyframes* in place.

    Args:
        keyframes: The parsed keyframe list (values already in final units).
        is_spatial: Whether the property is spatial.
        frame_rate: The composition frame rate.
    """
    default_influence = 100.0 / 6.0

    n = len(keyframes)
    if n == 0:
        return

    for i, kf in enumerate(keyframes):
        # --- Outgoing side ---
        if kf.out_temporal_ease:
            out_type = kf.out_interpolation_type
            if out_type == KeyframeInterpolationType.LINEAR:
                if i < n - 1:
                    speeds = _segment_speed(
                        kf, keyframes[i + 1], is_spatial, frame_rate
                    )
                else:
                    speeds = [0.0] * len(kf.out_temporal_ease)
                for ease, s in zip(kf.out_temporal_ease, speeds):
                    ease.speed = s
                    ease.influence = default_influence
            elif out_type == KeyframeInterpolationType.HOLD:
                for ease in kf.out_temporal_ease:
                    ease.speed = 0.0
                    ease.influence = default_influence

        # --- Incoming side ---
        if kf.in_temporal_ease:
            in_type = kf.in_interpolation_type
            if in_type == KeyframeInterpolationType.LINEAR:
                if i > 0:
                    speeds = _segment_speed(
                        keyframes[i - 1], kf, is_spatial, frame_rate
                    )
                else:
                    speeds = [0.0] * len(kf.in_temporal_ease)
                for ease, s in zip(kf.in_temporal_ease, speeds):
                    ease.speed = s
                    ease.influence = default_influence
            elif in_type == KeyframeInterpolationType.HOLD:
                for ease in kf.in_temporal_ease:
                    ease.speed = 0.0
                    ease.influence = default_influence


def parse_effect_param_defs(
    sspc_child_chunks: list[Aep.Chunk],
) -> dict[str, dict[str, Any]]:
    """Parse effect parameter definitions from parT chunk.

    Each effect has a parT LIST containing parameter definitions that
    describe the control type, default values, and ranges.

    Args:
        sspc_child_chunks: The SSPC chunk's child chunks.

    Returns:
        Dict mapping parameter match names to definition dicts.
    """
    part_chunk = find_by_list_type(chunks=sspc_child_chunks, list_type="parT")
    param_defs: dict[str, dict[str, Any]] = {}

    chunks_by_parameter = get_chunks_by_match_name(part_chunk)
    for index, (match_name, parameter_chunks) in enumerate(chunks_by_parameter.items()):
        # Skip first, it describes parent
        if index == 0:
            continue
        param_defs[match_name] = _parse_effect_parameter_def(parameter_chunks)

    return param_defs


def _merge_param_def(prop: Property, param_def: dict[str, Any]) -> None:
    """Merge parameter definition values into a parsed property.

    Overrides auto-detected property attributes with the more precise
    values from the effect's parameter definition.

    Args:
        prop: The property to update in place.
        param_def: The parameter definition dict.
    """
    prop.name = param_def["name"] or prop.name
    prop.property_control_type = param_def["property_control_type"]
    prop.property_value_type = param_def.get(
        "property_value_type", prop.property_value_type
    )
    prop.last_value = param_def.get("last_value")
    prop.default_value = param_def.get("default_value")
    prop.min_value = param_def.get("min_value") or prop.min_value
    prop.max_value = param_def.get("max_value") or prop.max_value
    prop.nb_options = param_def.get("nb_options")
    prop.property_parameters = param_def.get("property_parameters")


def _parse_effect_properties(
    tdgp_chunk: Aep.Chunk,
    param_defs: dict[str, dict[str, Any]],
    time_scale: float,
    child_depth: int,
    frame_rate: float,
) -> list[Property | PropertyGroup]:
    """Parse effect properties and merge with parameter definitions.

    Iterates the tdgp chunk's sub-properties, parses each one, and merges
    in the corresponding parameter definition if available.

    Args:
        tdgp_chunk: The tdgp chunk containing property data.
        param_defs: Parameter definitions to merge into properties.
        time_scale: The time scale of the parent composition.
        child_depth: The property depth for parsed child properties.
        frame_rate: The frame rate of the parent composition.

    Returns:
        List of parsed and merged properties.
    """
    properties: list[Property | PropertyGroup] = []
    chunks_by_property = get_chunks_by_match_name(tdgp_chunk)
    for match_name, prop_chunks in chunks_by_property.items():
        first_chunk = prop_chunks[0]
        if first_chunk.list_type == "tdbs":
            prop = parse_property(
                tdbs_chunk=first_chunk,
                match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                frame_rate=frame_rate,
            )
            if match_name in param_defs:
                _merge_param_def(prop, param_defs[match_name])
            properties.append(prop)
        elif first_chunk.list_type == "tdgp":
            sub_group = parse_property_group(
                tdgp_chunk=first_chunk,
                group_match_name=match_name,
                time_scale=time_scale,
                property_depth=child_depth,
                effect_param_defs={},
                frame_rate=frame_rate,
            )
            properties.append(sub_group)
        else:
            raise NotImplementedError(
                f"Cannot parse parameter value : {first_chunk.list_type}"
            )

    return properties


def parse_effect(
    sspc_chunk: Aep.Chunk,
    group_match_name: str,
    time_scale: float,
    property_depth: int,
    effect_param_defs: dict[str, dict[str, dict[str, Any]]],
    frame_rate: float,
) -> PropertyGroup:
    """
    Parse an effect.

    Args:
        sspc_chunk: The SSPC chunk to parse.
        group_match_name: A special name for the property used to build unique
            naming paths. The match name is not displayed, but you can refer
            to it in scripts. Every property has a unique match-name
            identifier. Match names are stable from version to version
            regardless of the display name (the name attribute value) or any
            changes to the application. Unlike the display name, it is not
            localized. An indexed group (`PropertyBase.property_type ==
            PropertyType.indexed_group`) may not have a name value, but
            always has a match_name value.
        time_scale: The time scale of the parent composition, used as a divisor
            for some frame values.
        property_depth: The nesting depth of this group (0 = layer level).
        effect_param_defs: Project-level effect parameter definitions, used as
            fallback when layer-level parT chunks are missing.
        frame_rate: The frame rate of the parent composition.
    """
    sspc_child_chunks = sspc_chunk.chunks
    fnam_chunk = find_by_type(chunks=sspc_child_chunks, chunk_type="fnam")

    utf8_chunk = fnam_chunk.chunk
    tdgp_chunk = find_by_list_type(chunks=sspc_child_chunks, list_type="tdgp")
    name = _get_user_defined_name(tdgp_chunk) or str_contents(utf8_chunk)

    try:
        param_defs = parse_effect_param_defs(sspc_child_chunks)
    except ChunkNotFoundError:
        # Layer-level sspc may lack parT when the same effect type is used
        # more than once. Fall back to project-level EfdG definitions.
        if group_match_name in effect_param_defs:
            param_defs = effect_param_defs[group_match_name]
        else:
            param_defs = {}
    properties = _parse_effect_properties(
        tdgp_chunk,
        param_defs,
        time_scale,
        child_depth=property_depth + 1,
        frame_rate=frame_rate,
    )

    effect_group = PropertyGroup(
        enabled=True,
        match_name=group_match_name,
        name=name,
        property_depth=property_depth,
        properties=properties,
    )
    effect_group.is_effect = True
    effect_group.property_type = PropertyType.INDEXED_GROUP

    # Set parent reference on all children
    for child in properties:
        child.parent_property = effect_group

    return effect_group


def _parse_effect_parameter_def(parameter_chunks: list[Aep.Chunk]) -> dict[str, Any]:
    """Parse effect parameter definition from pard chunk, returning a dict of values."""
    pard_chunk = find_by_type(chunks=parameter_chunks, chunk_type="pard")

    control_type = PropertyControlType(int(pard_chunk.property_control_type))

    result: dict[str, Any] = {
        "name": pard_chunk.name,
        "property_control_type": control_type,
    }

    if control_type == PropertyControlType.ANGLE:
        result["last_value"] = pard_chunk.last_value
        result["property_value_type"] = PropertyValueType.ORIENTATION

    elif control_type == PropertyControlType.BOOLEAN:
        result["last_value"] = pard_chunk.last_value
        result["default_value"] = pard_chunk.default

    elif control_type == PropertyControlType.COLOR:
        result["last_value"] = pard_chunk.last_color
        result["default_value"] = pard_chunk.default_color
        result["max_value"] = pard_chunk.max_color
        result["property_value_type"] = PropertyValueType.COLOR

    elif control_type == PropertyControlType.ENUM:
        result["last_value"] = pard_chunk.last_value
        result["nb_options"] = pard_chunk.nb_options
        result["default_value"] = pard_chunk.default

    elif control_type == PropertyControlType.SCALAR:
        result["last_value"] = pard_chunk.last_value
        result["min_value"] = pard_chunk.min_value
        result["max_value"] = pard_chunk.max_value

    elif control_type == PropertyControlType.SLIDER:
        result["last_value"] = pard_chunk.last_value
        result["max_value"] = pard_chunk.max_value

    elif control_type == PropertyControlType.THREE_D:
        result["last_value"] = [
            pard_chunk.last_value_x,
            pard_chunk.last_value_y,
            pard_chunk.last_value_z,
        ]

    elif control_type == PropertyControlType.TWO_D:
        result["last_value"] = [pard_chunk.last_value_x, pard_chunk.last_value_y]

    with suppress(ChunkNotFoundError):
        pdnm_chunk = find_by_type(chunks=parameter_chunks, chunk_type="pdnm")
        utf8_chunk = pdnm_chunk.chunk
        pdnm_data = str_contents(utf8_chunk)
        if control_type == PropertyControlType.ENUM:
            result["property_parameters"] = pdnm_data.split("|")
        elif pdnm_data:
            result["name"] = pdnm_data

    return result


def _get_user_defined_name(root_chunk: Aep.Chunk) -> str | None:
    """Get the user defined name of the property if there is one, else None.

    Args:
        root_chunk (Aep.Chunk): The LIST chunk to parse.

    Returns:
        The user-defined name (possibly empty string), or None when
        the property uses the default sentinel name.
    """
    tdsn_chunk = find_by_type(chunks=root_chunk.chunks, chunk_type="tdsn")
    utf8_chunk = tdsn_chunk.chunk
    name = str_contents(utf8_chunk)

    # Check if there is a custom user defined name added.
    # The default if there is not is "-_0_/-".
    if name != "-_0_/-":
        return name
    return None
