"""Property default / synthesis helpers.

This module contains all the logic for:

* Setting `default_value` on transform properties parsed from the binary.
* Synthesizing missing transform properties (AE always exposes twelve).
* Synthesizing missing children in standard property groups
  (Material Options, Geometry Options, Layer Styles, Mask atoms, etc.).
* Setting `min_value` / `max_value` on properties with known bounds.
* Reordering top-level layer groups to match the canonical ExtendScript order.

The two public entry points are:

* [set_transform_defaults][] - called once per layer to fill transform.
* [set_layer_property_defaults][] - called once per layer for everything else.
"""

from __future__ import annotations

from typing import Any

from ..enums import (
    PropertyControlType,
    PropertyType,
    PropertyValueType,
)
from ..kaitai.proxy import ProxyBody
from ..models.layers.av_layer import AVLayer
from ..models.layers.camera_layer import CameraLayer
from ..models.layers.layer import Layer
from ..models.layers.light_layer import LightLayer
from ..models.layers.shape_layer import ShapeLayer
from ..models.layers.text_layer import TextLayer
from ..models.properties.property import Property
from ..models.properties.property_group import PropertyGroup
from ..models.properties.specs import (
    _REGULAR_AV_ONLY_GROUPS,
    _SHAPE_ONLY_GROUPS,
    _TEXT_ONLY_GROUPS,
    _TOP_LEVEL_GROUP_ORDER,
    _TOP_LEVEL_LEAF_PROPERTIES,
    _TRANSFORM_FIXED_DEFAULTS,
    _TRANSFORM_SPECS,
)


def set_transform_defaults(layer: Layer) -> None:
    """Assign defaults and synthesize missing transform properties.

    After Effects always exposes twelve transform properties via ExtendScript
    regardless of whether the layer is 2-D or 3-D.  The binary format, however,
    only stores properties relevant to the current layer state.  This function:

    1. Sets `default_value` on every transform property already parsed from
       the binary so that `Property.is_modified` works correctly.
    2. Creates `Property` objects for any of the twelve canonical properties
       that are absent from the binary.
    3. Re-orders `transform.properties` to match the canonical ExtendScript
       order.

    Spatial defaults (Anchor Point, Position, and the X / Y separated followers)
    depend on layer dimensions and are computed here; all other defaults are
    fixed constants defined in `_TRANSFORM_FIXED_DEFAULTS`.
    """
    transform = layer.transform
    if transform is None:
        return

    # Anchor Point is relative to the layer itself (source dimensions),
    # while Position is relative to the containing composition.
    comp_w = layer.containing_comp.width
    comp_h = layer.containing_comp.height
    if isinstance(layer, AVLayer):
        if isinstance(layer, (TextLayer, ShapeLayer)) or layer.null_layer:
            # Source-less AVLayers: anchor defaults to origin
            anchor_w = 0
            anchor_h = 0
        else:
            anchor_w = layer.width
            anchor_h = layer.height
    else:
        anchor_w = comp_w
        anchor_h = comp_h

    # Spatial defaults depend on layer dimensions.
    spatial_defaults: dict[str, Any] = {
        "ADBE Anchor Point": [anchor_w / 2.0, anchor_h / 2.0, 0.0],
        "ADBE Position": [comp_w / 2.0, comp_h / 2.0, 0.0],
        "ADBE Position_0": comp_w / 2.0,
        "ADBE Position_1": comp_h / 2.0,
    }

    # --- Phase 1: set default_value on properties parsed from binary --------
    existing: dict[str, Property] = {}
    for prop in transform.properties:
        if isinstance(prop, Property):
            existing[prop.match_name] = prop
            # Pad 2D Scale to 3D with Z=100 (ExtendScript always reports 3D)
            if (
                prop.match_name == "ADBE Scale"
                and isinstance(prop._value, list)
                and len(prop._value) == 2
            ):
                prop._value = prop._value + [1.0]
                # Avoid mutating chunk fields
                prop.__dict__["dimensions"] = 3
                prop.__dict__["property_value_type"] = PropertyValueType.ThreeD
                for kf in prop.keyframes:
                    raw = kf._extract_raw_value()
                    if isinstance(raw, list) and len(raw) == 2:
                        kf._value = raw + [1.0]
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
            prop = Property.from_spec(spec, 2, value=value, default_value=default)
            prop.parent_property = transform
            ordered.append(prop)

    transform.properties = ordered  # type: ignore[assignment]

    # --- Phase 3: context-dependent naming ----------------------------------
    # ExtendScript displays "ADBE Rotate Z" as "Rotation" on 2-D layers
    # and "Z Rotation" on 3-D layers.  Camera and Light layers are always 3-D.
    is_3d = isinstance(layer, (CameraLayer, LightLayer)) or (
        isinstance(layer, AVLayer) and layer.three_d_layer
    )
    if not is_3d:
        rotate_z = existing.get("ADBE Rotate Z")
        if rotate_z is None:
            for p in ordered:
                if p.match_name == "ADBE Rotate Z":
                    rotate_z = p
                    break
        if rotate_z is not None:
            rotate_z._auto_name = "Rotation"

        # ExtendScript always reports Scale Z = 100 for 2-D layers,
        # regardless of the binary value.
        scale_prop = existing.get("ADBE Scale")
        if scale_prop is None:
            for p in ordered:
                if p.match_name == "ADBE Scale":
                    scale_prop = p
                    break
        if scale_prop is not None:
            # For parsed properties (cdat path), _resolve_value applies
            # the override; for synthesized properties (_value path),
            # fix the user-facing value directly.
            scale_prop._scale_z_override = 100.0
            if isinstance(scale_prop._value, list) and len(scale_prop._value) >= 3:
                scale_prop._value[2] = 100.0
            for kf in scale_prop.keyframes:
                raw = kf._extract_raw_value()
                if isinstance(raw, list) and len(raw) >= 3:
                    kf._value = raw
                    kf._value[2] = 1.0

    # Camera and Light layers show "Point of Interest" instead of
    # "Anchor Point" in the Transform group.
    if isinstance(layer, (CameraLayer, LightLayer)):
        anchor = existing.get("ADBE Anchor Point")
        if anchor is None:
            for p in ordered:
                if p.match_name == "ADBE Anchor Point":
                    anchor = p
                    break
        if anchor is not None:
            anchor._auto_name = "Point of Interest"

    # --- Phase 4: set min/max on transform properties -----------------------
    transform._apply_min_max_bounds()


def _derive_layer_styles_enabled(layer: Layer) -> None:
    """Derive `enabled` for the Layer Styles group and Blend Options.

    ExtendScript reports the Layer Styles group as `enabled=False` when
    no individual style (Drop Shadow, Inner Glow, etc.) is enabled.
    Blend Options mirrors the Layer Styles group's enabled state.
    The binary stores `enabled=True` for both regardless.

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
        # Avoid mutating chunk fields
        group.__dict__["enabled"] = any_style_enabled
        # Blend Options mirrors the Layer Styles group enabled state
        for child in group.properties:
            if (
                isinstance(child, PropertyGroup)
                and child.match_name == "ADBE Blend Options Group"
            ):
                # Avoid mutating chunk fields
                child.__dict__["enabled"] = any_style_enabled
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
            group._synthesize_children()
            group._apply_min_max_bounds()

    # --- Derive Layer Styles enabled from children -------------------------
    # ExtendScript reports the Layer Styles group and Blend Options as
    # enabled=False when no individual style is enabled, even though the
    # binary stores enabled=True at the group level.
    _derive_layer_styles_enabled(layer)


# ---------------------------------------------------------------------------
# Canonical order of top-level property groups on an AV layer.
# ---------------------------------------------------------------------------


def _synthesize_missing_top_level_groups(layer: Layer) -> None:
    """Add missing top-level property groups expected by ExtendScript.

    ExtendScript always reports a fixed set of top-level property groups
    on every AV layer, even when most are empty.  The binary only stores
    groups that contain data.  This function synthesizes the missing empty
    groups and reorders all groups to match the canonical ExtendScript order.

    Args:
        layer: The layer whose property list should be filled out.
    """
    if isinstance(layer, (CameraLayer, LightLayer)):
        # Light/Camera layers only need Marker synthesized; all other
        # AVLayer-specific groups are irrelevant.
        skip_groups = frozenset(
            mn for mn, _ in _TOP_LEVEL_GROUP_ORDER if mn != "ADBE Marker"
        )
    elif not isinstance(layer, AVLayer):
        return
    elif isinstance(layer, TextLayer):
        skip_groups = _REGULAR_AV_ONLY_GROUPS | _SHAPE_ONLY_GROUPS
    elif isinstance(layer, ShapeLayer):
        skip_groups = _REGULAR_AV_ONLY_GROUPS | _TEXT_ONLY_GROUPS
    else:
        skip_groups = _TEXT_ONLY_GROUPS | _SHAPE_ONLY_GROUPS

    existing: dict[str, Property | PropertyGroup] = {}
    for child in layer.properties:
        existing[child.match_name] = child

    ordered: list[Property | PropertyGroup] = []
    for match_name, name in _TOP_LEVEL_GROUP_ORDER:
        if match_name in existing:
            existing[match_name]._auto_name = name
            if match_name == "ADBE Layer Sets":
                existing[match_name].elided = True
            ordered.append(existing[match_name])
        elif match_name in skip_groups:
            continue
        elif match_name in _TOP_LEVEL_LEAF_PROPERTIES:
            prop = Property(
                _tdsb=ProxyBody(
                    enabled=1,
                    locked_ratio=0,
                    roto_bezier=0,
                    dimensions_separated=0,
                ),
                _tdb4=ProxyBody(
                    dimensions=0,
                    is_spatial=0,
                    animated=0,
                    color=0,
                    integer=0,
                    no_value=0,
                    vector=0,
                    can_vary_over_time=1,
                    expression_enabled=0,
                ),
                match_name=match_name,
                auto_name=name,
                property_depth=1,
                keyframes=[],
                property_control_type=PropertyControlType.UNKNOWN,
                property_value_type=_TOP_LEVEL_LEAF_PROPERTIES[match_name],
                value=None,
                units_text="",
            )
            prop.property_type = PropertyType.PROPERTY
            prop.parent_property = layer
            ordered.append(prop)
        else:
            group = PropertyGroup(
                _tdsb=ProxyBody(
                    enabled=1,
                    locked_ratio=0,
                    roto_bezier=0,
                    dimensions_separated=0,
                ),
                match_name=match_name,
                auto_name=name,
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
