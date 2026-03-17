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
from aep_parser.enums import (
    AutoOrientType,
    BlendingMode,
    FrameBlendingType,
    LayerQuality,
    LayerSamplingQuality,
    LightType,
    PropertyType,
    TrackMatteType,
)
from aep_parser.models.layers import (
    AVLayer,
    CameraLayer,
    LightLayer,
    ShapeLayer,
    TextLayer,
)
from aep_parser.models.layers.three_d_model_layer import ThreeDModelLayer
from aep_parser.models.properties.property_base import PropertyBase
from aep_parser.models.properties.property_group import PropertyGroup

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "layer"
BUGS_DIR = Path(__file__).parent.parent / "samples" / "bugs"


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
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "outPoint_clamp_precomp.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 5.0, abs_tol=0.001)

    def test_outPoint_clamp_stretch_200(self) -> None:
        """Precomp dur=5s, stretch=200%. OutPoint clamped to 10."""
        expected = load_expected(SAMPLES_DIR, "outPoint_clamp_stretch_200")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "outPoint_clamp_stretch_200.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert math.isclose(layer.stretch, 200.0)
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 10.0, abs_tol=0.001)

    def test_outPoint_clamp_stretch_400(self) -> None:
        """Precomp dur=5s, stretch=400%. OutPoint clamped to 20."""
        expected = load_expected(SAMPLES_DIR, "outPoint_clamp_stretch_400")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "outPoint_clamp_stretch_400.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert math.isclose(layer.stretch, 400.0)
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 20.0, abs_tol=0.001)

    def test_outPoint_clamp_collapse(self) -> None:
        """Precomp dur=5s, collapse=True. AE still clamps to 5."""
        expected = load_expected(SAMPLES_DIR, "outPoint_no_clamp_collapse")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "outPoint_no_clamp_collapse.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert layer.collapse_transformation is True
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 5.0, abs_tol=0.001)

    def test_outPoint_no_clamp_timeRemap(self) -> None:
        """Precomp dur=5s, timeRemap=True. OutPoint NOT clamped (stays 30)."""
        expected = load_expected(SAMPLES_DIR, "outPoint_no_clamp_timeRemap")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "outPoint_no_clamp_timeRemap.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert layer.time_remap_enabled is True
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 30.0, abs_tol=0.001)

    def test_outPoint_no_clamp_negative_stretch(self) -> None:
        """Precomp dur=5s, stretch=-100%. Clamping skipped."""
        expected = load_expected(SAMPLES_DIR, "outPoint_no_clamp_negative_stretch")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "outPoint_no_clamp_negative_stretch.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert math.isclose(layer.stretch, -100.0)
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)

    def test_outPoint_clamp_with_startTime(self) -> None:
        """Precomp dur=5s, startTime=3s. OutPoint clamped to 3+5=8."""
        expected = load_expected(SAMPLES_DIR, "outPoint_clamp_with_startTime")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "outPoint_clamp_with_startTime.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert math.isclose(layer.start_time, 3.0, abs_tol=0.001)
        assert math.isclose(layer.out_point, layer_json["outPoint"], abs_tol=0.001)
        assert math.isclose(layer.out_point, 8.0, abs_tol=0.001)


class TestLayerTypes:
    """Tests for different layer types."""

    def test_type_camera(self) -> None:
        layer = get_first_layer(parse_project(SAMPLES_DIR / "type_camera.aep"))
        assert layer.layer_type == "CameraLayer"
        assert isinstance(layer, CameraLayer)

    def test_type_null(self) -> None:
        expected = load_expected(SAMPLES_DIR, "type_null")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "type_null.aep"))
        layer_json = get_layer_from_json(expected)
        assert layer_json["nullLayer"] is True
        assert layer.null_layer == layer_json["nullLayer"]

    def test_type_shape(self) -> None:
        layer = get_first_layer(parse_project(SAMPLES_DIR / "type_shape.aep"))
        assert layer.layer_type == "Layer"
        assert isinstance(layer, ShapeLayer)

    def test_type_text(self) -> None:
        layer = get_first_layer(parse_project(SAMPLES_DIR / "type_text.aep"))
        assert layer.layer_type == "Layer"
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

    def test_lightType_ENVIRONMENT(self) -> None:
        project = parse_project(SAMPLES_DIR / "light_source_default.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, LightLayer)
        assert layer.light_type == LightType.ENVIRONMENT


class TestLightSource:
    """Tests for LightLayer.light_source."""

    def test_light_source_default_is_none(self) -> None:
        project = parse_project(SAMPLES_DIR / "light_source_default.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, LightLayer)
        assert layer.light_source is None

    def test_light_source_mov(self) -> None:
        project = parse_project(SAMPLES_DIR / "light_source_mov_23_976.mov.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, LightLayer)
        assert layer.light_source is not None
        assert isinstance(layer.light_source, AVLayer)
        assert layer.light_source.name == "mov_23_976.mov"


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
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "collapseTransformation_true.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert (
            layer.collapse_transformation
            == layer_json["collapseTransformation"]
            is True
        )

    def test_preserveTransparency_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "preserveTransparency_true")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "preserveTransparency_true.aep")
        )
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
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "blendingMode_MULTIPLY.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert (
            layer.blending_mode == layer_json["blendingMode"] == BlendingMode.MULTIPLY
        )

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
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "samplingQuality_BICUBIC.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert (
            layer.sampling_quality
            == layer_json["samplingQuality"]
            == LayerSamplingQuality.BICUBIC
        )


class TestFrameBlending:
    """Tests for frame blending type."""

    def test_frameBlendingType_NO_FRAME_BLEND(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameBlendingType_NO_FRAME_BLEND")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "frameBlendingType_NO_FRAME_BLEND.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert (
            layer.frame_blending_type
            == layer_json["frameBlendingType"]
            == FrameBlendingType.NO_FRAME_BLEND
        )
        assert layer.frame_blending is False

    def test_frameBlendingType_FRAME_MIX(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameBlendingType_FRAME_MIX")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "frameBlendingType_FRAME_MIX.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert (
            layer.frame_blending_type
            == layer_json["frameBlendingType"]
            == FrameBlendingType.FRAME_MIX
        )

    def test_frameBlendingType_PIXEL_MOTION(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameBlendingType_PIXEL_MOTION")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "frameBlendingType_PIXEL_MOTION.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert (
            layer.frame_blending_type
            == layer_json["frameBlendingType"]
            == FrameBlendingType.PIXEL_MOTION
        )


class TestAutoOrient:
    """Tests for auto-orient settings."""

    def test_autoOrient_ALONG_PATH(self) -> None:
        expected = load_expected(SAMPLES_DIR, "autoOrient_ALONG_PATH")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "autoOrient_ALONG_PATH.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert (
            layer.auto_orient == layer_json["autoOrient"] == AutoOrientType.ALONG_PATH
        )

    def test_autoOrient_CAMERA(self) -> None:
        expected = load_expected(SAMPLES_DIR, "autoOrient_CAMERA")
        layer = get_first_layer(parse_project(SAMPLES_DIR / "autoOrient_CAMERA.aep"))
        layer_json = get_layer_from_json(expected)
        assert (
            layer.auto_orient
            == layer_json["autoOrient"]
            == AutoOrientType.CAMERA_OR_POINT_OF_INTEREST
        )
        assert layer.three_d_layer is True

    def test_autoOrient_CHARACTERS(self) -> None:
        expected = load_expected(SAMPLES_DIR, "autoOrient_CHARACTERS")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "autoOrient_CHARACTERS.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert (
            layer.auto_orient
            == layer_json["autoOrient"]
            == AutoOrientType.CHARACTERS_TOWARD_CAMERA
        )
        assert layer.three_d_layer is True


class TestTrackMatte:
    """Tests for track matte settings."""

    def test_trackMatteType_ALPHA(self) -> None:
        expected = load_expected(SAMPLES_DIR, "trackMatteType_ALPHA")
        project = parse_project(SAMPLES_DIR / "trackMatteType_ALPHA.aep")
        comp = project.compositions[0]
        matted_layer = next(
            (
                layer
                for layer in comp.layers
                if layer.track_matte_type == TrackMatteType.ALPHA
            ),
            None,
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
            (
                layer
                for layer in comp.layers
                if layer.track_matte_type == TrackMatteType.LUMA
            ),
            None,
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

    def test_has_track_matte(self) -> None:
        expected = load_expected(SAMPLES_DIR, "track_matte_yes")
        project = parse_project(SAMPLES_DIR / "track_matte_yes.aep")
        comp = project.compositions[0]
        expected_layers = None
        for item in expected["items"]:
            if "layers" in item:
                expected_layers = item["layers"]
                break
        assert expected_layers is not None
        for layer, exp in zip(comp.layers, expected_layers):
            assert layer.has_track_matte == exp["hasTrackMatte"]

    def test_has_track_matte_false(self) -> None:
        expected = load_expected(SAMPLES_DIR, "track_matte_no")
        project = parse_project(SAMPLES_DIR / "track_matte_no.aep")
        comp = project.compositions[0]
        expected_layers = None
        for item in expected["items"]:
            if "layers" in item:
                expected_layers = item["layers"]
                break
        assert expected_layers is not None
        for layer in comp.layers:
            assert layer.has_track_matte is False

    def test_is_track_matte(self) -> None:
        expected = load_expected(SAMPLES_DIR, "track_matte_yes")
        project = parse_project(SAMPLES_DIR / "track_matte_yes.aep")
        comp = project.compositions[0]
        expected_layers = None
        for item in expected["items"]:
            if "layers" in item:
                expected_layers = item["layers"]
                break
        assert expected_layers is not None
        for layer, exp in zip(comp.layers, expected_layers):
            assert layer.is_track_matte == exp["isTrackMatte"]

    def test_is_track_matte_false(self) -> None:
        project = parse_project(SAMPLES_DIR / "track_matte_no.aep")
        comp = project.compositions[0]
        for layer in comp.layers:
            assert layer.is_track_matte is False

    def test_track_matte_layer(self) -> None:
        project = parse_project(SAMPLES_DIR / "track_matte_yes.aep")
        comp = project.compositions[0]
        matted_layer = next(
            (layer for layer in comp.layers if layer.has_track_matte), None
        )
        assert matted_layer is not None
        assert matted_layer.track_matte_layer is not None
        assert matted_layer.track_matte_layer.is_track_matte is True

    def test_track_matte_layer_none(self) -> None:
        project = parse_project(SAMPLES_DIR / "track_matte_no.aep")
        comp = project.compositions[0]
        for layer in comp.layers:
            assert layer.track_matte_layer is None


class TestParenting:
    """Tests for layer parenting."""

    def test_parent(self) -> None:
        expected = load_expected(SAMPLES_DIR, "parent")
        project = parse_project(SAMPLES_DIR / "parent.aep")
        comp = project.compositions[0]
        child_layer = next(
            (layer for layer in comp.layers if layer._parent_id != 0), None
        )
        assert child_layer is not None
        for item in expected["items"]:
            if "layers" in item:
                for layer_json in item["layers"]:
                    if layer_json.get("parent") is not None:
                        assert child_layer._parent_id == layer_json["parent"]


class TestTimeRemap:
    """Tests for time remap."""

    def test_timeRemapEnabled_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "timeRemapEnabled_true")
        layer = get_first_layer(
            parse_project(SAMPLES_DIR / "timeRemapEnabled_true.aep")
        )
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


class TestLayerNameEncoding:
    """Regression tests for layer name encoding edge cases."""

    def test_non_ascii_layer_name(self) -> None:
        """Layer names with non-ASCII characters (e.g. ≈) should parse without error.

        Regression test for windows-1250 decoding error: byte 0x98 is undefined
        in windows-1250 but valid in windows-1252.
        """
        expected = load_expected(BUGS_DIR, "windows-1250_decoding_error")
        layer = get_first_layer(
            parse_project(BUGS_DIR / "windows-1250_decoding_error.aep")
        )
        layer_json = get_layer_from_json(expected)
        assert layer.name == layer_json["name"]
        assert layer.name == "\u2248"


class TestActiveAtTime:
    """Tests for Layer.active_at_time() method."""

    def test_enabled_layer_within_range(self) -> None:
        """An enabled, non-soloed layer returns True inside its in/out range."""
        project = parse_project(SAMPLES_DIR / "startTime_5.aep")
        layer = get_first_layer(project)
        assert layer.enabled is True
        midpoint = (layer.in_point + layer.out_point) / 2
        assert layer.active_at_time(midpoint) is True

    def test_at_in_point(self) -> None:
        """Layer is active exactly at its in_point (inclusive)."""
        project = parse_project(SAMPLES_DIR / "inPoint_5.aep")
        layer = get_first_layer(project)
        assert layer.active_at_time(layer.in_point) is True

    def test_at_out_point(self) -> None:
        """Layer is not active at its out_point (exclusive)."""
        project = parse_project(SAMPLES_DIR / "inPoint_5.aep")
        layer = get_first_layer(project)
        assert layer.active_at_time(layer.out_point) is False

    def test_before_in_point(self) -> None:
        """Layer is not active before its in_point."""
        project = parse_project(SAMPLES_DIR / "inPoint_5.aep")
        layer = get_first_layer(project)
        assert layer.active_at_time(layer.in_point - 1) is False

    def test_disabled_layer(self) -> None:
        """A disabled layer is never active."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert layer.enabled is False
        midpoint = (layer.in_point + layer.out_point) / 2
        assert layer.active_at_time(midpoint) is False

    def test_solo_layer_active(self) -> None:
        """A soloed layer is active within its time range."""
        project = parse_project(SAMPLES_DIR / "solo_true.aep")
        layer = get_first_layer(project)
        assert layer.solo is True
        midpoint = (layer.in_point + layer.out_point) / 2
        assert layer.active_at_time(midpoint) is True

    def test_non_solo_layer_inactive_when_other_is_soloed(self) -> None:
        """A non-soloed layer is inactive when another layer in the comp is soloed."""
        project = parse_project(SAMPLES_DIR / "solo_true.aep")
        comp = project.compositions[0]
        non_solo_layers = [lyr for lyr in comp.layers if not lyr.solo]
        if non_solo_layers:
            layer = non_solo_layers[0]
            midpoint = (layer.in_point + layer.out_point) / 2
            assert layer.active_at_time(midpoint) is False


class TestLayerPropertyGroupInheritance:
    """Tests for Layer's PropertyGroup / PropertyBase inheritance."""

    def test_layer_is_property_group(self) -> None:
        """Layer is an instance of PropertyGroup."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, PropertyGroup)

    def test_layer_is_property_base(self) -> None:
        """Layer is an instance of PropertyBase."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, PropertyBase)

    def test_property_depth_is_zero(self) -> None:
        """Layers are at depth 0 (root of the property hierarchy)."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert layer.property_depth == 0

    def test_property_type_named_group(self) -> None:
        """Layer property_type is NAMED_GROUP."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert layer.property_type == PropertyType.NAMED_GROUP

    def test_av_layer_match_name(self) -> None:
        """AVLayer has the correct ExtendScript match name."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, AVLayer)
        assert layer.match_name == "ADBE AV Layer"

    def test_properties_contains_transform(self) -> None:
        """Layer.properties includes the Transform group."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        match_names = [p.match_name for p in layer.properties]
        assert "ADBE Transform Group" in match_names

    def test_transform_accessor(self) -> None:
        """Layer.transform returns the Transform PropertyGroup."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert isinstance(layer.transform, PropertyGroup)
        assert layer.transform.match_name == "ADBE Transform Group"

    def test_effects_none_when_no_effects(self) -> None:
        """Layer.effects is None when there are no effects."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        # Basic layer without effects
        assert layer.effects is None

    def test_num_properties_positive(self) -> None:
        """Layer.num_properties returns the count of top-level property groups."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert layer.num_properties == len(layer.properties)
        assert layer.num_properties > 0

    def test_active_property(self) -> None:
        """Layer.active reflects active_at_time(time)."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert layer.active == layer.active_at_time(layer.time)

    def test_identity_equality(self) -> None:
        """Two Layer objects are only equal when they are the same object."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert layer == layer
        # A copy (different object) should not be equal
        assert layer != object()

    def test_transform_is_same_object_in_properties(self) -> None:
        """Layer.transform returns the same PropertyGroup as in properties list."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        transform_from_list = next(
            p for p in layer.properties if p.match_name == "ADBE Transform Group"
        )
        assert layer.transform is transform_from_list

    def test_len_equals_num_properties(self) -> None:
        """len(layer) equals layer.num_properties."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert len(layer) == layer.num_properties
        assert len(layer) == len(layer.properties)

    def test_getitem_by_int_index(self) -> None:
        """layer[0] returns the first child property group."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        assert layer[0] is layer.properties[0]

    def test_getitem_by_match_name(self) -> None:
        """layer['ADBE Transform Group'] returns the Transform group."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        result = layer["ADBE Transform Group"]
        assert isinstance(result, PropertyGroup)
        assert result.match_name == "ADBE Transform Group"
        assert result is layer.transform

    def test_getitem_by_display_name(self) -> None:
        """layer['Transform'] returns the Transform group by display name."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        result = layer["Transform"]
        assert isinstance(result, PropertyGroup)
        assert result.match_name == "ADBE Transform Group"

    def test_getitem_chained(self) -> None:
        """layer['ADBE Transform Group']['ADBE Position'] chains correctly."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        transform = layer["ADBE Transform Group"]
        position = transform["ADBE Position"]
        assert position.match_name == "ADBE Position"

    def test_getitem_key_error(self) -> None:
        """layer['nonexistent'] raises KeyError."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        with pytest.raises(KeyError):
            layer["nonexistent_match_name"]

    def test_getitem_index_error(self) -> None:
        """layer[9999] raises IndexError."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        with pytest.raises(IndexError):
            layer[9999]

    def test_getitem_type_error(self) -> None:
        """layer[1.5] raises TypeError."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        with pytest.raises(TypeError):
            layer[1.5]  # type: ignore[index]

    def test_getattr_single_word(self) -> None:
        """layer.transform.position resolves via __getattr__."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        position = layer.transform.position  # type: ignore[attr-defined]
        assert position.match_name == "ADBE Position"

    def test_getattr_multi_word(self) -> None:
        """layer.transform.anchor_point resolves 'Anchor Point'."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        anchor = layer.transform.anchor_point  # type: ignore[attr-defined]
        assert anchor.match_name == "ADBE Anchor Point"

    def test_getattr_attribute_error(self) -> None:
        """Accessing a nonexistent child raises AttributeError."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        with pytest.raises(AttributeError):
            layer.transform.nonexistent  # type: ignore[attr-defined]  # noqa: B018

    def test_getattr_does_not_shadow_fields(self) -> None:
        """Dataclass fields take priority over __getattr__."""
        project = parse_project(SAMPLES_DIR / "enabled_false.aep")
        layer = get_first_layer(project)
        # 'name' is a dataclass field, should NOT look in children
        assert isinstance(layer.transform.name, str)


class TestThreeDModelLayer:
    """Tests for ThreeDModelLayer parsing."""

    def test_isinstance(self) -> None:
        """ThreeDModelLayer inherits from AVLayer."""
        project = parse_project(SAMPLES_DIR / "three_d_model_layer.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, ThreeDModelLayer)
        assert isinstance(layer, AVLayer)

    def test_match_name(self) -> None:
        """ThreeDModelLayer match_name is 'ADBE 3D Model Layer'."""
        project = parse_project(SAMPLES_DIR / "three_d_model_layer.aep")
        layer = get_first_layer(project)
        assert layer.match_name == "ADBE 3D Model Layer"

    def test_layer_type(self) -> None:
        """ThreeDModelLayer layer_type is 'Layer'."""
        project = parse_project(SAMPLES_DIR / "three_d_model_layer.aep")
        layer = get_first_layer(project)
        assert layer.layer_type == "Layer"

    def test_three_d_layer(self) -> None:
        """ThreeDModelLayer always reports three_d_layer=True."""
        project = parse_project(SAMPLES_DIR / "three_d_model_layer.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, ThreeDModelLayer)
        assert layer.three_d_layer is True

    def test_collapse_transformation(self) -> None:
        """ThreeDModelLayer has collapse_transformation=True."""
        project = parse_project(SAMPLES_DIR / "three_d_model_layer.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, ThreeDModelLayer)
        assert layer.collapse_transformation is True

    def test_source_is_footage(self) -> None:
        """ThreeDModelLayer source is a FootageItem."""
        project = parse_project(SAMPLES_DIR / "three_d_model_layer.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, ThreeDModelLayer)
        assert layer.source is not None
        assert layer.source.name == "crystal.fbx"

    def test_comp_three_d_model_layers(self) -> None:
        """CompItem.three_d_model_layers filters correctly."""
        project = parse_project(SAMPLES_DIR / "three_d_model_layer.aep")
        comp = project.compositions[0]
        assert len(comp.three_d_model_layers) == 1
        assert isinstance(comp.three_d_model_layers[0], ThreeDModelLayer)

    def test_can_set_collapse_transformation(self) -> None:
        """ThreeDModelLayer.can_set_collapse_transformation is always True."""
        project = parse_project(SAMPLES_DIR / "three_d_model_layer.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, ThreeDModelLayer)
        assert layer.can_set_collapse_transformation is True

    def test_can_set_time_remap_enabled(self) -> None:
        """ThreeDModelLayer.can_set_time_remap_enabled is always False."""
        project = parse_project(SAMPLES_DIR / "three_d_model_layer.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, ThreeDModelLayer)
        assert layer.can_set_time_remap_enabled is False


class TestThreeDPerChar:
    """Tests for AVLayer.three_d_per_char attribute."""

    def test_three_d_per_char_on(self) -> None:
        """three_d_per_char is True when per-character 3D is enabled."""
        project = parse_project(SAMPLES_DIR / "threeDPerChar_on.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, AVLayer)
        assert layer.three_d_per_char is True

    def test_three_d_per_char_off(self) -> None:
        """three_d_per_char is False when per-character 3D is disabled."""
        project = parse_project(SAMPLES_DIR / "threeDPerChar_off.aep")
        layer = get_first_layer(project)
        assert isinstance(layer, AVLayer)
        assert layer.three_d_per_char is False
