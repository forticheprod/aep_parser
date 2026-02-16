"""Tests for Layer model parsing."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
from conftest import (
    get_first_layer,
    get_layer_from_json,
    get_sample_files,
    load_expected,
    parse_project,
)

from aep_parser import Project
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


@pytest.mark.parametrize("sample_name", get_sample_files(SAMPLES_DIR))
def test_parse_layer_sample(sample_name: str) -> None:
    """Each layer sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


class TestLayerBasic:
    """Tests for basic layer attributes."""

    def test_enabled_false(self) -> None:
        expected = load_expected(SAMPLES_DIR, "enabled_false")
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["enabled"] is False
        assert layer.enabled == layer_json["enabled"]

    def test_locked_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "locked_true")
        project = parse_project(SAMPLES_DIR / "locked_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["locked"] is True
        assert layer.locked == layer_json["locked"]

    def test_shy_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "shy_true")
        project = parse_project(SAMPLES_DIR / "shy_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["shy"] is True
        assert layer.shy == layer_json["shy"]

    def test_solo_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "solo_true")
        project = parse_project(SAMPLES_DIR / "solo_true.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["solo"] is True
        assert layer.solo == layer_json["solo"]

    def test_name_renamed(self) -> None:
        expected = load_expected(SAMPLES_DIR, "name_renamed")
        project = parse_project(SAMPLES_DIR / "name_renamed.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer.name == layer_json["name"] == "RenamedLayer"

    def test_comment(self) -> None:
        expected = load_expected(SAMPLES_DIR, "comment")
        project = parse_project(SAMPLES_DIR / "comment.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer.comment == layer_json["comment"] == "Test layer comment"

    def test_label_3(self) -> None:
        expected = load_expected(SAMPLES_DIR, "label_3")
        project = parse_project(SAMPLES_DIR / "label_3.aep")
        layer = get_first_layer(project)
        layer_json = get_layer_from_json(expected)
        assert layer_json["label"] == 3
        assert layer.label.value == layer_json["label"]


class TestLayerTiming:
    """Tests for layer timing attributes."""

    def test_startTime_5(self) -> None:
        expected = load_expected(SAMPLES_DIR, "startTime_5")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "startTime_5.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer_json["startTime"] == 5
        assert math.isclose(layer.start_time, layer_json["startTime"])

    def test_inPoint_5(self) -> None:
        expected = load_expected(SAMPLES_DIR, "inPoint_5")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "inPoint_5.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer_json["inPoint"] == 5
        assert math.isclose(layer.in_point, layer_json["inPoint"])

    def test_outPoint_10(self) -> None:
        expected = load_expected(SAMPLES_DIR, "outPoint_10")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "outPoint_10.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer_json["outPoint"] == 10
        assert math.isclose(layer.out_point, layer_json["outPoint"])

    def test_stretch_200(self) -> None:
        expected = load_expected(SAMPLES_DIR, "stretch_200")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "stretch_200.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer_json["stretch"] == 200
        assert math.isclose(layer.stretch, layer_json["stretch"])

    def test_stretch_minus100(self) -> None:
        expected = load_expected(SAMPLES_DIR, "stretch_minus100")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "stretch_minus100.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer_json["stretch"] == -100
        assert math.isclose(layer.stretch, layer_json["stretch"])


class TestTimingEdgeCases:
    """Tests for outPoint/inPoint clamping with precomp sources."""

    def test_outPoint_clamp_precomp(self) -> None:
        """Precomp dur=5s, main comp=30s. OutPoint clamped to 5."""
        expected = load_expected(SAMPLES_DIR, "outPoint_clamp_precomp")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "outPoint_clamp_precomp.aep"))
        layer_json = get_layer_from_json(expected)
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 5.0, abs_tol=0.001)

    def test_outPoint_clamp_stretch_200(self) -> None:
        """Precomp dur=5s, stretch=200%. OutPoint clamped to 10."""
        expected = load_expected(SAMPLES_DIR, "outPoint_clamp_stretch_200")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "outPoint_clamp_stretch_200.aep"))
        layer_json = get_layer_from_json(expected)
        assert math.isclose(layer.stretch, 200.0)
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 10.0, abs_tol=0.001)

    def test_outPoint_clamp_stretch_400(self) -> None:
        """Precomp dur=5s, stretch=400%. OutPoint clamped to 20."""
        expected = load_expected(SAMPLES_DIR, "outPoint_clamp_stretch_400")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "outPoint_clamp_stretch_400.aep"))
        layer_json = get_layer_from_json(expected)
        assert math.isclose(layer.stretch, 400.0)
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 20.0, abs_tol=0.001)

    def test_outPoint_clamp_collapse(self) -> None:
        """Precomp dur=5s, collapse=True. AE still clamps to 5."""
        expected = load_expected(SAMPLES_DIR, "outPoint_no_clamp_collapse")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "outPoint_no_clamp_collapse.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.collapse_transformation is True
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 5.0, abs_tol=0.001)

    def test_outPoint_no_clamp_timeRemap(self) -> None:
        """Precomp dur=5s, timeRemap=True. OutPoint NOT clamped (stays 30)."""
        expected = load_expected(SAMPLES_DIR, "outPoint_no_clamp_timeRemap")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "outPoint_no_clamp_timeRemap.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.time_remap_enabled is True
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 30.0, abs_tol=0.001)

    def test_outPoint_no_clamp_negative_stretch(self) -> None:
        """Precomp dur=5s, stretch=-100%. Clamping skipped."""
        expected = load_expected(SAMPLES_DIR, "outPoint_no_clamp_negative_stretch")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "outPoint_no_clamp_negative_stretch.aep"))
        layer_json = get_layer_from_json(expected)
        assert math.isclose(layer.stretch, -100.0)
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)

    def test_outPoint_clamp_with_startTime(self) -> None:
        """Precomp dur=5s, startTime=3s. OutPoint clamped to 3+5=8."""
        expected = load_expected(SAMPLES_DIR, "outPoint_clamp_with_startTime")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "outPoint_clamp_with_startTime.aep"))
        layer_json = get_layer_from_json(expected)
        assert math.isclose(layer.start_time, 3.0, abs_tol=0.001)
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 8.0, abs_tol=0.001)


class TestLayerTypes:
    """Tests for different layer types."""

    def test_type_camera(self) -> None:
        layer = get_first_layer(parse_project(SAMPLES_DIR / "type_camera.aep"))
        assert layer.layer_type.name == "camera"
        assert isinstance(layer, CameraLayer)

    def test_type_null(self) -> None:
        expected = load_expected(SAMPLES_DIR, "type_null")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "type_null.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer_json["nullLayer"] is True
        assert layer.null_layer == layer_json["nullLayer"]

    def test_type_shape(self) -> None:
        layer = get_first_layer(parse_project(SAMPLES_DIR / "type_shape.aep"))
        assert layer.layer_type.name == "shape"
        assert isinstance(layer, ShapeLayer)

    def test_type_text(self) -> None:
        layer = get_first_layer(parse_project(SAMPLES_DIR / "type_text.aep"))
        assert layer.layer_type.name == "text"
        assert isinstance(layer, TextLayer)


class TestLightTypes:
    """Tests for light layer types."""

    def test_lightType_AMBIENT(self) -> None:
        expected = load_expected(SAMPLES_DIR, "lightType_AMBIENT")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "lightType_AMBIENT.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.light_type == layer_json["lightType"] == LightType.AMBIENT

    def test_lightType_POINT(self) -> None:
        expected = load_expected(SAMPLES_DIR, "lightType_POINT")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "lightType_POINT.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.light_type == layer_json["lightType"] == LightType.POINT

    def test_lightType_SPOT(self) -> None:
        expected = load_expected(SAMPLES_DIR, "lightType_SPOT")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "lightType_SPOT.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.light_type == layer_json["lightType"] == LightType.SPOT

    def test_lightType_PARALLEL(self) -> None:
        expected = load_expected(SAMPLES_DIR, "lightType_PARALLEL")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "lightType_PARALLEL.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.light_type == layer_json["lightType"] == LightType.PARALLEL


class TestAVLayerAttributes:
    """Tests for AVLayer-specific attributes."""

    def test_threeDLayer_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "threeDLayer_true")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "threeDLayer_true.aep"))
        layer_json = get_layer_from_json(expected)
        assert isinstance(layer, AVLayer)
        assert layer_json["threeDLayer"] is True
        assert layer.three_d_layer == layer_json["threeDLayer"]

    def test_adjustmentLayer_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "adjustmentLayer_true")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "adjustmentLayer_true.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.adjustment_layer == layer_json["adjustmentLayer"] is True

    def test_guideLayer_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "guideLayer_true")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "guideLayer_true.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.guide_layer == layer_json["guideLayer"] is True

    def test_collapseTransformation_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "collapseTransformation_true")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "collapseTransformation_true.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.collapse_transformation == layer_json["collapseTransformation"] is True

    def test_preserveTransparency_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "preserveTransparency_true")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "preserveTransparency_true.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.preserve_transparency == layer_json["preserveTransparency"] is True

    def test_motionBlur_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "motionBlur_true")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "motionBlur_true.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.motion_blur == layer_json["motionBlur"] is True

    def test_effectsActive_false(self) -> None:
        expected = load_expected(SAMPLES_DIR, "effectsActive_false")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "effectsActive_false.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer_json["effectsActive"] is False
        assert layer.effects_active == layer_json["effectsActive"]


class TestBlendingModes:
    """Tests for blending mode attributes."""

    def test_blendingMode_ADD(self) -> None:
        expected = load_expected(SAMPLES_DIR, "blendingMode_ADD")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "blendingMode_ADD.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.blending_mode == layer_json["blendingMode"] == BlendingMode.ADD

    def test_blendingMode_MULTIPLY(self) -> None:
        expected = load_expected(SAMPLES_DIR, "blendingMode_MULTIPLY")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "blendingMode_MULTIPLY.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.blending_mode == layer_json["blendingMode"] == BlendingMode.MULTIPLY

    def test_blendingMode_SCREEN(self) -> None:
        expected = load_expected(SAMPLES_DIR, "blendingMode_SCREEN")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "blendingMode_SCREEN.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.blending_mode == layer_json["blendingMode"] == BlendingMode.SCREEN


class TestQualitySettings:
    """Tests for layer quality settings."""

    def test_quality_BEST(self) -> None:
        expected = load_expected(SAMPLES_DIR, "quality_BEST")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "quality_BEST.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.quality == layer_json["quality"] == LayerQuality.BEST

    def test_quality_DRAFT(self) -> None:
        expected = load_expected(SAMPLES_DIR, "quality_DRAFT")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "quality_DRAFT.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.quality == layer_json["quality"] == LayerQuality.DRAFT

    def test_quality_WIREFRAME(self) -> None:
        expected = load_expected(SAMPLES_DIR, "quality_WIREFRAME")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "quality_WIREFRAME.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.quality == layer_json["quality"] == LayerQuality.WIREFRAME

    def test_samplingQuality_BICUBIC(self) -> None:
        expected = load_expected(SAMPLES_DIR, "samplingQuality_BICUBIC")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "samplingQuality_BICUBIC.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.sampling_quality == layer_json["samplingQuality"] == LayerSamplingQuality.BICUBIC


class TestFrameBlending:
    """Tests for frame blending type."""

    def test_frameBlendingType_NO_FRAME_BLEND(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameBlendingType_NO_FRAME_BLEND")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "frameBlendingType_NO_FRAME_BLEND.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.frame_blending_type == layer_json["frameBlendingType"] == FrameBlendingType.NO_FRAME_BLEND
        assert layer.frame_blending is False

    def test_frameBlendingType_FRAME_MIX(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameBlendingType_FRAME_MIX")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "frameBlendingType_FRAME_MIX.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.frame_blending_type == layer_json["frameBlendingType"] == FrameBlendingType.FRAME_MIX

    def test_frameBlendingType_PIXEL_MOTION(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameBlendingType_PIXEL_MOTION")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "frameBlendingType_PIXEL_MOTION.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.frame_blending_type == layer_json["frameBlendingType"] == FrameBlendingType.PIXEL_MOTION


class TestAutoOrient:
    """Tests for auto-orient settings."""

    def test_autoOrient_ALONG_PATH(self) -> None:
        expected = load_expected(SAMPLES_DIR, "autoOrient_ALONG_PATH")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "autoOrient_ALONG_PATH.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.auto_orient == layer_json["autoOrient"] == AutoOrientType.ALONG_PATH

    def test_autoOrient_CAMERA(self) -> None:
        expected = load_expected(SAMPLES_DIR, "autoOrient_CAMERA")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "autoOrient_CAMERA.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.auto_orient == layer_json["autoOrient"] == AutoOrientType.CAMERA_OR_POINT_OF_INTEREST
        assert layer.three_d_layer is True

    def test_autoOrient_CHARACTERS(self) -> None:
        expected = load_expected(SAMPLES_DIR, "autoOrient_CHARACTERS")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "autoOrient_CHARACTERS.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.auto_orient == layer_json["autoOrient"] == AutoOrientType.CHARACTERS_TOWARD_CAMERA
        assert layer.three_d_layer is True


class TestTrackMatte:
    """Tests for track matte settings."""

    def test_trackMatteType_ALPHA(self) -> None:
        expected = load_expected(SAMPLES_DIR, "trackMatteType_ALPHA")
        project = parse_project(SAMPLES_DIR / "trackMatteType_ALPHA.aep")
        comp = project.compositions[0]
        matted_layer = next(
            (layer for layer in comp.layers if layer.track_matte_type == TrackMatteType.ALPHA), None
        )
        expected_layer = None
        for item in expected["items"]:
            if "layers" in item:
                for lj in item["layers"]:
                    if lj.get("trackMatteType") == TrackMatteType.ALPHA:
                        expected_layer = lj
                        break
        assert matted_layer is not None
        assert expected_layer is not None
        assert matted_layer.track_matte_type == expected_layer["trackMatteType"]

    def test_trackMatteType_LUMA(self) -> None:
        expected = load_expected(SAMPLES_DIR, "trackMatteType_LUMA")
        project = parse_project(SAMPLES_DIR / "trackMatteType_LUMA.aep")
        comp = project.compositions[0]
        matted_layer = next(
            (layer for layer in comp.layers if layer.track_matte_type == TrackMatteType.LUMA), None
        )
        expected_layer = None
        for item in expected["items"]:
            if "layers" in item:
                for lj in item["layers"]:
                    if lj.get("trackMatteType") == TrackMatteType.LUMA:
                        expected_layer = lj
                        break
        assert matted_layer is not None
        assert expected_layer is not None
        assert matted_layer.track_matte_type == expected_layer["trackMatteType"]


class TestParenting:
    """Tests for layer parenting."""

    def test_parent(self) -> None:
        expected = load_expected(SAMPLES_DIR, "parent")
        project = parse_project(SAMPLES_DIR / "parent.aep")
        comp = project.compositions[0]
        child_layer = next((layer for layer in comp.layers if layer.parent_id is not None), None)
        assert child_layer is not None
        for item in expected["items"]:
            if "layers" in item:
                for layer_json in item["layers"]:
                    if layer_json.get("parent") is not None:
                        assert child_layer.parent_id == layer_json["parent"]


class TestTimeRemap:
    """Tests for time remap."""

    def test_timeRemapEnabled_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "timeRemapEnabled_true")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "timeRemapEnabled_true.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer_json["timeRemapEnabled"] is True
        assert layer.time_remap_enabled == layer_json["timeRemapEnabled"]


class TestAudio:
    """Tests for audio attributes."""

    def test_audioEnabled_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "audioEnabled_true")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "audioEnabled_true.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer.audio_enabled == layer_json["audioEnabled"] is True

    def test_audioEnabled_false(self) -> None:
        expected = load_expected(SAMPLES_DIR, "audioEnabled_false")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "audioEnabled_false.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer_json["audioEnabled"] is False
        assert layer.audio_enabled == layer_json["audioEnabled"]
