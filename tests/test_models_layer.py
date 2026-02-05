"""Tests for Layer model parsing using samples from models/layer/.

These tests verify that aep_parser produces the same values as the JSON
reference files exported from After Effects.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from aep_parser import Project, parse_project
from aep_parser.models.enums import (
    AutoOrientType,
    BlendingMode,
    FrameBlendingType,
    LayerQuality,
    LayerSamplingQuality,
    LightType,
    TrackMatteType,
)
from aep_parser.models.layers import (
    AVLayer,
    CameraLayer,
    ShapeLayer,
    TextLayer,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "layer"


def get_sample_files() -> list[str]:
    """Get all .aep files in the layer samples directory."""
    if not SAMPLES_DIR.exists():
        return []
    return [f.stem for f in SAMPLES_DIR.glob("*.aep")]


def load_expected(sample_name: str) -> dict:
    """Load the expected JSON for a sample."""
    json_path = SAMPLES_DIR / f"{sample_name}.json"
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("sample_name", get_sample_files())
def test_parse_layer_sample(sample_name: str) -> None:
    """Test that each layer sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


def get_first_layer(project: Project):
    """Get the first layer from the first composition that has layers."""
    assert len(project.compositions) >= 1
    for comp in project.compositions:
        if len(comp.layers) >= 1:
            return comp.layers[0]
    raise AssertionError("No composition with layers found")


def get_layer_from_json(expected: dict) -> dict:
    """Extract layer data from expected JSON."""
    # JSON structure: {"items": [{"layers": [...]}]}
    if "items" in expected:
        for item in expected["items"]:
            if "layers" in item and len(item["layers"]) > 0:
                return item["layers"][0]
    return {}


class TestLayerBasic:
    """Tests for basic layer attributes."""

    def test_enabled_false(self) -> None:
        """Test layer with enabled=false (video switch off)."""
        expected = load_expected("enabled_false")
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["enabled"] is False
        assert layer.enabled == layer_json["enabled"]

    def test_locked_true(self) -> None:
        """Test locked layer."""
        expected = load_expected("locked_true")
        project = parse_project(SAMPLES_DIR / "locked_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["locked"] is True
        assert layer.locked == layer_json["locked"]

    def test_shy_true(self) -> None:
        """Test shy layer."""
        expected = load_expected("shy_true")
        project = parse_project(SAMPLES_DIR / "shy_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["shy"] is True
        assert layer.shy == layer_json["shy"]

    def test_solo_true(self) -> None:
        """Test soloed layer."""
        expected = load_expected("solo_true")
        project = parse_project(SAMPLES_DIR / "solo_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["solo"] is True
        assert layer.solo == layer_json["solo"]

    def test_name_renamed(self) -> None:
        """Test renamed layer."""
        expected = load_expected("name_renamed")
        project = parse_project(SAMPLES_DIR / "name_renamed.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["name"] == "RenamedLayer"
        assert layer.name == layer_json["name"]

    def test_comment(self) -> None:
        """Test layer with comment."""
        expected = load_expected("comment")
        project = parse_project(SAMPLES_DIR / "comment.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["comment"] == "Test layer comment"
        assert layer.comment == layer_json["comment"]

    def test_label_3(self) -> None:
        """Test layer with label 3."""
        expected = load_expected("label_3")
        project = parse_project(SAMPLES_DIR / "label_3.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["label"] == 3
        assert layer.label.value == layer_json["label"]


class TestLayerTiming:
    """Tests for layer timing attributes."""

    def test_startTime_5(self) -> None:
        """Test layer with start time at 5 seconds."""
        expected = load_expected("startTime_5")
        project = parse_project(SAMPLES_DIR / "startTime_5.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["startTime"] == 5
        assert math.isclose(layer.start_time, layer_json["startTime"])

    def test_inPoint_5(self) -> None:
        """Test layer with in point at 5 seconds."""
        expected = load_expected("inPoint_5")
        project = parse_project(SAMPLES_DIR / "inPoint_5.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["inPoint"] == 5
        assert math.isclose(layer.in_point, layer_json["inPoint"])

    def test_outPoint_10(self) -> None:
        """Test layer with out point at 10 seconds."""
        expected = load_expected("outPoint_10")
        project = parse_project(SAMPLES_DIR / "outPoint_10.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["outPoint"] == 10
        assert math.isclose(layer.out_point, layer_json["outPoint"])

    def test_stretch_200(self) -> None:
        """Test layer with 200% time stretch."""
        expected = load_expected("stretch_200")
        project = parse_project(SAMPLES_DIR / "stretch_200.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["stretch"] == 200
        assert math.isclose(layer.stretch, layer_json["stretch"])

    def test_stretch_minus100(self) -> None:
        """Test layer with -100% time stretch (reversed)."""
        expected = load_expected("stretch_minus100")
        project = parse_project(SAMPLES_DIR / "stretch_minus100.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["stretch"] == -100
        assert math.isclose(layer.stretch, layer_json["stretch"])


class TestLayerTypes:
    """Tests for different layer types."""

    def test_type_camera(self) -> None:
        """Test camera layer."""
        project = parse_project(SAMPLES_DIR / "type_camera.aep")
        layer = get_first_layer(project)
        assert layer.layer_type.name == "camera"
        assert isinstance(layer, CameraLayer)

    def test_type_null(self) -> None:
        """Test null layer."""
        expected = load_expected("type_null")
        project = parse_project(SAMPLES_DIR / "type_null.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["nullLayer"] is True
        assert layer.null_layer == layer_json["nullLayer"]

    def test_type_shape(self) -> None:
        """Test shape layer."""
        project = parse_project(SAMPLES_DIR / "type_shape.aep")
        layer = get_first_layer(project)
        assert layer.layer_type.name == "shape"
        assert isinstance(layer, ShapeLayer)

    def test_type_text(self) -> None:
        """Test text layer."""
        project = parse_project(SAMPLES_DIR / "type_text.aep")
        layer = get_first_layer(project)
        assert layer.layer_type.name == "text"
        assert isinstance(layer, TextLayer)


class TestLightTypes:
    """Tests for light layer types."""

    def test_lightType_AMBIENT(self) -> None:
        """Test ambient light."""
        expected = load_expected("lightType_AMBIENT")
        project = parse_project(SAMPLES_DIR / "lightType_AMBIENT.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["lightType"] == LightType.AMBIENT
        assert layer.light_type == layer_json["lightType"]

    def test_lightType_POINT(self) -> None:
        """Test point light."""
        expected = load_expected("lightType_POINT")
        project = parse_project(SAMPLES_DIR / "lightType_POINT.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["lightType"] == LightType.POINT
        assert layer.light_type == layer_json["lightType"]

    def test_lightType_SPOT(self) -> None:
        """Test spot light."""
        expected = load_expected("lightType_SPOT")
        project = parse_project(SAMPLES_DIR / "lightType_SPOT.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["lightType"] == LightType.SPOT
        assert layer.light_type == layer_json["lightType"]

    def test_lightType_PARALLEL(self) -> None:
        """Test parallel light."""
        expected = load_expected("lightType_PARALLEL")
        project = parse_project(SAMPLES_DIR / "lightType_PARALLEL.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["lightType"] == LightType.PARALLEL
        assert layer.light_type == layer_json["lightType"]


class TestAVLayerAttributes:
    """Tests for AVLayer-specific attributes."""

    def test_threeDLayer_true(self) -> None:
        """Test 3D layer."""
        expected = load_expected("threeDLayer_true")
        project = parse_project(SAMPLES_DIR / "threeDLayer_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert isinstance(layer, AVLayer)
        assert layer_json["threeDLayer"] is True
        assert layer.three_d_layer == layer_json["threeDLayer"]

    def test_adjustmentLayer_true(self) -> None:
        """Test adjustment layer."""
        expected = load_expected("adjustmentLayer_true")
        project = parse_project(SAMPLES_DIR / "adjustmentLayer_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["adjustmentLayer"] is True
        assert layer.adjustment_layer == layer_json["adjustmentLayer"]

    def test_guideLayer_true(self) -> None:
        """Test guide layer."""
        expected = load_expected("guideLayer_true")
        project = parse_project(SAMPLES_DIR / "guideLayer_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["guideLayer"] is True
        assert layer.guide_layer == layer_json["guideLayer"]

    def test_collapseTransformation_true(self) -> None:
        """Test collapse transformation."""
        expected = load_expected("collapseTransformation_true")
        project = parse_project(SAMPLES_DIR / "collapseTransformation_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["collapseTransformation"] is True
        assert layer.collapse_transformation == layer_json["collapseTransformation"]

    def test_preserveTransparency_true(self) -> None:
        """Test preserve transparency."""
        expected = load_expected("preserveTransparency_true")
        project = parse_project(SAMPLES_DIR / "preserveTransparency_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["preserveTransparency"] is True
        assert layer.preserve_transparency == layer_json["preserveTransparency"]

    def test_motionBlur_true(self) -> None:
        """Test layer motion blur enabled."""
        expected = load_expected("motionBlur_true")
        project = parse_project(SAMPLES_DIR / "motionBlur_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["motionBlur"] is True
        assert layer.motion_blur == layer_json["motionBlur"]

    def test_effectsActive_false(self) -> None:
        """Test effects disabled on layer."""
        expected = load_expected("effectsActive_false")
        project = parse_project(SAMPLES_DIR / "effectsActive_false.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["effectsActive"] is False
        assert layer.effects_active == layer_json["effectsActive"]


class TestBlendingModes:
    """Tests for blending mode attributes."""

    def test_blendingMode_ADD(self) -> None:
        """Test Add blending mode."""
        expected = load_expected("blendingMode_ADD")
        project = parse_project(SAMPLES_DIR / "blendingMode_ADD.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["blendingMode"] == BlendingMode.ADD
        assert layer.blending_mode == layer_json["blendingMode"]

    def test_blendingMode_MULTIPLY(self) -> None:
        """Test Multiply blending mode."""
        expected = load_expected("blendingMode_MULTIPLY")
        project = parse_project(SAMPLES_DIR / "blendingMode_MULTIPLY.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["blendingMode"] == BlendingMode.MULTIPLY
        assert layer.blending_mode == layer_json["blendingMode"]

    def test_blendingMode_SCREEN(self) -> None:
        """Test Screen blending mode."""
        expected = load_expected("blendingMode_SCREEN")
        project = parse_project(SAMPLES_DIR / "blendingMode_SCREEN.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["blendingMode"] == BlendingMode.SCREEN
        assert layer.blending_mode == layer_json["blendingMode"]


class TestQualitySettings:
    """Tests for layer quality settings."""

    def test_quality_BEST(self) -> None:
        """Test Best quality."""
        expected = load_expected("quality_BEST")
        project = parse_project(SAMPLES_DIR / "quality_BEST.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["quality"] == LayerQuality.BEST
        assert layer.quality == layer_json["quality"]

    def test_quality_DRAFT(self) -> None:
        """Test Draft quality."""
        expected = load_expected("quality_DRAFT")
        project = parse_project(SAMPLES_DIR / "quality_DRAFT.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["quality"] == LayerQuality.DRAFT
        assert layer.quality == layer_json["quality"]

    def test_quality_WIREFRAME(self) -> None:
        """Test Wireframe quality."""
        expected = load_expected("quality_WIREFRAME")
        project = parse_project(SAMPLES_DIR / "quality_WIREFRAME.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["quality"] == LayerQuality.WIREFRAME
        assert layer.quality == layer_json["quality"]

    def test_samplingQuality_BICUBIC(self) -> None:
        """Test Bicubic sampling quality."""
        expected = load_expected("samplingQuality_BICUBIC")
        project = parse_project(SAMPLES_DIR / "samplingQuality_BICUBIC.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["samplingQuality"] == LayerSamplingQuality.BICUBIC
        assert layer.sampling_quality == layer_json["samplingQuality"]


class TestFrameBlending:
    """Tests for frame blending type.

    The frame blending type depends on two factors:
    1. The layer's frameBlending boolean (read-only, derived from frameBlendingType)
    2. The binary frame_blending_type bit (0=FRAME_MIX, 1=PIXEL_MOTION)

    When frameBlending is False, frameBlendingType should be NO_FRAME_BLEND (4012).
    This was a regression bug where binary value 0 was incorrectly mapped to FRAME_MIX.
    """

    def test_frameBlendingType_NO_FRAME_BLEND(self) -> None:
        """Test NO_FRAME_BLEND when layer frame blending is disabled.

        This covers the regression where binary value 0 was incorrectly
        mapped to FRAME_MIX instead of NO_FRAME_BLEND when frameBlending=False.
        """
        expected = load_expected("frameBlendingType_NO_FRAME_BLEND")
        project = parse_project(SAMPLES_DIR / "frameBlendingType_NO_FRAME_BLEND.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["frameBlendingType"] == FrameBlendingType.NO_FRAME_BLEND
        assert layer.frame_blending_type == layer_json["frameBlendingType"]
        assert layer.frame_blending is False

    def test_frameBlendingType_FRAME_MIX(self) -> None:
        """Test Frame Mix blending type."""
        expected = load_expected("frameBlendingType_FRAME_MIX")
        project = parse_project(SAMPLES_DIR / "frameBlendingType_FRAME_MIX.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["frameBlendingType"] == FrameBlendingType.FRAME_MIX
        assert layer.frame_blending_type == layer_json["frameBlendingType"]

    def test_frameBlendingType_PIXEL_MOTION(self) -> None:
        """Test Pixel Motion blending type."""
        expected = load_expected("frameBlendingType_PIXEL_MOTION")
        project = parse_project(SAMPLES_DIR / "frameBlendingType_PIXEL_MOTION.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["frameBlendingType"] == FrameBlendingType.PIXEL_MOTION
        assert layer.frame_blending_type == layer_json["frameBlendingType"]


class TestAutoOrient:
    """Tests for auto-orient settings.

    The auto-orient type is stored across multiple bits in the binary format:
    - ALONG_PATH: auto_orient_along_path bit is set
    - CAMERA_OR_POINT_OF_INTEREST: camera_or_poi_auto_orient bit is set AND three_d_layer is set
    - CHARACTERS_TOWARD_CAMERA: characters_toward_camera bits equal 3 (0b11)
    - NO_AUTO_ORIENT: none of the above
    """

    def test_autoOrient_ALONG_PATH(self) -> None:
        """Test auto-orient along path."""
        expected = load_expected("autoOrient_ALONG_PATH")
        project = parse_project(SAMPLES_DIR / "autoOrient_ALONG_PATH.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["autoOrient"] == AutoOrientType.ALONG_PATH
        assert layer.auto_orient == layer_json["autoOrient"]

    def test_autoOrient_CAMERA(self) -> None:
        """Test auto-orient towards camera/point of interest."""
        expected = load_expected("autoOrient_CAMERA")
        project = parse_project(SAMPLES_DIR / "autoOrient_CAMERA.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["autoOrient"] == AutoOrientType.CAMERA_OR_POINT_OF_INTEREST
        assert layer.three_d_layer is True  # CAMERA requires 3D layer
        assert layer.auto_orient == layer_json["autoOrient"]

    def test_autoOrient_CHARACTERS(self) -> None:
        """Test auto-orient characters toward camera (per-character 3D text)."""
        expected = load_expected("autoOrient_CHARACTERS")
        project = parse_project(SAMPLES_DIR / "autoOrient_CHARACTERS.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["autoOrient"] == AutoOrientType.CHARACTERS_TOWARD_CAMERA
        assert layer.three_d_layer is True  # CHARACTERS requires 3D layer
        assert layer.auto_orient == layer_json["autoOrient"]


class TestTrackMatte:
    """Tests for track matte settings."""

    def test_trackMatteType_ALPHA(self) -> None:
        """Test Alpha track matte."""
        expected = load_expected("trackMatteType_ALPHA")
        project = parse_project(SAMPLES_DIR / "trackMatteType_ALPHA.aep")
        # Find the layer that has a track matte (not the matte itself)
        comp = project.compositions[0]
        matted_layer = None
        expected_layer_json = None
        for item in expected["items"]:
            if "layers" in item:
                for layer_json in item["layers"]:
                    if layer_json.get("trackMatteType") == TrackMatteType.ALPHA:
                        expected_layer_json = layer_json
                        break
        for layer in comp.layers:
            if layer.track_matte_type == TrackMatteType.ALPHA:
                matted_layer = layer
                break
        assert matted_layer is not None
        assert expected_layer_json is not None
        assert matted_layer.track_matte_type == TrackMatteType.ALPHA
        assert matted_layer.track_matte_type == expected_layer_json["trackMatteType"]

    def test_trackMatteType_LUMA(self) -> None:
        """Test Luma track matte."""
        expected = load_expected("trackMatteType_LUMA")
        project = parse_project(SAMPLES_DIR / "trackMatteType_LUMA.aep")
        comp = project.compositions[0]
        matted_layer = None
        expected_layer_json = None
        for item in expected["items"]:
            if "layers" in item:
                for layer_json in item["layers"]:
                    if layer_json.get("trackMatteType") == TrackMatteType.LUMA:
                        expected_layer_json = layer_json
                        break
        for layer in comp.layers:
            if layer.track_matte_type == TrackMatteType.LUMA:
                matted_layer = layer
                break
        assert matted_layer is not None
        assert expected_layer_json is not None
        assert matted_layer.track_matte_type == TrackMatteType.LUMA
        assert matted_layer.track_matte_type == expected_layer_json["trackMatteType"]


class TestParenting:
    """Tests for layer parenting."""

    def test_parent(self) -> None:
        """Test layer with parent."""
        expected = load_expected("parent")
        project = parse_project(SAMPLES_DIR / "parent.aep")
        comp = project.compositions[0]
        # Find the child layer (should have parent_id set)
        child_layer = None
        for layer in comp.layers:
            if layer.parent_id is not None:
                child_layer = layer
                break
        assert child_layer is not None
        assert child_layer.parent_id is not None
        # Find matching layer in JSON
        for item in expected["items"]:
            if "layers" in item:
                for layer_json in item["layers"]:
                    if layer_json.get("parent") is not None:
                        # Verify parent index matches
                        assert child_layer.parent_id == layer_json["parent"]


class TestTimeRemap:
    """Tests for time remap."""

    def test_timeRemapEnabled_true(self) -> None:
        """Test time remap enabled."""
        expected = load_expected("timeRemapEnabled_true")
        project = parse_project(SAMPLES_DIR / "timeRemapEnabled_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        # JSON shows timeRemapEnabled=True
        assert layer_json["timeRemapEnabled"] is True
        assert layer.time_remap_enabled == layer_json["timeRemapEnabled"]


class TestAudio:
    """Tests for audio attributes."""

    def test_audioEnabled_true(self) -> None:
        """Test audio enabled."""
        expected = load_expected("audioEnabled_true")
        project = parse_project(SAMPLES_DIR / "audioEnabled_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["audioEnabled"] is True
        assert layer.audio_enabled == layer_json["audioEnabled"]

    def test_audioEnabled_false(self) -> None:
        """Test audio disabled."""
        expected = load_expected("audioEnabled_false")
        project = parse_project(SAMPLES_DIR / "audioEnabled_false.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["audioEnabled"] is False
        assert layer.audio_enabled == layer_json["audioEnabled"]
