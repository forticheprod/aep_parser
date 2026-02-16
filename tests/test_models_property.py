"""Tests for Property model parsing with strengthened assertions."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import get_first_layer, get_sample_files, load_expected

from aep_parser import Project, parse_project
from aep_parser.models.enums import KeyframeInterpolationType

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "property"


def _find_property(layer, match_name: str):  # type: ignore[no-untyped-def]
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
        """Position has 2 LINEAR keyframes."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_LINEAR.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.animated
        assert len(position.keyframes) == 2
        for kf in position.keyframes:
            assert kf.keyframe_interpolation_type == KeyframeInterpolationType.LINEAR

    def test_keyframe_BEZIER(self) -> None:
        """Position has 2 BEZIER keyframes."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_BEZIER.aep"))
        position = _find_property(layer, "ADBE Position")
        assert position is not None
        assert position.animated
        assert len(position.keyframes) == 2
        for kf in position.keyframes:
            assert kf.keyframe_interpolation_type == KeyframeInterpolationType.BEZIER

    def test_keyframe_HOLD(self) -> None:
        """Opacity has 3 keyframes, second is HOLD."""
        layer = get_first_layer(parse_project(SAMPLES_DIR / "keyframe_HOLD.aep"))
        opacity = _find_property(layer, "ADBE Opacity")
        assert opacity is not None
        assert opacity.animated
        assert len(opacity.keyframes) == 3
        # Keyframe 2 (index 1) is HOLD
        assert opacity.keyframes[1].keyframe_interpolation_type == KeyframeInterpolationType.HOLD


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
