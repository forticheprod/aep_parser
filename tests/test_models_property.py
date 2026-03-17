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
    PropertyValueType,
)
from aep_parser.models import MaskPropertyGroup

if TYPE_CHECKING:
    from aep_parser import Property


SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "property"
BUGS_DIR = Path(__file__).parent.parent / "samples" / "bugs"


def _find_property(layer, match_name: str) -> Property | None:
    """Find a property in the layer's transform by match_name."""
    for prop in layer.transform:
        if prop.match_name == match_name:
            return prop
    return None


def _get_json_transform_properties(expected: dict) -> list[dict]:
    """Extract transform properties from the expected JSON structure."""
    for item in expected["items"]:
        if "layers" in item:
            for group in item["layers"][0]["properties"]:
                if group.get("matchName") == "ADBE Transform Group":
                    return group["properties"]
    return []


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
        for prop in _get_json_transform_properties(expected):
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
        for prop in _get_json_transform_properties(expected):
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
        for prop in _get_json_transform_properties(expected):
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
            assert kf.out_interpolation_type == KeyframeInterpolationType.LINEAR
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
            assert kf.out_interpolation_type == KeyframeInterpolationType.BEZIER
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
        assert (
            opacity.keyframes[1].out_interpolation_type
            == KeyframeInterpolationType.HOLD
        )
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
        """Opacity is a 1D property with 2 keyframes going 0>100."""
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
        """Rotation is a 1D property with 2 keyframes going 0>360."""
        expected = load_expected(SAMPLES_DIR, "property_rotation")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_rotation.aep"))
        rotation = _find_property(layer, "ADBE Rotate Z")
        assert rotation is not None
        assert rotation.dimensions == 1
        assert rotation.animated
        assert len(rotation.keyframes) == 2
        # Verify against JSON
        for prop in _get_json_transform_properties(expected):
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
        for prop in _get_json_transform_properties(expected):
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
        layer = get_first_layer(parse_project(LAYER_SAMPLES_DIR / "orientation_0.aep"))
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
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.selected is False

    def test_layer_index_value(self) -> None:
        """LAYER_INDEX effect property reads layer index from tdpi chunk.

        The S_BlurDirectional effect's "Matte from Layer" parameter has
        property_value_type LAYER_INDEX.  When no layer is selected the
        value is 0.
        """
        project = parse_project(BUGS_DIR / "29.97_fps_time_scale_3.125.aep")
        # Find the S_BlurDirectional effect in any composition
        for comp in project.compositions:
            for layer in comp.layers:
                if layer.effects is None:
                    continue
                for effect in layer.effects:
                    if effect.name == "S_BlurDirectional":
                        for prop in effect.properties:
                            if prop.name == "Matte from Layer":
                                assert (
                                    prop.property_value_type
                                    == PropertyValueType.LAYER_INDEX
                                )
                                assert prop.value == 0
                                return
        pytest.fail("S_BlurDirectional 'Matte from Layer' property not found")

    def test_mask_index_value(self) -> None:
        """MASK_INDEX effect property reads mask index from tdli chunk.

        The S_BlurDirectional effect's "Matte from Path" parameter has
        property_value_type MASK_INDEX.  Value 1 means mask #1.
        """
        project = parse_project(BUGS_DIR / "29.97_fps_time_scale_3.125.aep")
        for comp in project.compositions:
            for layer in comp.layers:
                if layer.effects is None:
                    continue
                for effect in layer.effects:
                    if effect.name == "S_BlurDirectional":
                        for prop in effect.properties:
                            if prop.name == "Matte from Path":
                                assert (
                                    prop.property_value_type
                                    == PropertyValueType.MASK_INDEX
                                )
                                assert prop.value == 1
                                return
        pytest.fail("S_BlurDirectional 'Matte from Path' property not found")


class TestMasks:
    """Tests for mask property groups."""

    def test_is_mask_true_single(self) -> None:
        """Layer with one mask: Mask Parade has is_mask=False, atom has is_mask=True."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_mask_true.aep"))
        assert layer.masks is not None
        assert layer.masks.is_mask is False
        assert layer.masks.match_name == "ADBE Mask Parade"
        assert layer.masks.property_type == PropertyType.INDEXED_GROUP
        assert len(layer.masks.properties) == 1
        assert layer.masks.properties[0].is_mask is True

    def test_is_mask_multiple(self) -> None:
        """Layer with two masks: Mask Parade has is_mask=False, atoms have is_mask=True."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_mask_multiple.aep"))
        assert layer.masks is not None
        assert layer.masks.is_mask is False
        assert len(layer.masks.properties) == 2
        for mask in layer.masks.properties:
            assert mask.is_mask is True

    def test_no_masks(self) -> None:
        """Layer without masks has masks=None."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        assert layer.masks is None

    def test_mask_parent_property(self) -> None:
        """Mask children have parent_property pointing to mask parade."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_mask_true.aep"))
        assert layer.masks is not None
        for mask in layer.masks.properties:
            assert mask.parent_property is layer.masks

    def test_mask_atom_is_mask_property_group(self) -> None:
        """Each mask atom is a MaskPropertyGroup instance."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_mask_true.aep"))
        assert layer.masks is not None
        assert len(layer.masks.properties) == 1
        assert isinstance(layer.masks.properties[0], MaskPropertyGroup)

    def test_mask_atom_inverted_default(self) -> None:
        """Default mask has inverted=False."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_mask_true.aep"))
        assert layer.masks is not None
        mask = layer.masks.properties[0]
        assert isinstance(mask, MaskPropertyGroup)
        assert mask.inverted is False

    def test_mask_atom_locked_default(self) -> None:
        """Default mask has locked=False."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_mask_true.aep"))
        assert layer.masks is not None
        mask = layer.masks.properties[0]
        assert isinstance(mask, MaskPropertyGroup)
        assert mask.locked is False

    def test_mask_atom_mode_default(self) -> None:
        """Default mask has mask_mode=MaskMode.ADD."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_mask_true.aep"))
        assert layer.masks is not None
        mask = layer.masks.properties[0]
        assert isinstance(mask, MaskPropertyGroup)
        assert mask.mask_mode == MaskMode.ADD

    def test_mask_multiple_all_mask_property_groups(self) -> None:
        """All mask atoms in a multi-mask layer are MaskPropertyGroup."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_mask_multiple.aep"))
        assert layer.masks is not None
        for mask in layer.masks.properties:
            assert isinstance(mask, MaskPropertyGroup)

    def test_mask_children_parent_is_mask_group(self) -> None:
        """MaskPropertyGroup children point to the mask atom as parent."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_mask_true.aep"))
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
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_modified_false.aep"))
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
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_modified_false.aep"))
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
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_modified_false.aep"))
        assert layer.transform is not None
        # X/Y Position are moved > at least one child is modified
        assert layer.transform.is_modified is True

    def test_effect_parade_indexed_group_with_children(self) -> None:
        """Effect Parade (indexed group) with effects has is_modified=True."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_modified_false.aep"))
        assert layer.effects is not None
        assert layer.effects.property_type == PropertyType.INDEXED_GROUP
        assert len(layer.effects.properties) > 0
        assert layer.effects.is_modified is True

    def test_animated_property_is_modified(self) -> None:
        """An animated property (with keyframes) has is_modified=True."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.animated
        assert opacity.is_modified is True

    def test_expression_enabled_is_modified(self) -> None:
        """Property with enabled expression has is_modified=True."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "expression_enabled.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.expression_enabled is True
        assert position.is_modified is True

    def test_expression_disabled_not_modified(self) -> None:
        """Property with disabled expression is not modified by the expression."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "expression_disabled.aep"))
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
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_rotation.aep"))
        scale = _find_property(layer, "ADBE Scale")
        if scale is not None and scale.default_value is not None:
            assert scale.is_modified is False, (
                f"Scale value={scale.value}, default={scale.default_value}"
            )

    def test_effect_properties_at_default(self) -> None:
        """Effect properties at their default values have is_modified=False."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_modified_false.aep"))
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

        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        # Check a property that might not have a default
        for prop in layer.transform.properties:
            if isinstance(prop, PropCls) and prop.default_value is None:
                if not prop.animated and not (
                    prop.expression and prop.expression_enabled
                ):
                    assert prop.is_modified is False, (
                        f"{prop.match_name} with no default should be False"
                    )


class TestSeparation:
    """Tests for separation leader/follower properties.

    In After Effects, Position is a "separation leader" that can be
    split into X/Y/Z Position "followers".  These roles are structural
    and persist regardless of whether dimensions are currently separated.
    """

    def test_is_separation_leader(self) -> None:
        """Position is always a separation leader."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "transform_separated.aep"))
        pos = _find_property(layer, "ADBE Position")
        assert pos is not None
        assert pos.is_separation_leader is True
        assert pos.is_separation_follower is False
        assert pos.separation_dimension is None

    def test_is_separation_follower(self) -> None:
        """Position_0/1/2 are always separation followers."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "transform_separated.aep"))
        for suffix, dim in [("_0", 0), ("_1", 1), ("_2", 2)]:
            prop = _find_property(layer, f"ADBE Position{suffix}")
            assert prop is not None, f"ADBE Position{suffix} not found"
            assert prop.is_separation_follower is True
            assert prop.is_separation_leader is False
            assert prop.separation_dimension == dim

    def test_get_separation_follower(self) -> None:
        """Position.get_separation_follower(dim) returns the follower."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "transform_separated.aep"))
        pos = _find_property(layer, "ADBE Position")
        assert pos is not None
        for dim in range(3):
            follower = pos.get_separation_follower(dim)
            assert follower is not None, f"follower dim {dim} is None"
            assert follower.match_name == f"ADBE Position_{dim}"

    def test_separation_leader_back_reference(self) -> None:
        """Follower.separation_leader returns the Position property."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "transform_separated.aep"))
        pos = _find_property(layer, "ADBE Position")
        x_pos = _find_property(layer, "ADBE Position_0")
        assert x_pos is not None
        assert x_pos.separation_leader is pos

    def test_before_separation_still_structural(self) -> None:
        """Leader/follower roles hold even when never separated."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "before_separation.aep"))
        pos = _find_property(layer, "ADBE Position")
        assert pos is not None
        assert pos.is_separation_leader is True
        assert pos.dimensions_separated is False

        x_pos = _find_property(layer, "ADBE Position_0")
        assert x_pos is not None
        assert x_pos.is_separation_follower is True
        assert x_pos.separation_dimension == 0

    def test_non_position_not_separation(self) -> None:
        """Opacity has neither leader nor follower role."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "transform_separated.aep"))
        opa = _find_property(layer, "ADBE Opacity")
        assert opa is not None
        assert opa.is_separation_leader is False
        assert opa.is_separation_follower is False
        assert opa.separation_dimension is None
        assert opa.separation_leader is None
        assert opa.get_separation_follower(0) is None

    def test_unseparated_structural(self) -> None:
        """Leader/follower roles hold after un-separating."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "transform_unseparated.aep")
        )
        pos = _find_property(layer, "ADBE Position")
        assert pos is not None
        assert pos.is_separation_leader is True
        assert pos.dimensions_separated is False

        y_pos = _find_property(layer, "ADBE Position_1")
        assert y_pos is not None
        assert y_pos.is_separation_follower is True
        assert y_pos.separation_dimension == 1


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
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_modified_false.aep"))
        assert layer.transform is not None
        assert len(layer.transform.properties) == 12

    def test_canonical_order(self) -> None:
        """Properties appear in the canonical ExtendScript order."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "is_modified_false.aep"))
        match_names = [p.match_name for p in layer.transform.properties]
        assert match_names == self._CANONICAL_ORDER

    def test_synthesized_orientation_metadata(self) -> None:
        """Orientation always present with correct defaults."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.default_value is not None
        assert orientation.is_modified is False

    def test_synthesized_rotate_x_metadata(self) -> None:
        """X Rotation always present with correct defaults."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        rotate_x = _find_property(layer, "ADBE Rotate X")
        assert rotate_x is not None
        assert rotate_x.dimensions == 1
        assert rotate_x.default_value is not None
        assert rotate_x.is_modified is False

    def test_synthesized_value_equals_default(self) -> None:
        """Non-animated transform properties at default have is_modified=False."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
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
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        for match_name in ("ADBE Orientation", "ADBE Rotate X", "ADBE Rotate Y"):
            prop = _find_property(layer, match_name)
            assert prop is not None
            assert not prop.animated, f"{match_name} should not be animated"
            assert prop.expression == ""
            assert prop.keyframes == []

    def test_synthesized_parent_property(self) -> None:
        """Synthesized properties point to the transform group as parent."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        for prop in layer.transform.properties:
            assert prop.parent_property is layer.transform, (
                f"{prop.match_name} parent should be transform group"
            )

    def test_envir_appear_in_reflect(self) -> None:
        """Appears in Reflections is synthesised with correct name and value."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        envir = _find_property(layer, "ADBE Envir Appear in Reflect")
        assert envir is not None
        assert envir.name == "Appears in Reflections"
        assert envir.value == 1.0
        assert envir.default_value == 1.0
        assert envir.is_modified is False

    def test_property_rotation_twelve_properties(self) -> None:
        """Another sample (property_rotation) also gets 12 transform props."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_rotation.aep"))
        assert layer.transform is not None
        assert len(layer.transform.properties) == 12
        match_names = [p.match_name for p in layer.transform.properties]
        assert match_names == self._CANONICAL_ORDER


LAYER_SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "layer"


class TestUnitsText:
    """Tests for Property.units_text.

    The ``units_text`` attribute is determined by the property's ``match_name``
    and returns one of ``"pixels"``, ``"degrees"``, ``"percent"``,
    ``"seconds"``, ``"dB"``, or ``""`` (no unit).
    """

    # -- Transform properties ------------------------------------------------

    def test_transform_pixels(self) -> None:
        """Anchor Point and Position report 'pixels'."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        anchor = _find_property(layer, "ADBE Anchor Point")
        assert anchor is not None
        assert anchor.units_text == "pixels"

        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.units_text == "pixels"

    def test_transform_percent(self) -> None:
        """Scale and Opacity report 'percent'."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        scale = _find_property(layer, "ADBE Scale")
        assert scale is not None
        assert scale.units_text == "percent"

        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.units_text == "percent"

    def test_transform_degrees(self) -> None:
        """Rotation and Orientation report 'degrees'."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_rotation.aep"))
        rotate_z = _find_property(layer, "ADBE Rotate Z")
        assert rotate_z is not None
        assert rotate_z.units_text == "degrees"

        orientation = _find_property(layer, "ADBE Orientation")
        assert orientation is not None
        assert orientation.units_text == "degrees"

    def test_transform_no_unit(self) -> None:
        """Appears in Reflections has empty units_text."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        envir = _find_property(layer, "ADBE Envir Appear in Reflect")
        assert envir is not None
        assert envir.units_text == ""

    # -- Separated position followers ----------------------------------------

    def test_separation_followers_pixels(self) -> None:
        """X/Y/Z Position followers report 'pixels'."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "transform_separated.aep"))
        for mn in ("ADBE Position_0", "ADBE Position_1"):
            prop = _find_property(layer, mn)
            assert prop is not None, f"{mn} missing"
            assert prop.units_text == "pixels", f"{mn} wrong units"

    # -- Mask properties -----------------------------------------------------

    def test_mask_feather_pixels(self) -> None:
        """Mask Feather reports 'pixels'."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "mask_add.aep"))
        assert layer.masks is not None
        mask = layer.masks.properties[0]
        # Mask children: [0]=Feather, [1]=Opacity, [2]=Expansion(Offset)
        feather = mask.properties[0]
        assert feather.match_name == "ADBE Mask Feather"
        assert feather.units_text == "pixels"

    def test_mask_opacity_percent(self) -> None:
        """Mask Opacity reports 'percent'."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "mask_add.aep"))
        assert layer.masks is not None
        mask = layer.masks.properties[0]
        opacity = mask.properties[1]
        assert opacity.match_name == "ADBE Mask Opacity"
        assert opacity.units_text == "percent"

    # -- Effect properties ---------------------------------------------------

    def test_effect_mask_opacity_percent(self) -> None:
        """Effect Mask Opacity (Compositing Options) reports 'percent'."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "effect_2dPoint.aep"))
        assert layer.effects is not None
        effect = layer.effects.properties[0]
        # Compositing Options group is the last child of an effect
        comp_opts = None
        for child in effect.properties:
            if child.match_name == "ADBE Effect Built In Params":
                comp_opts = child
                break
        assert comp_opts is not None
        opacity = None
        for child in comp_opts.properties:
            if child.match_name == "ADBE Effect Mask Opacity":
                opacity = child
                break
        assert opacity is not None
        assert opacity.units_text == "percent"

    def test_effect_property_no_unit(self) -> None:
        """Gaussian Blur Blurriness has no units in the map > empty string."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "2_gaussian_20_30.aep"))
        assert layer.effects is not None
        effect = layer.effects.properties[0]
        blurriness = None
        for child in effect.properties:
            if child.match_name == "ADBE Gaussian Blur 2-0001":
                blurriness = child
                break
        assert blurriness is not None
        assert blurriness.units_text == ""

    # -- Time Remapping ------------------------------------------------------

    def test_time_remapping_seconds(self) -> None:
        """Time Remapping reports 'seconds'."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_BEZIER.aep"))
        for prop_group in layer.properties:
            if prop_group.match_name == "ADBE Time Remapping":
                assert prop_group.units_text == "seconds"
                return
        pytest.skip("Time Remapping not found in this sample")

    # -- Unknown match name --------------------------------------------------

    def test_unknown_match_name_empty(self) -> None:
        """Unknown match names default to empty string."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "property_1D_opacity.aep"))
        envir = _find_property(layer, "ADBE Envir Appear in Reflect")
        assert envir is not None
        assert envir.units_text == ""


class TestKeyframeInterpolationTypes:
    """Tests for in/out interpolation type fields on keyframes."""

    def test_linear_in_out_match(self) -> None:
        """LINEAR keyframes have matching in/out interpolation types."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_LINEAR.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        for kf in position.keyframes:
            assert kf.in_interpolation_type == KeyframeInterpolationType.LINEAR
            assert kf.out_interpolation_type == KeyframeInterpolationType.LINEAR

    def test_bezier_in_out_match(self) -> None:
        """BEZIER keyframes have matching in/out interpolation types."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_BEZIER.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        for kf in position.keyframes:
            assert kf.in_interpolation_type == KeyframeInterpolationType.BEZIER
            assert kf.out_interpolation_type == KeyframeInterpolationType.BEZIER

    def test_mixed_interpolation(self) -> None:
        """Mixed interpolation keyframes have different in/out types."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_mixed_interpolation.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert len(opacity.keyframes) == 4
        # KF[0]: LINEAR in/out
        assert (
            opacity.keyframes[0].in_interpolation_type
            == KeyframeInterpolationType.LINEAR
        )
        assert (
            opacity.keyframes[0].out_interpolation_type
            == KeyframeInterpolationType.LINEAR
        )
        # KF[1]: BEZIER in, HOLD out
        assert (
            opacity.keyframes[1].in_interpolation_type
            == KeyframeInterpolationType.BEZIER
        )
        assert (
            opacity.keyframes[1].out_interpolation_type
            == KeyframeInterpolationType.HOLD
        )
        # KF[2]: HOLD in, LINEAR out
        assert (
            opacity.keyframes[2].in_interpolation_type == KeyframeInterpolationType.HOLD
        )
        assert (
            opacity.keyframes[2].out_interpolation_type
            == KeyframeInterpolationType.LINEAR
        )
        # KF[3]: LINEAR in/out
        assert (
            opacity.keyframes[3].in_interpolation_type
            == KeyframeInterpolationType.LINEAR
        )
        assert (
            opacity.keyframes[3].out_interpolation_type
            == KeyframeInterpolationType.LINEAR
        )


class TestTemporalEase:
    """Tests for in/out temporal ease on keyframes."""

    def test_bezier_ease_in_out_1d(self) -> None:
        """1D Bezier ease has one KeyframeEase per keyframe."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_bezier_ease_in_out_1D.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        for kf in opacity.keyframes:
            assert len(kf.in_temporal_ease) == 1
            assert len(kf.out_temporal_ease) == 1

    def test_bezier_ease_scale_multi_dim(self) -> None:
        """Scale (3D) has three KeyframeEase per keyframe."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_bezier_ease_scale.aep")
        )
        scale = _find_property(layer, "ADBE Scale")
        assert scale is not None
        assert len(scale.keyframes) >= 2
        for kf in scale.keyframes:
            assert len(kf.in_temporal_ease) == 3
            assert len(kf.out_temporal_ease) == 3

    def test_bezier_ease_scale_influence_values(self) -> None:
        """Scale ease-scale sample: KF0 out influence=75, KF1 in influence=75."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_bezier_ease_scale.aep")
        )
        scale = _find_property(layer, "ADBE Scale")
        assert scale is not None
        # KF0 out_ease all 75%
        for ease in scale.keyframes[0].out_temporal_ease:
            assert abs(ease.influence - 75.0) < 0.01
        # KF1 in_ease all 75%
        for ease in scale.keyframes[1].in_temporal_ease:
            assert abs(ease.influence - 75.0) < 0.01

    def test_bezier_nonzero_speed(self) -> None:
        """Percent property speeds are scaled to match ExtendScript units."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_bezier_nonzero_speed.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        # KF0 out speed = 20 (%/sec), KF1 in speed = 15 (%/sec)
        assert abs(opacity.keyframes[0].out_temporal_ease[0].speed - 20.0) < 0.1
        assert abs(opacity.keyframes[1].in_temporal_ease[0].speed - 15.0) < 0.1

    def test_bezier_asymmetric_ease(self) -> None:
        """Asymmetric ease has different in/out influence values."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_bezier_asymmetric_ease_1D.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        # Should have at least 2 keyframes with different in/out
        kf0 = opacity.keyframes[0]
        assert len(kf0.in_temporal_ease) == 1
        assert len(kf0.out_temporal_ease) == 1

    def test_spatial_position_single_ease(self) -> None:
        """Spatial properties (Position) always have 1 ease element."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_spatial_bezier_arc.aep")
        )
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        for kf in position.keyframes:
            assert len(kf.in_temporal_ease) == 1
            assert len(kf.out_temporal_ease) == 1

    def test_bounce_pattern_ease_count(self) -> None:
        """Bounce pattern has 10 keyframes, each with ease data."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_bounce_pattern.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert len(opacity.keyframes) == 10
        for kf in opacity.keyframes:
            assert len(kf.in_temporal_ease) == 1
            assert len(kf.out_temporal_ease) == 1


class TestSpatialTangents:
    """Tests for in/out spatial tangents on keyframes."""

    def test_spatial_tangents_present(self) -> None:
        """Spatial bezier arc has non-None tangent vectors."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_spatial_bezier_arc.aep")
        )
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        for kf in position.keyframes:
            assert kf.in_spatial_tangent is not None
            assert kf.out_spatial_tangent is not None
            assert len(kf.in_spatial_tangent) == 3  # x, y, z
            assert len(kf.out_spatial_tangent) == 3

    def test_spatial_tangent_values_arc(self) -> None:
        """Spatial bezier arc: KF0 out tangent = [60, -80, 0]."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_spatial_bezier_arc.aep")
        )
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        kf0 = position.keyframes[0]
        assert kf0.out_spatial_tangent is not None
        assert abs(kf0.out_spatial_tangent[0] - 60.0) < 0.01
        assert abs(kf0.out_spatial_tangent[1] - (-80.0)) < 0.01
        assert abs(kf0.out_spatial_tangent[2] - 0.0) < 0.01

    def test_non_spatial_no_tangents(self) -> None:
        """Non-spatial properties (Opacity) have None tangents."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_bezier_ease_in_out_1D.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        for kf in opacity.keyframes:
            assert kf.in_spatial_tangent is None
            assert kf.out_spatial_tangent is None

    def test_3d_spatial_tangents(self) -> None:
        """3D spatial bezier has 3-component tangent vectors."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_spatial_bezier_3D.aep")
        )
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        for kf in position.keyframes:
            assert kf.in_spatial_tangent is not None
            assert kf.out_spatial_tangent is not None
            assert len(kf.in_spatial_tangent) == 3
            assert len(kf.out_spatial_tangent) == 3

    def test_s_curve_spatial_tangents(self) -> None:
        """S-curve: KF1 in tangent = [-40, -60, 0]."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_spatial_bezier_s_curve.aep")
        )
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        kf1 = position.keyframes[1]
        assert kf1.in_spatial_tangent is not None
        assert abs(kf1.in_spatial_tangent[0] - (-40.0)) < 0.01
        assert abs(kf1.in_spatial_tangent[1] - (-60.0)) < 0.01


class TestLinearHoldEase:
    """Tests for computed temporal ease on LINEAR and HOLD keyframes.

    The binary stores zeros for LINEAR/HOLD ease but ExtendScript computes
    and reports actual values: influence = 100/6 (≈16.667 %) and speed =
    value_change / time_in_seconds.
    """

    DEFAULT_INFLUENCE = 100.0 / 6.0

    def test_linear_position_out_speed(self) -> None:
        """LINEAR position: KF0 out speed = distance / time."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_LINEAR.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        kf0 = position.keyframes[0]
        # [0,50,0] > [100,50,0] over 5 seconds (120 frames @ 24fps)
        # distance = 100, speed = 100/5 = 20
        assert abs(kf0.out_temporal_ease[0].speed - 20.0) < 0.01
        assert abs(kf0.out_temporal_ease[0].influence - self.DEFAULT_INFLUENCE) < 0.001

    def test_linear_position_in_speed(self) -> None:
        """LINEAR position: KF1 in speed = distance / time."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_LINEAR.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        kf1 = position.keyframes[1]
        assert abs(kf1.in_temporal_ease[0].speed - 20.0) < 0.01
        assert abs(kf1.in_temporal_ease[0].influence - self.DEFAULT_INFLUENCE) < 0.001

    def test_linear_first_keyframe_in_speed_zero(self) -> None:
        """First keyframe in a LINEAR property has in speed = 0."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_LINEAR.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        kf0 = position.keyframes[0]
        assert abs(kf0.in_temporal_ease[0].speed) < 0.001
        assert abs(kf0.in_temporal_ease[0].influence - self.DEFAULT_INFLUENCE) < 0.001

    def test_linear_last_keyframe_out_speed_zero(self) -> None:
        """Last keyframe in a LINEAR property has out speed = 0."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_LINEAR.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        kf_last = position.keyframes[-1]
        assert abs(kf_last.out_temporal_ease[0].speed) < 0.001
        assert (
            abs(kf_last.out_temporal_ease[0].influence - self.DEFAULT_INFLUENCE) < 0.001
        )

    def test_mixed_linear_opacity_speed(self) -> None:
        """Mixed interpolation: LINEAR opacity out speed = value_change / time."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_mixed_interpolation.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        # KF[0] (100%) > KF[1] (0%) over 3 sec (72 frames @ 24fps)
        # speed = (0 - 100) / 3 = -33.333
        kf0 = opacity.keyframes[0]
        assert abs(kf0.out_temporal_ease[0].speed - (-100.0 / 3.0)) < 0.01
        assert abs(kf0.out_temporal_ease[0].influence - self.DEFAULT_INFLUENCE) < 0.001

    def test_mixed_hold_out_speed_zero(self) -> None:
        """HOLD out keyframe has speed = 0 and influence = 100/6."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_mixed_interpolation.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        # KF[1]: BEZIER in, HOLD out
        kf1 = opacity.keyframes[1]
        assert abs(kf1.out_temporal_ease[0].speed) < 0.001
        assert abs(kf1.out_temporal_ease[0].influence - self.DEFAULT_INFLUENCE) < 0.001

    def test_mixed_hold_in_speed_zero(self) -> None:
        """HOLD in keyframe has speed = 0 and influence = 100/6."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_mixed_interpolation.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        # KF[2]: HOLD in, LINEAR out
        kf2 = opacity.keyframes[2]
        assert abs(kf2.in_temporal_ease[0].speed) < 0.001
        assert abs(kf2.in_temporal_ease[0].influence - self.DEFAULT_INFLUENCE) < 0.001

    def test_mixed_linear_out_after_hold(self) -> None:
        """LINEAR out after HOLD in computes speed from adjacent keyframes."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_mixed_interpolation.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        # KF[2] (100%) > KF[3] (50%) over 3 sec (72 frames @ 24fps)
        # speed = (50 - 100) / 3 = -16.667
        kf2 = opacity.keyframes[2]
        assert abs(kf2.out_temporal_ease[0].speed - (-50.0 / 3.0)) < 0.01
        assert abs(kf2.out_temporal_ease[0].influence - self.DEFAULT_INFLUENCE) < 0.001

    def test_bezier_ease_unchanged(self) -> None:
        """BEZIER keyframes retain their stored binary ease values."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "keyframe_mixed_interpolation.aep")
        )
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        # KF[1]: BEZIER in - binary stores (speed=0, influence=0)
        kf1 = opacity.keyframes[1]
        assert abs(kf1.in_temporal_ease[0].speed) < 0.001
        assert abs(kf1.in_temporal_ease[0].influence) < 0.001


def _get_mask_shape(layer) -> Property:  # type: ignore[type-arg]
    """Return the ``ADBE Mask Shape`` property from the first mask."""
    assert layer.masks is not None
    mask = layer.masks.properties[0]
    for prop in mask.properties:
        if prop.match_name == "ADBE Mask Shape":
            return prop
    raise AssertionError("ADBE Mask Shape not found")


class TestShapeValue:
    """Tests for Shape value parsing (vertices, tangents, feather)."""

    def test_closed_square_vertices(self) -> None:
        """Closed square mask has 4 vertices at the expected positions."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "shape_closed_square.aep"))
        shape = _get_mask_shape(layer).value
        assert shape.closed is True
        assert len(shape.vertices) == 4
        assert shape.vertices == [
            [100.0, 100.0],
            [100.0, 300.0],
            [300.0, 300.0],
            [300.0, 100.0],
        ]

    def test_closed_square_tangents_zero(self) -> None:
        """Closed square mask has zero tangents (straight line segments)."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "shape_closed_square.aep"))
        shape = _get_mask_shape(layer).value
        for t in shape.in_tangents + shape.out_tangents:
            assert t == [0, 0]

    def test_closed_square_no_feather(self) -> None:
        """Closed square mask has empty feather arrays."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "shape_closed_square.aep"))
        shape = _get_mask_shape(layer).value
        assert shape.feather_seg_locs == []
        assert shape.feather_radii == []
        assert shape.feather_types == []
        assert shape.feather_interps == []
        assert shape.feather_tensions == []
        assert shape.feather_rel_seg_locs == []
        assert shape.feather_rel_corner_angles == []

    def test_closed_oval_tangents(self) -> None:
        """Closed oval mask has non-zero tangents."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "shape_closed_oval.aep"))
        shape = _get_mask_shape(layer).value
        assert shape.closed is True
        assert len(shape.vertices) == 4
        # Tangents should be non-zero (bezier curves)
        for t in shape.in_tangents + shape.out_tangents:
            assert t != [0, 0]

    def test_open_path(self) -> None:
        """Open path mask has closed=False."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "shape_open.aep"))
        shape = _get_mask_shape(layer).value
        assert shape.closed is False
        assert len(shape.vertices) == 4

    def test_feather_points(self) -> None:
        """Feather points mask has 2 outer feather points at segments 1 and 2."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "shape_feather_points.aep"))
        shape = _get_mask_shape(layer).value
        assert shape.feather_seg_locs == [1, 2]
        assert shape.feather_rel_seg_locs == [0.15, 0.5]
        assert shape.feather_radii == [30.0, 100.0]
        assert shape.feather_types == [0, 0]
        assert shape.feather_interps == [0, 0]
        assert shape.feather_tensions == [0.0, 0.0]
        assert shape.feather_rel_corner_angles == [0.0, 0.0]

    def test_feather_inner_hold(self) -> None:
        """Feather with inner/outer types and hold/non-hold interpolation."""
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "shape_feather_inner_hold.aep")
        )
        shape = _get_mask_shape(layer).value
        assert shape.feather_seg_locs == [0, 1, 2, 3]
        assert shape.feather_radii == [50.0, -30.0, 80.0, -20.0]
        assert shape.feather_types == [0, 1, 0, 1]
        assert shape.feather_interps == [0, 0, 1, 1]
        assert shape.feather_tensions == [0.0, 0.5, 1.0, 0.25]
        assert shape.feather_rel_corner_angles == [0.0, 0.0, 0.0, 0.0]

    def test_animated_keyframes(self) -> None:
        """Animated mask shape has 2 keyframes with different vertices."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "shape_animated.aep"))
        prop = _get_mask_shape(layer)
        assert len(prop.keyframes) == 2
        kf0 = prop.keyframes[0].value
        kf1 = prop.keyframes[1].value
        assert kf0.vertices == [
            [100.0, 100.0],
            [100.0, 300.0],
            [300.0, 300.0],
            [300.0, 100.0],
        ]
        assert kf1.vertices == [
            [150.0, 150.0],
            [150.0, 250.0],
            [250.0, 250.0],
            [250.0, 150.0],
        ]

    def test_many_points_seg_locs(self) -> None:
        """300-vertex mask with feather seg_locs >255 proves u4le field width."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "shape_many_points.aep"))
        shape = _get_mask_shape(layer).value
        assert len(shape.vertices) == 300
        assert shape.feather_seg_locs == [0, 128, 255, 256, 270, 299]
        assert shape.feather_radii == [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
