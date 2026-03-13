"""Property default / synthesis helpers.

This module contains all the logic for:

* Setting ``default_value`` on transform properties parsed from the binary.
* Synthesizing missing transform properties (AE always exposes twelve).
* Synthesizing missing children in standard property groups
  (Material Options, Geometry Options, Layer Styles, Mask atoms, etc.).
* Setting ``min_value`` / ``max_value`` on properties with known bounds.
* Reordering top-level layer groups to match the canonical ExtendScript order.

The two public entry points are:

* [set_transform_defaults][] - called once per layer to fill transform.
* [set_layer_property_defaults][] - called once per layer for everything else.
"""

from __future__ import annotations

from typing import Any, NamedTuple

from ..enums import (
    PropertyControlType,
    PropertyType,
    PropertyValueType,
)
from ..models.layers.av_layer import AVLayer
from ..models.layers.layer import Layer
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from .property_value import _UNITS_TEXT_MAP


class _TransformSpec(NamedTuple):
    """Metadata for a standard transform property."""

    match_name: str
    name: str
    dimensions: int
    is_spatial: bool
    property_value_type: PropertyValueType


# Canonical order of transform properties as reported by ExtendScript.
# Spatial values (Anchor Point, Position, Position_0, Position_1) are
# computed from layer/comp dimensions; all others use a fixed default.
_TRANSFORM_SPECS: list[_TransformSpec] = [
    _TransformSpec(
        "ADBE Anchor Point", "Anchor Point", 3, True, PropertyValueType.ThreeD_SPATIAL
    ),
    _TransformSpec(
        "ADBE Position", "Position", 3, True, PropertyValueType.ThreeD_SPATIAL
    ),
    _TransformSpec("ADBE Position_0", "X Position", 1, False, PropertyValueType.OneD),
    _TransformSpec("ADBE Position_1", "Y Position", 1, False, PropertyValueType.OneD),
    _TransformSpec("ADBE Position_2", "Z Position", 1, False, PropertyValueType.OneD),
    _TransformSpec("ADBE Scale", "Scale", 3, False, PropertyValueType.ThreeD),
    _TransformSpec(
        "ADBE Orientation", "Orientation", 3, True, PropertyValueType.ThreeD_SPATIAL
    ),
    _TransformSpec("ADBE Rotate X", "X Rotation", 1, False, PropertyValueType.OneD),
    _TransformSpec("ADBE Rotate Y", "Y Rotation", 1, False, PropertyValueType.OneD),
    _TransformSpec("ADBE Rotate Z", "Rotation", 1, False, PropertyValueType.OneD),
    _TransformSpec("ADBE Opacity", "Opacity", 1, False, PropertyValueType.OneD),
    _TransformSpec(
        "ADBE Envir Appear in Reflect",
        "Appears in Reflections",
        1,
        False,
        PropertyValueType.OneD,
    ),
]

# Map of match_name > fixed default for standard transform properties.
# Position and Anchor Point defaults depend on layer/comp dimensions and
# are handled separately.
_TRANSFORM_FIXED_DEFAULTS: dict[str, Any] = {
    "ADBE Scale": [100.0, 100.0, 100.0],
    "ADBE Rotate X": 0.0,
    "ADBE Rotate Y": 0.0,
    "ADBE Rotate Z": 0.0,
    "ADBE Opacity": 100.0,
    "ADBE Orientation": [0.0, 0.0, 0.0],
    "ADBE Position_2": 0.0,
    "ADBE Envir Appear in Reflect": 1.0,
}


def _synthesize_property(
    spec: _TransformSpec,
    value: Any,
    default_value: Any,
) -> Property:
    """Create a `Property` for a transform entry absent from the binary.

    The property is built with neutral metadata (no keyframes, no expression,
    enabled) and the supplied *value* / *default_value*.

    Args:
        spec: Metadata describing the transform property.
        value: The current value to assign.
        default_value: The default value for `is_modified` comparison.
    """
    prop = Property(
        animated=False,
        color=False,
        dimensions_separated=False,
        dimensions=spec.dimensions,
        enabled=True,
        expression_enabled=False,
        expression="",
        integer=False,
        is_spatial=spec.is_spatial,
        keyframes=[],
        locked_ratio=False,
        match_name=spec.match_name,
        name=spec.name,
        no_value=False,
        property_control_type=PropertyControlType.UNKNOWN,
        property_depth=2,
        property_value_type=spec.property_value_type,
        units_text=_UNITS_TEXT_MAP.get(spec.match_name, ""),
        value=value,
        vector=spec.dimensions > 1,
    )
    prop.default_value = default_value
    return prop


def set_transform_defaults(layer: Layer) -> None:
    """Assign defaults and synthesize missing transform properties.

    After Effects always exposes twelve transform properties via ExtendScript
    regardless of whether the layer is 2-D or 3-D.  The binary format, however,
    only stores properties relevant to the current layer state.  This function:

    1. Sets ``default_value`` on every transform property already parsed from
       the binary so that `Property.is_modified` works correctly.
    2. Creates ``Property`` objects for any of the twelve canonical properties
       that are absent from the binary.
    3. Re-orders ``transform.properties`` to match the canonical ExtendScript
       order.

    Spatial defaults (Anchor Point, Position, and the X / Y separated followers)
    depend on layer dimensions and are computed here; all other defaults are
    fixed constants defined in ``_TRANSFORM_FIXED_DEFAULTS``.
    """
    transform = layer.transform
    if transform is None:
        return

    # Determine spatial center. For AVLayers with a linked source, width
    # and height come from the source; otherwise fall back to comp dims.
    if isinstance(layer, AVLayer):
        w = float(layer.width)
        h = float(layer.height)
    else:
        w = float(layer.containing_comp.width)
        h = float(layer.containing_comp.height)

    center_x = w / 2.0
    center_y = h / 2.0

    # Spatial defaults depend on layer dimensions.
    spatial_defaults: dict[str, Any] = {
        "ADBE Anchor Point": [center_x, center_y, 0.0],
        "ADBE Position": [center_x, center_y, 0.0],
        "ADBE Position_0": center_x,
        "ADBE Position_1": center_y,
    }

    # --- Phase 1: set default_value on properties parsed from binary --------
    existing: dict[str, Property] = {}
    for prop in transform.properties:
        if isinstance(prop, Property):
            existing[prop.match_name] = prop
            # Pad 2D Scale to 3D with Z=100 (ExtendScript always reports 3D)
            if (
                prop.match_name == "ADBE Scale"
                and isinstance(prop.value, list)
                and len(prop.value) == 2
            ):
                prop.value = prop.value + [100.0]
                prop.dimensions = 3
                prop.property_value_type = PropertyValueType.ThreeD
                for kf in prop.keyframes:
                    if isinstance(kf.value, list) and len(kf.value) == 2:
                        kf.value = kf.value + [100.0]
            if prop.default_value is not None:
                continue  # already set (e.g. by effect param defs)
            default = _TRANSFORM_FIXED_DEFAULTS.get(prop.match_name)
            if default is None:
                default = spatial_defaults.get(prop.match_name)
            if default is not None:
                # When the parser stores a vector property as a scalar
                # (e.g. Orientation parsed as 0.0 instead of [0,0,0]),
                # coerce the default to match the actual value type.
                if isinstance(default, list) and not isinstance(
                    prop.value, (list, tuple)
                ):
                    default = default[0] if default else 0.0
                prop.default_value = default

    # --- Phase 2: synthesize missing properties & reorder -------------------
    # Match names whose synthesized *value* is 0.0 (inactive separation
    # followers) while their *default* comes from spatial_defaults.
    _INACTIVE_FOLLOWER_VALUE: dict[str, float] = {
        "ADBE Position_0": 0.0,
        "ADBE Position_1": 0.0,
    }

    ordered: list[Property] = []
    for spec in _TRANSFORM_SPECS:
        if spec.match_name in existing:
            ordered.append(existing[spec.match_name])
        else:
            # Determine value and default for the synthesised property.
            default = _TRANSFORM_FIXED_DEFAULTS.get(spec.match_name)
            if default is None:
                default = spatial_defaults.get(spec.match_name)
            value: list[float] | float | None = _INACTIVE_FOLLOWER_VALUE.get(
                spec.match_name
            )
            if value is None:
                value = default
            if value is None:
                value = [0.0] * spec.dimensions if spec.dimensions > 1 else 0.0
            if default is None:
                default = value
            prop = _synthesize_property(spec, value, default)
            prop.parent_property = transform
            ordered.append(prop)

    transform.properties = ordered  # type: ignore[assignment]

    # --- Phase 3: context-dependent naming ----------------------------------
    # ExtendScript displays "ADBE Rotate Z" as "Rotation" on 2-D layers
    # and "Z Rotation" on 3-D layers.  Adjust the display name here.
    is_3d = isinstance(layer, AVLayer) and layer.three_d_layer
    if not is_3d:
        rotate_z = existing.get("ADBE Rotate Z")
        if rotate_z is None:
            # Must be a synthesized property - find it in ordered list
            for p in ordered:
                if p.match_name == "ADBE Rotate Z":
                    rotate_z = p
                    break
        if rotate_z is not None:
            rotate_z.name = "Rotation"

        # ExtendScript always reports Scale Z = 100 for 2-D layers,
        # regardless of the binary value.
        scale_prop = existing.get("ADBE Scale")
        if scale_prop is None:
            for p in ordered:
                if p.match_name == "ADBE Scale":
                    scale_prop = p
                    break
        if scale_prop is not None:
            if isinstance(scale_prop.value, list) and len(scale_prop.value) >= 3:
                scale_prop.value[2] = 100.0
            for kf in scale_prop.keyframes:
                if isinstance(kf.value, list) and len(kf.value) >= 3:
                    kf.value[2] = 100.0

    # --- Phase 4: set min/max on transform properties -----------------------
    _apply_min_max_defaults(transform)


# Hardcoded min/max values that ExtendScript reports for standard properties.
# The binary does not store these; they are implicit in the AE object model.
_PROPERTY_MIN_MAX: dict[str, tuple[float, float]] = {
    # Transform
    "ADBE Opacity": (0, 100),
    # Geometry Options
    "ADBE Bevel Direction": (1, 2),
    # Material Options
    "ADBE Reflection Coefficient": (0, 100),
    "ADBE Glossiness Coefficient": (0, 100),
    "ADBE Fresnel Coefficient": (0, 100),
    "ADBE Transparency Coefficient": (0, 100),
    "ADBE Transp Rolloff": (0, 100),
    "ADBE Index of Refraction": (1, 5),
    # Mask properties
    "ADBE Mask Feather": (0, 32000),
    "ADBE Mask Opacity": (0, 100),
    "ADBE Mask Offset": (-32000, 32000),
}


def _apply_min_max_defaults(group: PropertyGroup) -> None:
    """Set ``min_value`` / ``max_value`` on properties with known bounds.

    ExtendScript exposes fixed min/max on certain standard properties whose
    binary bounds (``tdum``/``tduM`` chunks) may differ from the values
    reported by ExtendScript.  This function walks all children of *group*
    and applies ``_PROPERTY_MIN_MAX`` overrides unconditionally.

    Args:
        group: The property group whose children should be updated.
    """
    for child in group.properties:
        if isinstance(child, Property):
            bounds = _PROPERTY_MIN_MAX.get(child.match_name)
            if bounds is not None:
                child.min_value = bounds[0]
                child.max_value = bounds[1]
        elif isinstance(child, PropertyGroup):
            _apply_min_max_defaults(child)


def _derive_layer_styles_enabled(layer: Layer) -> None:
    """Derive `enabled` for the Layer Styles group and Blend Options.

    ExtendScript reports the Layer Styles group as ``enabled=False`` when
    no individual style (Drop Shadow, Inner Glow, etc.) is enabled.
    Blend Options mirrors the Layer Styles group's enabled state.
    The binary stores ``enabled=True`` for both regardless.

    Args:
        layer: The layer to fix up.
    """
    for group in layer.properties:
        if not isinstance(group, PropertyGroup):
            continue
        if group.match_name != "ADBE Layer Styles":
            continue
        any_style_enabled = False
        for child in group.properties:
            if not isinstance(child, PropertyGroup):
                continue
            # Blend Options follows the parent; skip it for the check
            if child.match_name == "ADBE Blend Options Group":
                continue
            if child.enabled:
                any_style_enabled = True
                break
        group.enabled = any_style_enabled
        # Blend Options mirrors the Layer Styles group enabled state
        for child in group.properties:
            if (
                isinstance(child, PropertyGroup)
                and child.match_name == "ADBE Blend Options Group"
            ):
                child.enabled = any_style_enabled
                break
        break


def set_layer_property_defaults(layer: Layer) -> None:
    """Apply min/max and other property defaults to all layer groups.

    Walks all top-level property groups on the layer (excluding Transform,
    which is handled by [set_transform_defaults][]).  Also synthesizes
    missing sub-properties in standard groups (Material Options, Geometry
    Options, etc.) and missing top-level groups that ExtendScript always
    exposes.

    Args:
        layer: The layer whose properties should be updated.
    """
    # --- Synthesize missing top-level groups --------------------------------
    _synthesize_missing_top_level_groups(layer)

    # --- Synthesize missing sub-properties & apply min/max ------------------
    for group in layer.properties:
        if isinstance(group, PropertyGroup):
            if group.match_name == "ADBE Transform Group":
                continue  # already handled by set_transform_defaults
            _synthesize_group_children(group)
            _apply_min_max_defaults(group)

    # --- Derive Layer Styles enabled from children -------------------------
    # ExtendScript reports the Layer Styles group and Blend Options as
    # enabled=False when no individual style is enabled, even though the
    # binary stores enabled=True at the group level.
    _derive_layer_styles_enabled(layer)


# ---------------------------------------------------------------------------
# Property synthesis specs
# ---------------------------------------------------------------------------

_USE_VALUE = object()
"""Sentinel indicating ``_PropSpec.default_value`` should mirror ``value``."""


class _PropSpec(NamedTuple):
    """Metadata for a synthesized property."""

    match_name: str
    name: str
    value: Any
    pvt: PropertyValueType
    dimensions: int = 1
    is_spatial: bool = False
    color: bool = False
    min_value: float | None = None
    max_value: float | None = None
    default_value: Any = _USE_VALUE


# Color min/max bounds used by Layer Styles and Material Shadow Color.
_COLOR_MIN: float = -3921568.62745098
_COLOR_MAX: float = 3921568.62745098

# Canonical children of "ADBE Material Options Group" as reported by
# ExtendScript.  Properties already parsed from binary are skipped.
_MATERIAL_SPECS: list[_PropSpec] = [
    _PropSpec("ADBE Casts Shadows", "Casts Shadows", 0.0, PropertyValueType.OneD),
    _PropSpec(
        "ADBE Light Transmission",
        "Light Transmission",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec("ADBE Accepts Shadows", "Accepts Shadows", 1.0, PropertyValueType.OneD),
    _PropSpec("ADBE Accepts Lights", "Accepts Lights", 1.0, PropertyValueType.OneD),
    _PropSpec(
        "ADBE Shadow Color",
        "Shadow Color",
        [0.0, 0.0, 0.0, 1.0],
        PropertyValueType.COLOR,
        dimensions=4,
        is_spatial=True,
        color=True,
        min_value=_COLOR_MIN,
        max_value=_COLOR_MAX,
    ),
    _PropSpec(
        "ADBE Appears in Reflections",
        "Appears in Reflections",
        1.0,
        PropertyValueType.OneD,
    ),
    _PropSpec(
        "ADBE Ambient Coefficient",
        "Ambient",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Diffuse Coefficient",
        "Diffuse",
        50.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Specular Coefficient",
        "Specular Intensity",
        50.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Shininess Coefficient",
        "Specular Shininess",
        5.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Metal Coefficient",
        "Metal",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Reflection Coefficient",
        "Reflection Intensity",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Glossiness Coefficient",
        "Reflection Sharpness",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Fresnel Coefficient",
        "Reflection Rolloff",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Transparency Coefficient",
        "Transparency",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Transp Rolloff",
        "Transparency Rolloff",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Index of Refraction",
        "Index of Refraction",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=5,
    ),
]

# Canonical children of "ADBE Extrsn Options Group".
_EXTRUSION_SPECS: list[_PropSpec] = [
    _PropSpec(
        "ADBE Bevel Styles",
        "Bevel Style",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=4,
    ),
    _PropSpec(
        "ADBE Bevel Direction",
        "Bevel Direction",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=2,
    ),
    _PropSpec(
        "ADBE Bevel Depth",
        "Bevel Depth",
        2.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Hole Bevel Depth",
        "Hole Bevel Depth",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Extrsn Depth",
        "Extrusion Depth",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=10000,
    ),
]

# Canonical children of "ADBE Plane Options Group".
_PLANE_SPECS: list[_PropSpec] = [
    _PropSpec(
        "ADBE Plane Curvature",
        "Curvature",
        0.0,
        PropertyValueType.OneD,
        min_value=-100,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Plane Subdivision",
        "Segments",
        4.0,
        PropertyValueType.OneD,
        min_value=2,
        max_value=256,
    ),
]

# Canonical children of "ADBE Audio Group".
_AUDIO_SPECS: list[_PropSpec] = [
    _PropSpec(
        "ADBE Audio Levels",
        "Audio Levels",
        [0.0, 0.0],
        PropertyValueType.TwoD,
        dimensions=2,
        min_value=-192,
        max_value=24,
    ),
]

# Canonical children of "ADBE Source Options Group".
_SOURCE_OPTIONS_SPECS: list[_PropSpec] = [
    _PropSpec(
        "ADBE Layer Source Alternate",
        "Item Cache Entry",
        None,
        PropertyValueType.NO_VALUE,
        default_value=0,
    ),
]

# Canonical children of "ADBE Effect Built In Params" (Compositing Options)
# that are simple properties.  The Masks indexed group is synthesized
# separately by ``_fill_compositing_options``.
_COMPOSITING_OPTIONS_PROPERTY_SPECS: list[_PropSpec] = [
    _PropSpec(
        "ADBE Effect Mask Opacity",
        "Effect Opacity",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE Force CPU GPU",
        "GPU Rendering",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=3,
    ),
]

# Canonical children of a mask atom ("ADBE Mask Atom").
# Mask Path (ADBE Mask Shape) must already exist in binary (it carries
# the shape data); the remaining three are synthesized when absent.
_MASK_ATOM_SPECS: list[_PropSpec] = [
    _PropSpec(
        "ADBE Mask Feather",
        "Mask Feather",
        [0.0, 0.0],
        PropertyValueType.TwoD,
        dimensions=2,
        min_value=0,
        max_value=32000,
    ),
    _PropSpec(
        "ADBE Mask Opacity",
        "Mask Opacity",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec("ADBE Mask Offset", "Mask Expansion", 0.0, PropertyValueType.OneD),
]

# Mapping from group match_name to ordered list of child property specs.
_GROUP_CHILD_SPECS: dict[str, list[_PropSpec]] = {
    "ADBE Material Options Group": _MATERIAL_SPECS,
    "ADBE Extrsn Options Group": _EXTRUSION_SPECS,
    "ADBE Plane Options Group": _PLANE_SPECS,
    "ADBE Audio Group": _AUDIO_SPECS,
    "ADBE Source Options Group": _SOURCE_OPTIONS_SPECS,
}

# Canonical children for Layer Styles sub-groups.

_DROP_SHADOW_SPECS: list[_PropSpec] = [
    _PropSpec(
        "dropShadow/mode2",
        "Blend Mode",
        5.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "dropShadow/color",
        "Color",
        [0.0, 0.0, 0.0, 1.0],
        PropertyValueType.COLOR,
        dimensions=4,
        is_spatial=True,
        color=True,
        min_value=_COLOR_MIN,
        max_value=_COLOR_MAX,
    ),
    _PropSpec(
        "dropShadow/opacity",
        "Opacity",
        75.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "dropShadow/useGlobalAngle",
        "Use Global Light",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
    _PropSpec("dropShadow/localLightingAngle", "Angle", 120.0, PropertyValueType.OneD),
    _PropSpec(
        "dropShadow/distance",
        "Distance",
        5.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=30000,
    ),
    _PropSpec(
        "dropShadow/chokeMatte",
        "Spread",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "dropShadow/blur",
        "Size",
        5.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=250,
    ),
    _PropSpec(
        "dropShadow/noise",
        "Noise",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "dropShadow/layerConceals",
        "Layer Knocks Out Drop Shadow",
        1.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
]

_INNER_SHADOW_SPECS: list[_PropSpec] = [
    _PropSpec(
        "innerShadow/mode2",
        "Blend Mode",
        5.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "innerShadow/color",
        "Color",
        [0.0, 0.0, 0.0, 1.0],
        PropertyValueType.COLOR,
        dimensions=4,
        is_spatial=True,
        color=True,
        min_value=_COLOR_MIN,
        max_value=_COLOR_MAX,
    ),
    _PropSpec(
        "innerShadow/opacity",
        "Opacity",
        75.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "innerShadow/useGlobalAngle",
        "Use Global Light",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
    _PropSpec("innerShadow/localLightingAngle", "Angle", 120.0, PropertyValueType.OneD),
    _PropSpec(
        "innerShadow/distance",
        "Distance",
        5.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=30000,
    ),
    _PropSpec(
        "innerShadow/chokeMatte",
        "Choke",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "innerShadow/blur",
        "Size",
        5.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=250,
    ),
    _PropSpec(
        "innerShadow/noise",
        "Noise",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
]

_OUTER_GLOW_SPECS: list[_PropSpec] = [
    _PropSpec(
        "outerGlow/mode2",
        "Blend Mode",
        11.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "outerGlow/opacity",
        "Opacity",
        75.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "outerGlow/noise",
        "Noise",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "outerGlow/AEColorChoice",
        "Color Type",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=2,
    ),
    _PropSpec(
        "outerGlow/color",
        "Color",
        [1.0, 1.0, 0.74509803921569, 1.0],
        PropertyValueType.COLOR,
        dimensions=4,
        is_spatial=True,
        color=True,
        min_value=_COLOR_MIN,
        max_value=_COLOR_MAX,
    ),
    _PropSpec(
        "outerGlow/gradient",
        "Colors",
        None,
        PropertyValueType.NO_VALUE,
        is_spatial=True,
    ),
    _PropSpec(
        "outerGlow/gradientSmoothness",
        "Gradient Smoothness",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "outerGlow/glowTechnique",
        "Technique",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=2,
    ),
    _PropSpec(
        "outerGlow/chokeMatte",
        "Spread",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "outerGlow/blur",
        "Size",
        5.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=250,
    ),
    _PropSpec(
        "outerGlow/inputRange",
        "Range",
        50.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=100,
    ),
    _PropSpec(
        "outerGlow/shadingNoise",
        "Jitter",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
]

_INNER_GLOW_SPECS: list[_PropSpec] = [
    _PropSpec(
        "innerGlow/mode2",
        "Blend Mode",
        11.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "innerGlow/opacity",
        "Opacity",
        75.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "innerGlow/noise",
        "Noise",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "innerGlow/AEColorChoice",
        "Color Type",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=2,
    ),
    _PropSpec(
        "innerGlow/color",
        "Color",
        [1.0, 1.0, 0.74509803921569, 1.0],
        PropertyValueType.COLOR,
        dimensions=4,
        is_spatial=True,
        color=True,
        min_value=_COLOR_MIN,
        max_value=_COLOR_MAX,
    ),
    _PropSpec(
        "innerGlow/gradient",
        "Colors",
        None,
        PropertyValueType.NO_VALUE,
        is_spatial=True,
    ),
    _PropSpec(
        "innerGlow/gradientSmoothness",
        "Gradient Smoothness",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "innerGlow/glowTechnique",
        "Technique",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=2,
    ),
    _PropSpec(
        "innerGlow/innerGlowSource",
        "Source",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=2,
    ),
    _PropSpec(
        "innerGlow/chokeMatte",
        "Choke",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "innerGlow/blur",
        "Size",
        5.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=250,
    ),
    _PropSpec(
        "innerGlow/inputRange",
        "Range",
        50.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=100,
    ),
    _PropSpec(
        "innerGlow/shadingNoise",
        "Jitter",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
]

_BEVEL_EMBOSS_SPECS: list[_PropSpec] = [
    _PropSpec(
        "bevelEmboss/bevelStyle",
        "Style",
        2.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=5,
    ),
    _PropSpec(
        "bevelEmboss/bevelTechnique",
        "Technique",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=3,
    ),
    _PropSpec(
        "bevelEmboss/strengthRatio",
        "Depth",
        100.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=1000,
    ),
    _PropSpec(
        "bevelEmboss/bevelDirection",
        "Direction",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=2,
    ),
    _PropSpec(
        "bevelEmboss/blur",
        "Size",
        5.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=250,
    ),
    _PropSpec(
        "bevelEmboss/softness",
        "Soften",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=16,
    ),
    _PropSpec(
        "bevelEmboss/useGlobalAngle",
        "Use Global Light",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
    _PropSpec("bevelEmboss/localLightingAngle", "Angle", 120.0, PropertyValueType.OneD),
    _PropSpec(
        "bevelEmboss/localLightingAltitude", "Altitude", 30.0, PropertyValueType.OneD
    ),
    _PropSpec(
        "bevelEmboss/highlightMode",
        "Highlight Mode",
        11.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "bevelEmboss/highlightColor",
        "Highlight Color",
        [1.0, 1.0, 1.0, 1.0],
        PropertyValueType.COLOR,
        dimensions=4,
        is_spatial=True,
        color=True,
        min_value=_COLOR_MIN,
        max_value=_COLOR_MAX,
    ),
    _PropSpec(
        "bevelEmboss/highlightOpacity",
        "Highlight Opacity",
        75.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "bevelEmboss/shadowMode",
        "Shadow Mode",
        5.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "bevelEmboss/shadowColor",
        "Shadow Color",
        [0.0, 0.0, 0.0, 1.0],
        PropertyValueType.COLOR,
        dimensions=4,
        is_spatial=True,
        color=True,
        min_value=_COLOR_MIN,
        max_value=_COLOR_MAX,
    ),
    _PropSpec(
        "bevelEmboss/shadowOpacity",
        "Shadow Opacity",
        75.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
]

_SATIN_SPECS: list[_PropSpec] = [
    _PropSpec(
        "chromeFX/mode2",
        "Blend Mode",
        5.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "chromeFX/color",
        "Color",
        [0.0, 0.0, 0.0, 1.0],
        PropertyValueType.COLOR,
        dimensions=4,
        is_spatial=True,
        color=True,
        min_value=_COLOR_MIN,
        max_value=_COLOR_MAX,
    ),
    _PropSpec(
        "chromeFX/opacity",
        "Opacity",
        50.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec("chromeFX/localLightingAngle", "Angle", 19.0, PropertyValueType.OneD),
    _PropSpec(
        "chromeFX/distance",
        "Distance",
        11.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=250,
    ),
    _PropSpec(
        "chromeFX/blur",
        "Size",
        14.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=250,
    ),
    _PropSpec(
        "chromeFX/invert",
        "Invert",
        1.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
]

_COLOR_OVERLAY_SPECS: list[_PropSpec] = [
    _PropSpec(
        "solidFill/mode2",
        "Blend Mode",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "solidFill/color",
        "Color",
        [1.0, 0.0, 0.0, 1.0],
        PropertyValueType.COLOR,
        dimensions=4,
        is_spatial=True,
        color=True,
        min_value=_COLOR_MIN,
        max_value=_COLOR_MAX,
    ),
    _PropSpec(
        "solidFill/opacity",
        "Opacity",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
]

_GRADIENT_OVERLAY_SPECS: list[_PropSpec] = [
    _PropSpec(
        "gradientFill/mode2",
        "Blend Mode",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "gradientFill/opacity",
        "Opacity",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "gradientFill/gradient",
        "Colors",
        None,
        PropertyValueType.NO_VALUE,
        is_spatial=True,
    ),
    _PropSpec(
        "gradientFill/gradientSmoothness",
        "Gradient Smoothness",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec("gradientFill/angle", "Angle", 90.0, PropertyValueType.OneD),
    _PropSpec(
        "gradientFill/type",
        "Style",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=5,
    ),
    _PropSpec(
        "gradientFill/reverse",
        "Reverse",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
    _PropSpec(
        "gradientFill/align",
        "Align with Layer",
        1.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
    _PropSpec(
        "gradientFill/scale",
        "Scale",
        100.0,
        PropertyValueType.OneD,
        min_value=10,
        max_value=150,
    ),
    _PropSpec(
        "gradientFill/offset",
        "Offset",
        [0.0, 0.0],
        PropertyValueType.TwoD_SPATIAL,
        dimensions=2,
        is_spatial=True,
    ),
]

_PATTERN_OVERLAY_SPECS: list[_PropSpec] = [
    _PropSpec(
        "patternFill/mode2",
        "Blend Mode",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "patternFill/opacity",
        "Opacity",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "patternFill/align",
        "Link with Layer",
        1.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
    _PropSpec(
        "patternFill/scale",
        "Scale",
        100.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=1000,
    ),
    _PropSpec(
        "patternFill/phase",
        "Offset",
        [0.0, 0.0],
        PropertyValueType.TwoD_SPATIAL,
        dimensions=2,
        is_spatial=True,
    ),
]

_STROKE_SPECS: list[_PropSpec] = [
    _PropSpec(
        "frameFX/mode2",
        "Blend Mode",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=33,
    ),
    _PropSpec(
        "frameFX/color",
        "Color",
        [1.0, 0.0, 0.0, 1.0],
        PropertyValueType.COLOR,
        dimensions=4,
        is_spatial=True,
        color=True,
        min_value=_COLOR_MIN,
        max_value=_COLOR_MAX,
    ),
    _PropSpec(
        "frameFX/size", "Size", 3.0, PropertyValueType.OneD, min_value=1, max_value=250
    ),
    _PropSpec(
        "frameFX/opacity",
        "Opacity",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "frameFX/style",
        "Position",
        1.0,
        PropertyValueType.OneD,
        min_value=1,
        max_value=3,
    ),
]

# Blending Options has two direct properties and one sub-group.
_BLEND_OPTIONS_GLOBAL_SPECS: list[_PropSpec] = [
    _PropSpec(
        "ADBE Global Angle2", "Global Light Angle", 120.0, PropertyValueType.OneD
    ),
    _PropSpec(
        "ADBE Global Altitude2", "Global Light Altitude", 30.0, PropertyValueType.OneD
    ),
]

_ADV_BLEND_SPECS: list[_PropSpec] = [
    _PropSpec(
        "ADBE Layer Fill Opacity2",
        "Fill Opacity",
        100.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=100,
    ),
    _PropSpec(
        "ADBE R Channel Blend",
        "Red",
        1.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
    _PropSpec(
        "ADBE G Channel Blend",
        "Green",
        1.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
    _PropSpec(
        "ADBE B Channel Blend",
        "Blue",
        1.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
    _PropSpec(
        "ADBE Blend Interior",
        "Blend Interior Styles as Group",
        0.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
    _PropSpec(
        "ADBE Blend Ranges",
        "Use Blend Ranges from Source",
        1.0,
        PropertyValueType.OneD,
        min_value=0,
        max_value=1,
    ),
]

# Layer Styles sub-group specs (keyed by sub-group match name).
_LAYER_STYLE_CHILD_SPECS: dict[str, list[_PropSpec]] = {
    "dropShadow/enabled": _DROP_SHADOW_SPECS,
    "innerShadow/enabled": _INNER_SHADOW_SPECS,
    "outerGlow/enabled": _OUTER_GLOW_SPECS,
    "innerGlow/enabled": _INNER_GLOW_SPECS,
    "bevelEmboss/enabled": _BEVEL_EMBOSS_SPECS,
    "chromeFX/enabled": _SATIN_SPECS,
    "solidFill/enabled": _COLOR_OVERLAY_SPECS,
    "gradientFill/enabled": _GRADIENT_OVERLAY_SPECS,
    "patternFill/enabled": _PATTERN_OVERLAY_SPECS,
    "frameFX/enabled": _STROKE_SPECS,
}


def _make_property_from_spec(
    spec: _PropSpec,
    property_depth: int,
) -> Property:
    """Create a Property instance from a ``_PropSpec``."""
    no_value = spec.pvt == PropertyValueType.NO_VALUE
    prop = Property(
        animated=False,
        color=spec.color,
        dimensions_separated=False,
        dimensions=spec.dimensions,
        enabled=True,
        expression_enabled=False,
        expression="",
        integer=False,
        is_spatial=spec.is_spatial,
        keyframes=[],
        locked_ratio=False,
        match_name=spec.match_name,
        name=spec.name,
        no_value=no_value,
        property_control_type=PropertyControlType.UNKNOWN,
        property_depth=property_depth,
        property_value_type=spec.pvt,
        units_text=_UNITS_TEXT_MAP.get(spec.match_name, ""),
        value=spec.value,
        vector=spec.dimensions > 1,
    )
    prop.default_value = (
        spec.value if spec.default_value is _USE_VALUE else spec.default_value
    )
    if spec.min_value is not None:
        prop.min_value = spec.min_value
    if spec.max_value is not None:
        prop.max_value = spec.max_value
    return prop


def _synthesize_group_children(group: PropertyGroup) -> None:
    """Synthesize missing children in a standard property group.

    Checks if *group* has a known set of canonical children (Material Options,
    Geometry, Plane, Audio, or Layer Styles sub-groups) and creates any that
    are missing from the binary.  Existing properties are preserved in their
    canonical order.

    Args:
        group: The property group to fill out.
    """
    specs = _GROUP_CHILD_SPECS.get(group.match_name)
    if specs is not None:
        _fill_group(group, specs)
        return

    # Compositing Options (inside each effect): Masks, Effect Opacity, GPU.
    if group.match_name == "ADBE Effect Built In Params":
        _fill_compositing_options(group)
        return

    # Mask atoms: synthesize missing Mask Feather, Opacity, Expansion.
    if group.match_name == "ADBE Mask Atom":
        _fill_mask_atom(group)
        return

    # Layer Styles top-level: fill Blending Options and each style sub-group.
    if group.match_name == "ADBE Layer Styles":
        for child in group.properties:
            if not isinstance(child, PropertyGroup):
                continue
            if child.match_name == "ADBE Blend Options Group":
                _fill_blend_options(child)
            else:
                child_specs = _LAYER_STYLE_CHILD_SPECS.get(child.match_name)
                if child_specs is not None:
                    _fill_group(child, child_specs)

    # Recurse into other groups that may contain known sub-groups.
    for child in group.properties:
        if isinstance(child, PropertyGroup):
            _synthesize_group_children(child)


def _fill_group(
    group: PropertyGroup,
    specs: list[_PropSpec],
) -> None:
    """Fill missing children of *group* using *specs* in canonical order."""
    existing: dict[str, Property | PropertyGroup] = {}
    for child in group.properties:
        existing[child.match_name] = child

    child_depth = group.property_depth + 1
    ordered: list[Property | PropertyGroup] = []
    for spec in specs:
        if spec.match_name in existing:
            ordered.append(existing[spec.match_name])
        else:
            prop = _make_property_from_spec(spec, child_depth)
            prop.parent_property = group
            ordered.append(prop)

    group.properties = ordered  # type: ignore[assignment]


def _fill_blend_options(group: PropertyGroup) -> None:
    """Fill Blending Options: 2 global-angle properties + Advanced Blending."""
    existing: dict[str, Property | PropertyGroup] = {}
    for child in group.properties:
        existing[child.match_name] = child

    child_depth = group.property_depth + 1
    ordered: list[Property | PropertyGroup] = []

    # Global Light Angle, Global Light Altitude
    for spec in _BLEND_OPTIONS_GLOBAL_SPECS:
        if spec.match_name in existing:
            ordered.append(existing[spec.match_name])
        else:
            prop = _make_property_from_spec(spec, child_depth)
            prop.parent_property = group
            ordered.append(prop)

    # Advanced Blending sub-group
    adv_mn = "ADBE Adv Blend Group"
    if adv_mn in existing:
        adv_group = existing[adv_mn]
        ordered.append(adv_group)
    else:
        adv_group = PropertyGroup(
            enabled=True,
            match_name=adv_mn,
            name="Advanced Blending",
            property_depth=child_depth,
            properties=[],
        )
        adv_group.parent_property = group
        ordered.append(adv_group)

    # Fill Advanced Blending children
    if isinstance(adv_group, PropertyGroup):
        _fill_group(adv_group, _ADV_BLEND_SPECS)

    group.properties = ordered  # type: ignore[assignment]


def _fill_compositing_options(group: PropertyGroup) -> None:
    """Fill Compositing Options: Masks, Effect Opacity, GPU Rendering.

    ExtendScript always exposes these three children under
    "ADBE Effect Built In Params", even when the binary stores nothing.
    The Masks child is an indexed group (not a Property).

    Args:
        group: The Compositing Options group to fill.
    """
    existing: dict[str, Property | PropertyGroup] = {}
    for child in group.properties:
        existing[child.match_name] = child

    child_depth = group.property_depth + 1
    ordered: list[Property | PropertyGroup] = []

    # Masks indexed group
    masks_mn = "ADBE Effect Mask Parade"
    if masks_mn in existing:
        ordered.append(existing[masks_mn])
    else:
        masks_group = PropertyGroup(
            enabled=True,
            match_name=masks_mn,
            name="Masks",
            property_depth=child_depth,
            properties=[],
        )
        masks_group.property_type = PropertyType.INDEXED_GROUP
        masks_group.elided = True
        masks_group.parent_property = group
        ordered.append(masks_group)

    # Effect Opacity & GPU Rendering
    for spec in _COMPOSITING_OPTIONS_PROPERTY_SPECS:
        if spec.match_name in existing:
            ordered.append(existing[spec.match_name])
        else:
            prop = _make_property_from_spec(spec, child_depth)
            prop.parent_property = group
            ordered.append(prop)

    group.properties = ordered  # type: ignore[assignment]


def _fill_mask_atom(group: PropertyGroup) -> None:
    """Fill missing children of a mask atom in canonical order.

    ExtendScript always exposes four children per mask: Mask Path, Mask
    Feather, Mask Opacity, and Mask Expansion.  Mask Path must already
    exist (it carries shape data).  The remaining three are synthesized
    when absent.

    Also sets ``default_value`` on existing binary-parsed mask properties
    so that ``is_modified`` works correctly.

    Args:
        group: The mask atom group to fill.
    """
    existing: dict[str, Property | PropertyGroup] = {}
    for child in group.properties:
        existing[child.match_name] = child

    # Build a quick lookup of spec defaults for binary-parsed properties.
    spec_defaults: dict[str, Any] = {s.match_name: s.value for s in _MASK_ATOM_SPECS}

    # Set default_value on existing mask properties parsed from binary.
    for child in group.properties:
        if isinstance(child, Property) and child.default_value is None:
            default = spec_defaults.get(child.match_name)
            if default is not None:
                child.default_value = default

    child_depth = group.property_depth + 1
    ordered: list[Property | PropertyGroup] = []

    # Mask Path must already be parsed from binary
    mask_path_mn = "ADBE Mask Shape"
    if mask_path_mn in existing:
        ordered.append(existing[mask_path_mn])

    # Mask Feather, Mask Opacity, Mask Expansion
    for spec in _MASK_ATOM_SPECS:
        if spec.match_name in existing:
            ordered.append(existing[spec.match_name])
        else:
            prop = _make_property_from_spec(spec, child_depth)
            prop.parent_property = group
            ordered.append(prop)

    group.properties = ordered  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Canonical order of top-level property groups on an AV layer.
# ---------------------------------------------------------------------------
_TOP_LEVEL_GROUP_ORDER: list[tuple[str, str]] = [
    ("ADBE Time Remapping", "Time Remap"),
    ("ADBE MTrackers", "Motion Trackers"),
    ("ADBE Mask Parade", "Masks"),
    ("ADBE Effect Parade", "Effects"),
    ("ADBE Transform Group", "Transform"),
    ("ADBE Layer Styles", "Layer Styles"),
    ("ADBE Plane Options Group", "Geometry Options"),
    ("ADBE Extrsn Options Group", "Geometry Options"),
    ("ADBE Material Options Group", "Material Options"),
    ("ADBE Audio Group", "Audio"),
    ("ADBE Data Group", "Data"),
    ("ADBE Layer Overrides", "Essential Properties"),
    ("ADBE Layer Sets", "Sets"),
    ("ADBE Source Options Group", "Replace Source"),
]


def _synthesize_missing_top_level_groups(layer: Layer) -> None:
    """Add missing top-level property groups expected by ExtendScript.

    ExtendScript always reports a fixed set of top-level property groups
    on every AV layer, even when most are empty.  The binary only stores
    groups that contain data.  This function synthesizes the missing empty
    groups and reorders all groups to match the canonical ExtendScript order.

    Args:
        layer: The layer whose property list should be filled out.
    """
    if not isinstance(layer, AVLayer):
        return

    existing: dict[str, Property | PropertyGroup] = {}
    for child in layer.properties:
        existing[child.match_name] = child

    ordered: list[Property | PropertyGroup] = []
    for match_name, name in _TOP_LEVEL_GROUP_ORDER:
        if match_name in existing:
            ordered.append(existing[match_name])
        else:
            group = PropertyGroup(
                enabled=True,
                match_name=match_name,
                name=name,
                property_depth=1,
                properties=[],
            )
            if match_name == "ADBE Layer Sets":
                group.elided = True
            group.parent_property = layer
            ordered.append(group)

    # Append any remaining properties not in the canonical list (e.g.
    # custom property groups) in their original order.
    canonical_mns = {mn for mn, _ in _TOP_LEVEL_GROUP_ORDER}
    for child in layer.properties:
        if child.match_name not in canonical_mns:
            ordered.append(child)

    # Ensure all top-level groups have the canonical depth of 1.
    for child in ordered:
        if isinstance(child, PropertyGroup) and child.match_name in canonical_mns:
            child.property_depth = 1

    layer.properties = ordered  # type: ignore[assignment]
