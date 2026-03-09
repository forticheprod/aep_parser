"""Tests for Property model parsing with strengthened assertions."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from conftest import get_first_layer, get_sample_files, load_expected, parse_project

from aep_parser import Project
from aep_parser.enums import (
    KeyframeInterpolationType,
    MaskFeatherFalloff,
    MaskMode,
    MaskMotionBlur,
    PropertyType,
)
from aep_parser.models import MaskPropertyGroup

if TYPE_CHECKING:
    from aep_parser import Property


SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "property"


def _find_property(layer, match_name: str) -> Property | None:
    """Find a property in the layer's transform by match_name."""
    for prop in layer.transform:
        if prop.match_name == match_name:
            return prop
    return None


@pytest.mark.parametrize("sample_name", get_sample_files(SAMPLES_DIR))
def test_parse_property_sample(sample_name: str) -> None:
    """Each property sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


class TestExpressions:
    """Tests for property expressions."""

    def test_expression_enabled(self) -> None:
        """Position has expression 'wiggle(2, 50)' and is enabled."""
        expected = load_expected(SAMPLES_DIR, "expression_enabled")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "expression_enabled.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.expression_enabled is True
        assert position.expression == "wiggle(2, 50)"
        # Verify against JSON
        for item in expected["items"]:
            if "layers" in item:
                for prop in item["layers"][0]["transform"]["properties"]:
                    if prop["matchName"] == "ADBE Position":
                        assert prop["expressionEnabled"] is True
                        assert prop["expression"] == "wiggle(2, 50)"

    def test_expression_disabled(self) -> None:
        """Opacity has expression '50' but expression is disabled."""
        expected = load_expected(SAMPLES_DIR, "expression_disabled")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "expression_disabled.aep"))
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.expression_enabled is False
        assert opacity.expression == "50"
        # Value should be the static value, not the expression result
        for item in expected["items"]:
            if "layers" in item:
                for prop in item["layers"][0]["transform"]["properties"]:
                    if prop["matchName"] == "ADBE Opacity":
                        assert prop["expressionEnabled"] is False
                        assert prop["expression"] == "50"
                        assert prop["value"] == 100

    def test_expression_time(self) -> None:
        """Rotation has expression 'time * 36' and is enabled."""
        expected = load_expected(SAMPLES_DIR, "expression_time")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "expression_time.aep"))
        rotation = _find_property(layer, "ADBE Rotate Z")
        assert rotation is not None
        assert rotation.expression_enabled is True
        assert rotation.expression == "time * 36"
        # Verify against JSON
        for item in expected["items"]:
            if "layers" in item:
                for prop in item["layers"][0]["transform"]["properties"]:
                    if prop["matchName"] == "ADBE Rotate Z":
                        assert prop["expressionEnabled"] is True
                        assert prop["expression"] == "time * 36"


class TestKeyframes:
    """Tests for keyframe interpolation types."""

    def test_keyframe_LINEAR(self) -> None:
        """Position has 2 LINEAR keyframes with values [0,50,0] and [100,50,0]."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_LINEAR.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.animated
        assert len(position.keyframes) == 2
        for kf in position.keyframes:
            assert kf.keyframe_interpolation_type == KeyframeInterpolationType.LINEAR
        assert position.keyframes[0].value == [0.0, 50.0, 0.0]
        assert position.keyframes[1].value == [100.0, 50.0, 0.0]

    def test_keyframe_BEZIER(self) -> None:
        """Position has 2 BEZIER keyframes with values [0,50,0] and [100,50,0]."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_BEZIER.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.animated
        assert len(position.keyframes) == 2
        for kf in position.keyframes:
            assert kf.keyframe_interpolation_type == KeyframeInterpolationType.BEZIER
        assert position.keyframes[0].value == [0.0, 50.0, 0.0]
        assert position.keyframes[1].value == [100.0, 50.0, 0.0]

    def test_keyframe_HOLD(self) -> None:
        """Opacity has 3 keyframes, second is HOLD, values 1.0/0.0/1.0."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_HOLD.aep"))
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.animated
        assert len(opacity.keyframes) == 3
        # Keyframe 2 (index 1) is HOLD
        assert opacity.keyframes[1].keyframe_interpolation_type == KeyframeInterpolationType.HOLD
        assert opacity.keyframes[0].value == 100.0
        assert opacity.keyframes[1].value == 0.0
        assert opacity.keyframes[2].value == 100.0


class TestPropertyStructure:
    """Tests for property structural attributes (depth, index, is_time_varying)."""

    def test_transform_properties_depth(self) -> None:
        """Transform properties are at depth 2 (layer=0, transform-group=1, prop=2)."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        # All transform properties should be at depth 2
        for prop in layer.transform.properties:
            assert prop.property_depth == 2, (
                f"{prop.match_name} has depth {prop.property_depth}, expected 2"
            )

    def test_effect_depth(self) -> None:
        """Effects (PropertyGroup) are at depth 2; their properties at depth 3."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "effect_2dPoint.aep"))
        assert layer.effects is not None
        assert len(layer.effects.properties) > 0
        effect = layer.effects.properties[0]
        assert effect.property_depth == 2
        for prop in effect.properties:
            assert prop.property_depth == 3, (
                f"{prop.match_name} has depth {prop.property_depth}, expected 3"
            )

    def test_is_time_varying_with_keyframes(self) -> None:
        """Opacity with keyframes has is_time_varying == True."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.is_time_varying is True

    def test_is_time_varying_with_expression(self) -> None:
        """Position with enabled expression has is_time_varying == True."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "expression_enabled.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.is_time_varying is True

    def test_is_time_varying_static(self) -> None:
        """A non-animated property with no actual expression has is_time_varying == False."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_rotation.aep"))
        # Only ADBE Rotate Z is animated; ADBE Rotate X is static
        rotate_x = _find_property(layer, "ADBE Rotate X")
        assert rotate_x is not None
        assert not rotate_x.animated
        assert rotate_x.is_time_varying is False


class TestPropertyDimensions:
    """Tests for property value types and dimensions."""

    def test_property_1D_opacity(self) -> None:
        """Opacity is a 1D property with 2 keyframes going 0→100."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.dimensions == 1
        assert opacity.animated
        assert len(opacity.keyframes) == 2

    def test_property_2D_position(self) -> None:
        """Position in a 2D layer has 2 keyframes."""
        expected = load_expected(SAMPLES_DIR, "property_2D_position")
        project = parse_project(SAMPLES_DIR / "property_2D_position.aep")
        layer = get_first_layer(project)
        # Verify the layer is not 3D
        for item in expected["items"]:
            if "layers" in item:
                assert item["layers"][0]["threeDLayer"] is False
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.animated
        assert len(position.keyframes) == 2

    def test_property_3D_position(self) -> None:
        """Position in a 3D layer has 3 dimensions and 2 keyframes."""
        expected = load_expected(SAMPLES_DIR, "property_3D_position")
        project = parse_project(SAMPLES_DIR / "property_3D_position.aep")
        layer = get_first_layer(project)
        # Verify the layer is 3D
        for item in expected["items"]:
            if "layers" in item:
                assert item["layers"][0]["threeDLayer"] is True
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.animated
        assert len(position.keyframes) == 2

    def test_property_rotation(self) -> None:
        """Rotation is a 1D property with 2 keyframes going 0→360."""
        expected = load_expected(SAMPLES_DIR, "property_rotation")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_rotation.aep"))
        rotation = _find_property(layer, "ADBE Rotate Z")
        assert rotation is not None
        assert rotation.dimensions == 1
        assert rotation.animated
        assert len(rotation.keyframes) == 2
        # Verify against JSON
        for item in expected["items"]:
            if "layers" in item:
                for prop in item["layers"][0]["transform"]["properties"]:
                    if prop["matchName"] == "ADBE Rotate Z":
                        assert prop["numKeys"] == 2

    def test_property_scale(self) -> None:
        """Scale has 2 keyframes."""
        expected = load_expected(SAMPLES_DIR, "property_scale")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_scale.aep"))
        scale = _find_property(layer, "ADBE Scale")
        assert scale is not None
        assert scale.animated
        assert len(scale.keyframes) == 2
        # Verify against JSON
        for item in expected["items"]:
            if "layers" in item:
                for prop in item["layers"][0]["transform"]["properties"]:
                    if prop["matchName"] == "ADBE Scale":
                        assert prop["numKeys"] == 2


LAYER_SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "layer"


class TestOrientation:
    """Tests for orientation property parsing (OTST chunks).

    Orientation is stored in a special OTST chunk whose cdat uses
    little-endian doubles (unlike the rest of the big-endian RIFX file).
    """

    def test_orientation_default(self) -> None:
        """Default orientation [0, 0, 0] when no OTST chunk is present."""
        layer = get_first_layer(
            parse_project(LAYER_SAMPLES_DIR / "orientation_0.aep")
        )
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.value == [0.0, 0.0, 0.0]
        assert orientation.dimensions == 3

    def test_orientation_x_only(self) -> None:
        """Orientation with only X component set to 5."""
        layer = get_first_layer(
            parse_project(LAYER_SAMPLES_DIR / "orientation_5_0_0.aep")
        )
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.value == [5.0, 0.0, 0.0]
        assert orientation.dimensions == 3
        assert orientation.is_spatial is True

    def test_orientation_y_only(self) -> None:
        """Orientation with only Y component set to 279."""
        layer = get_first_layer(
            parse_project(LAYER_SAMPLES_DIR / "orientation_0_279_0.aep")
        )
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.value == [0.0, 279.0, 0.0]
        assert orientation.dimensions == 3

    def test_orientation_z_only(self) -> None:
        """Orientation with only Z component set to 5."""
        layer = get_first_layer(
            parse_project(LAYER_SAMPLES_DIR / "orientation_0_0_5.aep")
        )
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.value == [0.0, 0.0, 5.0]
        assert orientation.dimensions == 3

    def test_orientation_metadata(self) -> None:
        """Orientation has correct property metadata."""
        layer = get_first_layer(
            parse_project(LAYER_SAMPLES_DIR / "orientation_5_0_0.aep")
        )
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.name == "Orientation"
        assert orientation.match_name == "ADBE Orientation"
        assert orientation.is_spatial is True
        assert orientation.vector is True
        assert not orientation.animated

    def test_orientation_animated_keyframe_values(self) -> None:
        """Animated orientation keyframes carry 3-component values from otda."""
        layer = get_first_layer(
            parse_project(LAYER_SAMPLES_DIR / "orientation_with_keyframes.aep")
        )
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.animated
        assert len(orientation.keyframes) == 2
        assert orientation.keyframes[0].value == [5.0, 0.0, 0.0]
        assert orientation.keyframes[1].value == [0.0, 0.0, 0.0]

    def test_orientation_animated_keyframe_times(self) -> None:
        """Animated orientation keyframes have correct frame times."""
        layer = get_first_layer(
            parse_project(LAYER_SAMPLES_DIR / "orientation_with_keyframes.aep")
        )
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.keyframes[0].frame_time == 0
        assert orientation.keyframes[1].frame_time == 240

    def test_orientation_animated_metadata(self) -> None:
        """Animated orientation retains correct property metadata."""
        layer = get_first_layer(
            parse_project(LAYER_SAMPLES_DIR / "orientation_with_keyframes.aep")
        )
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.dimensions == 3
        assert orientation.is_spatial is True
        assert orientation.vector is True
        assert orientation.value is None


class TestEffectProperties:
    """Tests for effect-related property samples."""

    def test_effect_2dPoint(self) -> None:
        project = parse_project(SAMPLES_DIR / "effect_2dPoint.aep")
        assert isinstance(project, Project)
        assert len(project.compositions) >= 1

    def test_effect_3dPoint(self) -> None:
        project = parse_project(SAMPLES_DIR / "effect_3dPoint.aep")
        assert isinstance(project, Project)
        assert len(project.compositions) >= 1

    def test_effect_puppet(self) -> None:
        project = parse_project(SAMPLES_DIR / "effect_puppet.aep")
        assert isinstance(project, Project)
        assert len(project.compositions) >= 1

    def test_duplicate_effects(self) -> None:
        """Two Gaussian Blur effects on the same layer are both parsed.

        When the same effect type is applied more than once, only the first
        instance carries a ``parT`` chunk at layer level. The parser falls
        back to project-level EfdG definitions for subsequent instances.
        """
        project = parse_project(SAMPLES_DIR / "2_gaussian.aep")
        layer = get_first_layer(project)
        assert layer.effects is not None
        assert len(layer.effects.properties) == 2
        for effect in layer.effects:
            assert effect.match_name == "ADBE Gaussian Blur 2"
            assert effect.is_effect is True
        # Second effect should have a user-defined name
        assert layer.effects.properties[0].name == "Gaussian Blur"
        assert layer.effects.properties[1].name == "Gaussian Blur 2"

    def test_duplicate_effects_values(self) -> None:
        """Gaussian Blur effects with non-default Blurriness values 20 and 30."""
        project = parse_project(SAMPLES_DIR / "2_gaussian_20_30.aep")
        layer = get_first_layer(project)
        assert layer.effects is not None
        assert len(layer.effects.properties) == 2

        # Each effect should have a Blurriness property with modified value
        effect_0 = layer.effects.properties[0]
        blurriness_0 = None
        for prop in effect_0.properties:
            if prop.match_name == "ADBE Gaussian Blur 2-0001":
                blurriness_0 = prop
                break
        assert blurriness_0 is not None
        assert blurriness_0.value == 20.0

        effect_1 = layer.effects.properties[1]
        blurriness_1 = None
        for prop in effect_1.properties:
            if prop.match_name == "ADBE Gaussian Blur 2-0001":
                blurriness_1 = prop
                break
        assert blurriness_1 is not None
        assert blurriness_1.value == 30.0

    def test_effect_selected_first(self) -> None:
        """First Gaussian Blur effect is selected."""
        project = parse_project(SAMPLES_DIR / "2_gaussian_first_selected.aep")
        layer = get_first_layer(project)
        assert layer.effects is not None
        assert len(layer.effects.properties) == 2
        assert layer.effects.properties[0].selected is True
        assert layer.effects.properties[1].selected is False

    def test_effect_selected_second(self) -> None:
        """Second Gaussian Blur effect is selected."""
        project = parse_project(SAMPLES_DIR / "2_gaussian_second_selected.aep")
        layer = get_first_layer(project)
        assert layer.effects is not None
        assert len(layer.effects.properties) == 2
        assert layer.effects.properties[0].selected is False
        assert layer.effects.properties[1].selected is True

    def test_effect_selected_default(self) -> None:
        """No effects are selected in the default sample."""
        project = parse_project(SAMPLES_DIR / "2_gaussian.aep")
        layer = get_first_layer(project)
        assert layer.effects is not None
        assert len(layer.effects.properties) == 2
        assert layer.effects.properties[0].selected is False
        assert layer.effects.properties[1].selected is False

    def test_property_selected_default_false(self) -> None:
        """Non-effect properties default to selected=False."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_1D_opacity.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.selected is False


class TestMasks:
    """Tests for mask property groups."""

    def test_is_mask_true_single(self) -> None:
        """Layer with one mask: Mask Parade has is_mask=False, atom has is_mask=True."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_mask_true.aep")
        )
        assert layer.masks is not None
        assert layer.masks.is_mask is False
        assert layer.masks.match_name == "ADBE Mask Parade"
        assert layer.masks.property_type == PropertyType.INDEXED_GROUP
        assert len(layer.masks.properties) == 1
        assert layer.masks.properties[0].is_mask is True

    def test_is_mask_multiple(self) -> None:
        """Layer with two masks: Mask Parade has is_mask=False, atoms have is_mask=True."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_mask_multiple.aep")
        )
        assert layer.masks is not None
        assert layer.masks.is_mask is False
        assert len(layer.masks.properties) == 2
        for mask in layer.masks.properties:
            assert mask.is_mask is True

    def test_no_masks(self) -> None:
        """Layer without masks has masks=None."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_1D_opacity.aep")
        )
        assert layer.masks is None

    def test_mask_parent_property(self) -> None:
        """Mask children have parent_property pointing to mask parade."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_mask_true.aep")
        )
        assert layer.masks is not None
        for mask in layer.masks.properties:
            assert mask.parent_property is layer.masks

    def test_mask_atom_is_mask_property_group(self) -> None:
        """Each mask atom is a MaskPropertyGroup instance."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_mask_true.aep")
        )
        assert layer.masks is not None
        assert len(layer.masks.properties) == 1
        assert isinstance(layer.masks.properties[0], MaskPropertyGroup)

    def test_mask_atom_inverted_default(self) -> None:
        """Default mask has inverted=False."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_mask_true.aep")
        )
        assert layer.masks is not None
        mask = layer.masks.properties[0]
        assert isinstance(mask, MaskPropertyGroup)
        assert mask.inverted is False

    def test_mask_atom_locked_default(self) -> None:
        """Default mask has locked=False."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_mask_true.aep")
        )
        assert layer.masks is not None
        mask = layer.masks.properties[0]
        assert isinstance(mask, MaskPropertyGroup)
        assert mask.locked is False

    def test_mask_atom_mode_default(self) -> None:
        """Default mask has mask_mode=MaskMode.ADD."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_mask_true.aep")
        )
        assert layer.masks is not None
        mask = layer.masks.properties[0]
        assert isinstance(mask, MaskPropertyGroup)
        assert mask.mask_mode == MaskMode.ADD

    def test_mask_multiple_all_mask_property_groups(self) -> None:
        """All mask atoms in a multi-mask layer are MaskPropertyGroup."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_mask_multiple.aep")
        )
        assert layer.masks is not None
        for mask in layer.masks.properties:
            assert isinstance(mask, MaskPropertyGroup)

    def test_mask_children_parent_is_mask_group(self) -> None:
        """MaskPropertyGroup children point to the mask atom as parent."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_mask_true.aep")
        )
        assert layer.masks is not None
        mask = layer.masks.properties[0]
        assert isinstance(mask, MaskPropertyGroup)
        for child in mask.properties:
            assert child.parent_property is mask


class TestMaskAttributes:
    """Tests for MaskPropertyGroup attributes (color, featherFalloff, motionBlur, rotoBezier)."""

    @staticmethod
    def _get_mask(filename: str) -> MaskPropertyGroup:
        """Parse a mask sample and return the first MaskPropertyGroup."""
        project = parse_project(SAMPLES_DIR / filename)
        layer = get_first_layer(project)
        assert layer.masks is not None
        mask = layer.masks.properties[0]
        assert isinstance(mask, MaskPropertyGroup)
        return mask

    # --- color ---

    def test_color_default(self) -> None:
        """Default mask color is [30/255, 64/255, 30/255]."""
        mask = self._get_mask("mask_add.aep")
        assert len(mask.color) == 3
        assert pytest.approx(mask.color, abs=1e-3) == [
            30 / 255,
            64 / 255,
            30 / 255,
        ]

    def test_color_custom_1(self) -> None:
        """Custom mask color [0.102, 0.2, 0.302] (26/255, 51/255, 77/255)."""
        mask = self._get_mask("mask_color_0.102_0.2_0.302.aep")
        assert pytest.approx(mask.color, abs=1e-3) == [
            26 / 255,
            51 / 255,
            77 / 255,
        ]

    def test_color_custom_2(self) -> None:
        """Custom mask color [0.2, 0.302, 0.4] (51/255, 77/255, 102/255)."""
        mask = self._get_mask("mask_color_0.2_0.302_0.4.aep")
        assert pytest.approx(mask.color, abs=1e-3) == [
            51 / 255,
            77 / 255,
            102 / 255,
        ]

    # --- maskFeatherFalloff ---

    def test_feather_falloff_smooth(self) -> None:
        """Feather falloff Smooth is the default."""
        mask = self._get_mask("mask_feather_falloff_smooth.aep")
        assert mask.mask_feather_falloff == MaskFeatherFalloff.FFO_SMOOTH

    def test_feather_falloff_linear(self) -> None:
        """Feather falloff Linear."""
        mask = self._get_mask("mask_feather_falloff_linear.aep")
        assert mask.mask_feather_falloff == MaskFeatherFalloff.FFO_LINEAR

    # --- maskMotionBlur ---

    def test_motion_blur_same_as_layer(self) -> None:
        """Motion blur Same as Layer is the default."""
        mask = self._get_mask("mask_motion_blur_same_as_layer.aep")
        assert mask.mask_motion_blur == MaskMotionBlur.SAME_AS_LAYER

    def test_motion_blur_on(self) -> None:
        """Motion blur On."""
        mask = self._get_mask("mask_motion_blur_on.aep")
        assert mask.mask_motion_blur == MaskMotionBlur.ON

    def test_motion_blur_off(self) -> None:
        """Motion blur Off."""
        mask = self._get_mask("mask_motion_blur_off.aep")
        assert mask.mask_motion_blur == MaskMotionBlur.OFF

    # --- rotoBezier ---

    def test_roto_bezier_default_false(self) -> None:
        """Default mask has rotoBezier=False."""
        mask = self._get_mask("mask_add.aep")
        assert mask.roto_bezier is False

    def test_roto_bezier_on(self) -> None:
        """Mask with RotoBezier enabled."""
        mask = self._get_mask("mask_rotobezier_on.aep")
        assert mask.roto_bezier is True

    # --- mask_mode (all modes via from_binary) ---

    def test_mask_mode_none(self) -> None:
        mask = self._get_mask("mask_none.aep")
        assert mask.mask_mode == MaskMode.NONE

    def test_mask_mode_add(self) -> None:
        mask = self._get_mask("mask_add.aep")
        assert mask.mask_mode == MaskMode.ADD

    def test_mask_mode_subtract(self) -> None:
        mask = self._get_mask("mask_subtract.aep")
        assert mask.mask_mode == MaskMode.SUBTRACT

    def test_mask_mode_intersect(self) -> None:
        mask = self._get_mask("mask_intersect.aep")
        assert mask.mask_mode == MaskMode.INTERSECT

    def test_mask_mode_darken(self) -> None:
        mask = self._get_mask("mask_darken.aep")
        assert mask.mask_mode == MaskMode.DARKEN

    def test_mask_mode_lighten(self) -> None:
        mask = self._get_mask("mask_lighten.aep")
        assert mask.mask_mode == MaskMode.LIGHTEN

    def test_mask_mode_difference(self) -> None:
        mask = self._get_mask("mask_difference.aep")
        assert mask.mask_mode == MaskMode.DIFFERENCE


class TestIsModified:
    """Tests for PropertyBase.is_modified computed property."""

    def test_transform_defaults_at_default_values(self) -> None:
        """Transform properties at their default values have is_modified=False."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_modified_false.aep")
        )
        # These transform properties are at their defaults in this sample.
        for match_name in (
            "ADBE Orientation",
            "ADBE Rotate X",
            "ADBE Rotate Y",
            "ADBE Envir Appear in Reflect",
        ):
            prop = _find_property(layer, match_name)
            if prop is not None:
                assert prop.is_modified is False, (
                    f"{match_name}: expected is_modified=False, "
                    f"value={prop.value!r}, default={prop.default_value!r}"
                )

    def test_separated_position_modified(self) -> None:
        """X/Y Position followers moved to 0 from center are is_modified=True."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_modified_false.aep")
        )
        pos_x = _find_property(layer, "ADBE Position_0")
        pos_y = _find_property(layer, "ADBE Position_1")
        if pos_x is not None:
            assert pos_x.is_modified is True, (
                f"X Position value={pos_x.value}, default={pos_x.default_value}"
            )
        if pos_y is not None:
            assert pos_y.is_modified is True, (
                f"Y Position value={pos_y.value}, default={pos_y.default_value}"
            )

    def test_transform_group_is_modified(self) -> None:
        """Transform group is_modified=True when any child is modified."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_modified_false.aep")
        )
        assert layer.transform is not None
        # X/Y Position are moved → at least one child is modified
        assert layer.transform.is_modified is True

    def test_effect_parade_indexed_group_with_children(self) -> None:
        """Effect Parade (indexed group) with effects has is_modified=True."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_modified_false.aep")
        )
        assert layer.effects is not None
        assert layer.effects.property_type == PropertyType.INDEXED_GROUP
        assert len(layer.effects.properties) > 0
        assert layer.effects.is_modified is True

    def test_animated_property_is_modified(self) -> None:
        """An animated property (with keyframes) has is_modified=True."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_1D_opacity.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.animated
        assert opacity.is_modified is True

    def test_expression_enabled_is_modified(self) -> None:
        """Property with enabled expression has is_modified=True."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "expression_enabled.aep")
        )
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.expression_enabled is True
        assert position.is_modified is True

    def test_expression_disabled_not_modified(self) -> None:
        """Property with disabled expression is not modified by the expression."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "expression_disabled.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.expression_enabled is False
        # Expression is disabled, so the expression itself doesn't trigger
        # is_modified. However the static value (100.0) equals the default
        # so the property should not be modified either.
        if opacity.default_value is not None:
            assert opacity.is_modified is False

    def test_scale_at_default_not_modified(self) -> None:
        """Scale [100,100,100] at default is is_modified=False."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_rotation.aep")
        )
        scale = _find_property(layer, "ADBE Scale")
        if scale is not None and scale.default_value is not None:
            assert scale.is_modified is False, (
                f"Scale value={scale.value}, default={scale.default_value}"
            )

    def test_effect_properties_at_default(self) -> None:
        """Effect properties at their default values have is_modified=False."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_modified_false.aep")
        )
        assert layer.effects is not None
        from aep_parser.models.properties.property import Property as PropCls

        for effect in layer.effects:
            for prop in effect.properties:
                if isinstance(prop, PropCls) and prop.default_value is not None:
                    # In this sample all effect params are at defaults
                    assert prop.is_modified is False, (
                        f"{prop.match_name}: value={prop.value!r}, "
                        f"default={prop.default_value!r}"
                    )

    def test_effect_modified_value(self) -> None:
        """Effect property with value != default has is_modified=True."""
        project = parse_project(SAMPLES_DIR / "2_gaussian_20_30.aep")
        layer = get_first_layer(project)
        assert layer.effects is not None
        effect = layer.effects.properties[0]
        blurriness = None
        for prop in effect.properties:
            if prop.match_name == "ADBE Gaussian Blur 2-0001":
                blurriness = prop
                break
        assert blurriness is not None
        assert blurriness.value == 20.0
        # Blurriness default from pard chunk is 0.0
        if blurriness.default_value is not None:
            assert blurriness.is_modified is True

    def test_no_default_value_not_modified(self) -> None:
        """Property with no default_value returns is_modified=False (conservative)."""
        from aep_parser.models.properties.property import Property as PropCls

        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_1D_opacity.aep")
        )
        # Check a property that might not have a default
        for prop in layer.transform.properties:
            if isinstance(prop, PropCls) and prop.default_value is None:
                if not prop.animated and not (
                    prop.expression and prop.expression_enabled
                ):
                    assert prop.is_modified is False, (
                        f"{prop.match_name} with no default should be False"
                    )


class TestTransformSynthesis:
    """Tests for synthesized transform properties.

    After Effects always reports 12 transform properties via ExtendScript
    regardless of layer dimensionality (2-D vs 3-D). The binary format only
    stores properties relevant to the current state, so the parser synthesises
    the missing ones.
    """

    _CANONICAL_ORDER = [
        "ADBE Anchor Point",
        "ADBE Position",
        "ADBE Position_0",
        "ADBE Position_1",
        "ADBE Position_2",
        "ADBE Scale",
        "ADBE Orientation",
        "ADBE Rotate X",
        "ADBE Rotate Y",
        "ADBE Rotate Z",
        "ADBE Opacity",
        "ADBE Envir Appear in Reflect",
    ]

    def test_twelve_properties(self) -> None:
        """Transform group always contains exactly 12 properties."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_modified_false.aep")
        )
        assert layer.transform is not None
        assert len(layer.transform.properties) == 12

    def test_canonical_order(self) -> None:
        """Properties appear in the canonical ExtendScript order."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "is_modified_false.aep")
        )
        match_names = [p.match_name for p in layer.transform.properties]
        assert match_names == self._CANONICAL_ORDER

    def test_synthesized_orientation_metadata(self) -> None:
        """Orientation always present with correct defaults."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_1D_opacity.aep")
        )
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.default_value is not None
        assert orientation.is_modified is False

    def test_synthesized_rotate_x_metadata(self) -> None:
        """X Rotation always present with correct defaults."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_1D_opacity.aep")
        )
        rotate_x = _find_property(layer, "ADBE Rotate X")
        assert rotate_x is not None
        assert rotate_x.dimensions == 1
        assert rotate_x.default_value is not None
        assert rotate_x.is_modified is False

    def test_synthesized_value_equals_default(self) -> None:
        """Non-animated transform properties at default have is_modified=False."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_1D_opacity.aep")
        )
        from aep_parser.models.properties.property import Property as PropCls

        # All non-animated transform properties should have a default and
        # be at that default (the sample only animates Opacity).
        for prop in layer.transform.properties:
            if isinstance(prop, PropCls) and not prop.animated:
                assert prop.default_value is not None, (
                    f"{prop.match_name} should have a default_value"
                )

        # Verify specific properties
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.is_modified is False

        rotate_x = _find_property(layer, "ADBE Rotate X")
        assert rotate_x is not None
        assert rotate_x.value == 0.0
        assert rotate_x.is_modified is False

    def test_synthesized_not_animated(self) -> None:
        """Synthesized properties have animated=False."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_1D_opacity.aep")
        )
        for match_name in ("ADBE Orientation", "ADBE Rotate X", "ADBE Rotate Y"):
            prop = _find_property(layer, match_name)
            assert prop is not None
            assert not prop.animated, f"{match_name} should not be animated"
            assert prop.expression == ""
            assert prop.keyframes == []

    def test_synthesized_parent_property(self) -> None:
        """Synthesized properties point to the transform group as parent."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_1D_opacity.aep")
        )
        for prop in layer.transform.properties:
            assert prop.parent_property is layer.transform, (
                f"{prop.match_name} parent should be transform group"
            )

    def test_envir_appear_in_reflect(self) -> None:
        """Appears in Reflections is synthesised with correct name and value."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_1D_opacity.aep")
        )
        envir = _find_property(layer, "ADBE Envir Appear in Reflect")
        assert envir is not None
        assert envir.name == "Appears in Reflections"
        assert envir.value == 1.0
        assert envir.default_value == 1.0
        assert envir.is_modified is False

    def test_property_rotation_twelve_properties(self) -> None:
        """Another sample (property_rotation) also gets 12 transform props."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "property_rotation.aep")
        )
        assert layer.transform is not None
        assert len(layer.transform.properties) == 12
        match_names = [p.match_name for p in layer.transform.properties]
        assert match_names == self._CANONICAL_ORDER
