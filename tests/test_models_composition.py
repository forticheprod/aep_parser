"""Tests for CompItem model parsing."""
from __future__ import annotations

import math
from pathlib import Path

import pytest
from conftest import get_comp_from_json, get_sample_files, load_expected, parse_project

from aep_parser import Project

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "composition"


@pytest.mark.parametrize("sample_name", get_sample_files(SAMPLES_DIR))
def test_parse_composition_sample(sample_name: str) -> None:
    """Each composition sample parses and has at least one composition."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)
    assert len(project.compositions) >= 1


class TestCompItemBasic:
    """Tests for basic composition attributes."""

    def test_bgColor_red(self) -> None:
        expected = load_expected(SAMPLES_DIR, "bgColor_red")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "bgColor_red.aep").compositions[0]
        assert math.isclose(comp.bg_color[0], comp_json["bgColor"][0])
        assert math.isclose(comp.bg_color[1], comp_json["bgColor"][1])
        assert math.isclose(comp.bg_color[2], comp_json["bgColor"][2])

    def test_bgColor_custom(self) -> None:
        expected = load_expected(SAMPLES_DIR, "bgColor_custom")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "bgColor_custom.aep").compositions[0]
        assert math.isclose(comp.bg_color[0], comp_json["bgColor"][0])
        assert math.isclose(comp.bg_color[1], comp_json["bgColor"][1])
        assert math.isclose(comp.bg_color[2], comp_json["bgColor"][2])


class TestCompItemSize:
    """Tests for composition size attributes."""

    def test_size_1920x1080(self) -> None:
        expected = load_expected(SAMPLES_DIR, "size_1920x1080")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "size_1920x1080.aep").compositions[0]
        assert comp.width == comp_json["width"] == 1920
        assert comp.height == comp_json["height"] == 1080

    def test_size_2048x872(self) -> None:
        expected = load_expected(SAMPLES_DIR, "size_2048x872")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "size_2048x872.aep").compositions[0]
        assert comp.width == comp_json["width"] == 2048
        assert comp.height == comp_json["height"] == 872


class TestCompItemFrameRate:
    """Tests for composition frame rate."""

    def test_frameRate_23976(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameRate_23976")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "frameRate_23976.aep").compositions[0]
        assert math.isclose(comp.frame_rate, comp_json["frameRate"], rel_tol=0.001)

    def test_frameRate_30(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameRate_30")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "frameRate_30.aep").compositions[0]
        assert comp_json["frameRate"] == 30
        assert math.isclose(comp.frame_rate, comp_json["frameRate"], rel_tol=0.001)

    def test_frameRate_60(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameRate_60")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "frameRate_60.aep").compositions[0]
        assert comp_json["frameRate"] == 60
        assert math.isclose(comp.frame_rate, comp_json["frameRate"], rel_tol=0.001)


class TestCompItemDuration:
    """Tests for composition duration."""

    def test_duration_60(self) -> None:
        expected = load_expected(SAMPLES_DIR, "duration_60")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "duration_60.aep").compositions[0]
        assert comp_json["duration"] == 60
        assert math.isclose(comp.duration, comp_json["duration"])


class TestCompItemMotionBlur:
    """Tests for motion blur attributes."""

    def test_motionBlur_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "motionBlur_true")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "motionBlur_true.aep").compositions[0]
        assert comp_json["motionBlur"] is True
        assert comp.motion_blur == comp_json["motionBlur"]

    def test_shutterAngle_180(self) -> None:
        expected = load_expected(SAMPLES_DIR, "shutterAngle_180")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "shutterAngle_180.aep").compositions[0]
        assert comp.shutter_angle == comp_json["shutterAngle"] == 180

    def test_shutterAngle_360(self) -> None:
        expected = load_expected(SAMPLES_DIR, "shutterAngle_360")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "shutterAngle_360.aep").compositions[0]
        assert comp.shutter_angle == comp_json["shutterAngle"] == 360

    def test_shutterPhase_minus90(self) -> None:
        expected = load_expected(SAMPLES_DIR, "shutterPhase_minus90")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "shutterPhase_minus90.aep").compositions[0]
        assert comp.shutter_phase == comp_json["shutterPhase"] == -90

    def test_motionBlurSamplesPerFrame_32(self) -> None:
        expected = load_expected(SAMPLES_DIR, "motionBlurSamplesPerFrame_32")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "motionBlurSamplesPerFrame_32.aep").compositions[0]
        assert comp.motion_blur_samples_per_frame == comp_json["motionBlurSamplesPerFrame"] == 32

    def test_motionBlurAdaptiveSampleLimit_256(self) -> None:
        expected = load_expected(SAMPLES_DIR, "motionBlurAdaptiveSampleLimit_256")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "motionBlurAdaptiveSampleLimit_256.aep").compositions[0]
        assert comp.motion_blur_adaptive_sample_limit == comp_json["motionBlurAdaptiveSampleLimit"] == 256


class TestCompItemResolution:
    """Tests for resolution attributes."""

    def test_resolutionFactor_half(self) -> None:
        expected = load_expected(SAMPLES_DIR, "resolutionFactor_half")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "resolutionFactor_half.aep").compositions[0]
        assert comp.resolution_factor == comp_json["resolutionFactor"]

    def test_resolutionFactor_quarter(self) -> None:
        expected = load_expected(SAMPLES_DIR, "resolutionFactor_quarter")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "resolutionFactor_quarter.aep").compositions[0]
        assert comp.resolution_factor == comp_json["resolutionFactor"]


class TestCompItemNestedOptions:
    """Tests for nested composition options."""

    def test_preserveNestedFrameRate_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "preserveNestedFrameRate_true")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "preserveNestedFrameRate_true.aep").compositions[0]
        assert comp_json["preserveNestedFrameRate"] is True
        assert comp.preserve_nested_frame_rate == comp_json["preserveNestedFrameRate"]

    def test_preserveNestedResolution_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "preserveNestedResolution_true")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "preserveNestedResolution_true.aep").compositions[0]
        assert comp_json["preserveNestedResolution"] is True
        assert comp.preserve_nested_resolution == comp_json["preserveNestedResolution"]


class TestCompItemFrameBlending:
    """Tests for frame blending attribute."""

    def test_frameBlending_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameBlending_true")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "frameBlending_true.aep").compositions[0]
        assert comp_json["frameBlending"] is True
        assert comp.frame_blending == comp_json["frameBlending"]


class TestCompItemShyLayers:
    """Tests for hide shy layers attribute."""

    def test_hideShyLayers_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "hideShyLayers_true")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "hideShyLayers_true.aep").compositions[0]
        assert comp_json["hideShyLayers"] is True
        assert comp.hide_shy_layers == comp_json["hideShyLayers"]


class TestCompItemTime:
    """Tests for time-related attributes (rel_tol=0.001 for precision)."""

    def test_time_0(self) -> None:
        expected = load_expected(SAMPLES_DIR, "time_0")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "time_0.aep").compositions[0]
        assert comp_json["time"] == 0
        assert math.isclose(comp.time, comp_json["time"])

    def test_time_5(self) -> None:
        expected = load_expected(SAMPLES_DIR, "time_5")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "time_5.aep").compositions[0]
        assert math.isclose(comp.time, comp_json["time"], rel_tol=0.001)

    def test_time_15(self) -> None:
        expected = load_expected(SAMPLES_DIR, "time_15")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "time_15.aep").compositions[0]
        assert math.isclose(comp.time, comp_json["time"], rel_tol=0.001)


class TestCompItemWorkArea:
    """Tests for work area attributes (rel_tol=0.001 for precision)."""

    def test_workAreaStart_5(self) -> None:
        expected = load_expected(SAMPLES_DIR, "workAreaStart_5")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "workAreaStart_5.aep").compositions[0]
        assert math.isclose(comp.in_point, comp_json["workAreaStart"], rel_tol=0.001)

    def test_workAreaDuration_10(self) -> None:
        expected = load_expected(SAMPLES_DIR, "workAreaDuration_10")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "workAreaDuration_10.aep").compositions[0]
        work_area_duration = comp.out_point - comp.in_point
        assert math.isclose(work_area_duration, comp_json["workAreaDuration"], rel_tol=0.001)


class TestCompItemDisplayStart:
    """Tests for display start attributes."""

    def test_displayStartFrame_100(self) -> None:
        expected = load_expected(SAMPLES_DIR, "displayStartFrame_100")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "displayStartFrame_100.aep").compositions[0]
        assert comp.display_start_frame == comp_json["displayStartFrame"] == 100

    def test_displayStartTime_10(self) -> None:
        expected = load_expected(SAMPLES_DIR, "displayStartTime_10")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "displayStartTime_10.aep").compositions[0]
        assert comp_json["displayStartTime"] == 10
        assert math.isclose(comp.display_start_time, comp_json["displayStartTime"])


class TestCompItemPixelAspect:
    """Tests for pixel aspect ratio."""

    def test_pixelAspect_0_75(self) -> None:
        expected = load_expected(SAMPLES_DIR, "pixelAspect_0.75")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "pixelAspect_0.75.aep").compositions[0]
        assert math.isclose(comp.pixel_aspect, comp_json["pixelAspect"])

    def test_pixelAspect_2_0(self) -> None:
        expected = load_expected(SAMPLES_DIR, "pixelAspect_2")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "pixelAspect_2.aep").compositions[0]
        assert math.isclose(comp.pixel_aspect, comp_json["pixelAspect"])


class TestCompItemName:
    """Tests for composition name."""

    def test_name_renamed(self) -> None:
        expected = load_expected(SAMPLES_DIR, "name_renamed")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "name_renamed.aep").compositions[0]
        assert comp.name == comp_json["name"] == "RenamedComp"


class TestCompItemComment:
    """Tests for composition comment."""

    def test_comment(self) -> None:
        expected = load_expected(SAMPLES_DIR, "comment")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "comment.aep").compositions[0]
        assert comp.comment == comp_json["comment"] == "Test comment"


class TestCompItemLabel:
    """Tests for composition label."""

    def test_label_5(self) -> None:
        expected = load_expected(SAMPLES_DIR, "label_5")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "label_5.aep").compositions[0]
        assert comp_json["label"] == 5
        assert comp.label.value == comp_json["label"]


class TestCompItemDropFrame:
    """Tests for composition drop frame."""

    def test_dropFrame_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "dropFrame_true")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "dropFrame_true.aep").compositions[0]
        assert comp_json["dropFrame"] is True
        assert comp.drop_frame == comp_json["dropFrame"]

    def test_dropFrame_false(self) -> None:
        expected = load_expected(SAMPLES_DIR, "dropFrame_false")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "dropFrame_false.aep").compositions[0]
        assert comp_json["dropFrame"] is False
        assert comp.drop_frame == comp_json["dropFrame"]

class TestCompItemDraft3D:
    """Tests for composition Draft 3D mode."""

    def test_draft3d_on(self) -> None:
        expected = load_expected(SAMPLES_DIR, "draft3d_on")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "draft3d_on.aep").compositions[0]
        assert comp_json["draft3d"] is True
        assert comp.draft_3d is True

    def test_draft3d_off(self) -> None:
        expected = load_expected(SAMPLES_DIR, "draft3d_off")
        comp_json = get_comp_from_json(expected)
        comp = parse_project(SAMPLES_DIR / "draft3d_off.aep").compositions[0]
        assert comp_json["draft3d"] is False
        assert comp.draft_3d is False