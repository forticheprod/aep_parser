"""Tests for CompItem model parsing using samples from models/composition/.

These tests verify that aep_parser produces the same values as the JSON
reference files exported from After Effects.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from aep_parser import Project, parse_project

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "composition"


def get_sample_files() -> list[str]:
    """Get all .aep files in the composition samples directory."""
    if not SAMPLES_DIR.exists():
        return []
    return [f.stem for f in SAMPLES_DIR.glob("*.aep")]


def load_expected(sample_name: str) -> dict:
    """Load the expected JSON for a sample."""
    json_path = SAMPLES_DIR / f"{sample_name}.json"
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def get_comp_from_json(expected: dict) -> dict:
    """Extract composition data from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Composition":
                return item
    return {}


@pytest.mark.parametrize("sample_name", get_sample_files())
def test_parse_composition_sample(sample_name: str) -> None:
    """Test that each composition sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)
    # Each composition sample should have at least one composition
    assert len(project.compositions) >= 1


class TestCompItemBasic:
    """Tests for basic composition attributes."""

    def test_bgColor_red(self) -> None:
        """Test composition with red background color."""
        expected = load_expected("bgColor_red")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "bgColor_red.aep")
        comp = project.compositions[0]
        assert math.isclose(comp.bg_color[0], comp_json["bgColor"][0])
        assert math.isclose(comp.bg_color[1], comp_json["bgColor"][1])
        assert math.isclose(comp.bg_color[2], comp_json["bgColor"][2])

    def test_bgColor_custom(self) -> None:
        """Test composition with custom background color."""
        expected = load_expected("bgColor_custom")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "bgColor_custom.aep")
        comp = project.compositions[0]
        assert math.isclose(comp.bg_color[0], comp_json["bgColor"][0])
        assert math.isclose(comp.bg_color[1], comp_json["bgColor"][1])
        assert math.isclose(comp.bg_color[2], comp_json["bgColor"][2])


class TestCompItemSize:
    """Tests for composition size attributes."""

    def test_size_1920x1080(self) -> None:
        """Test 1920x1080 composition."""
        expected = load_expected("size_1920x1080")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "size_1920x1080.aep")
        comp = project.compositions[0]
        assert comp_json["width"] == 1920
        assert comp_json["height"] == 1080
        assert comp.width == comp_json["width"]
        assert comp.height == comp_json["height"]

    def test_size_2048x872(self) -> None:
        """Test 2048x872 (Cinemascope) composition."""
        expected = load_expected("size_2048x872")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "size_2048x872.aep")
        comp = project.compositions[0]
        assert comp_json["width"] == 2048
        assert comp_json["height"] == 872
        assert comp.width == comp_json["width"]
        assert comp.height == comp_json["height"]


class TestCompItemFrameRate:
    """Tests for composition frame rate attributes.

    NOTE: Frame rate parsing from cdta uses a base + fractional formula that
    may have small precision errors. Using rel_tol=0.01 (1%) for comparisons.
    """

    def test_frameRate_23976(self) -> None:
        """Test 23.976 fps composition.

        Frame rate is stored as a 16.16 fixed point value:
        frame_rate_integer + frame_rate_fractional / 65536
        For 23.976: 23 + 63963/65536 = 23.975997924804688
        """
        expected = load_expected("frameRate_23976")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "frameRate_23976.aep")
        comp = project.compositions[0]
        assert math.isclose(comp_json["frameRate"], 23.976, rel_tol=0.001)
        assert math.isclose(comp.frame_rate, comp_json["frameRate"], rel_tol=0.001)

    def test_frameRate_30(self) -> None:
        """Test 30 fps composition."""
        expected = load_expected("frameRate_30")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "frameRate_30.aep")
        comp = project.compositions[0]
        assert comp_json["frameRate"] == 30
        assert math.isclose(comp.frame_rate, comp_json["frameRate"], rel_tol=0.001)

    def test_frameRate_60(self) -> None:
        """Test 60 fps composition."""
        expected = load_expected("frameRate_60")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "frameRate_60.aep")
        comp = project.compositions[0]
        assert comp_json["frameRate"] == 60
        assert math.isclose(comp.frame_rate, comp_json["frameRate"], rel_tol=0.001)


class TestCompItemDuration:
    """Tests for composition duration attributes."""

    def test_duration_60(self) -> None:
        """Test 60 second composition."""
        expected = load_expected("duration_60")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "duration_60.aep")
        comp = project.compositions[0]
        assert comp_json["duration"] == 60
        assert math.isclose(comp.duration, comp_json["duration"])


class TestCompItemMotionBlur:
    """Tests for motion blur attributes."""

    def test_motionBlur_true(self) -> None:
        """Test motion blur enabled."""
        expected = load_expected("motionBlur_true")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "motionBlur_true.aep")
        comp = project.compositions[0]
        assert comp_json["motionBlur"] is True
        assert comp.motion_blur == comp_json["motionBlur"]

    def test_shutterAngle_180(self) -> None:
        """Test 180 degree shutter angle."""
        expected = load_expected("shutterAngle_180")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "shutterAngle_180.aep")
        comp = project.compositions[0]
        assert comp_json["shutterAngle"] == 180
        assert comp.shutter_angle == comp_json["shutterAngle"]

    def test_shutterAngle_360(self) -> None:
        """Test 360 degree shutter angle."""
        expected = load_expected("shutterAngle_360")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "shutterAngle_360.aep")
        comp = project.compositions[0]
        assert comp_json["shutterAngle"] == 360
        assert comp.shutter_angle == comp_json["shutterAngle"]

    def test_shutterPhase_minus90(self) -> None:
        """Test -90 degree shutter phase."""
        expected = load_expected("shutterPhase_minus90")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "shutterPhase_minus90.aep")
        comp = project.compositions[0]
        assert comp_json["shutterPhase"] == -90
        assert comp.shutter_phase == comp_json["shutterPhase"]

    def test_motionBlurSamplesPerFrame_32(self) -> None:
        """Test motion blur samples per frame."""
        expected = load_expected("motionBlurSamplesPerFrame_32")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "motionBlurSamplesPerFrame_32.aep")
        comp = project.compositions[0]
        assert comp_json["motionBlurSamplesPerFrame"] == 32
        assert comp.motion_blur_samples_per_frame == comp_json["motionBlurSamplesPerFrame"]

    def test_motionBlurAdaptiveSampleLimit_256(self) -> None:
        """Test motion blur adaptive sample limit."""
        expected = load_expected("motionBlurAdaptiveSampleLimit_256")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "motionBlurAdaptiveSampleLimit_256.aep")
        comp = project.compositions[0]
        assert comp_json["motionBlurAdaptiveSampleLimit"] == 256
        assert comp.motion_blur_adaptive_sample_limit == comp_json["motionBlurAdaptiveSampleLimit"]


class TestCompItemResolution:
    """Tests for resolution attributes."""

    def test_resolutionFactor_half(self) -> None:
        """Test half resolution."""
        expected = load_expected("resolutionFactor_half")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "resolutionFactor_half.aep")
        comp = project.compositions[0]
        assert comp.resolution_factor == comp_json["resolutionFactor"]

    def test_resolutionFactor_quarter(self) -> None:
        """Test quarter resolution."""
        expected = load_expected("resolutionFactor_quarter")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "resolutionFactor_quarter.aep")
        comp = project.compositions[0]
        assert comp.resolution_factor == comp_json["resolutionFactor"]


class TestCompItemNestedOptions:
    """Tests for nested composition options."""

    def test_preserveNestedFrameRate_true(self) -> None:
        """Test preserve nested frame rate."""
        expected = load_expected("preserveNestedFrameRate_true")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "preserveNestedFrameRate_true.aep")
        comp = project.compositions[0]
        assert comp_json["preserveNestedFrameRate"] is True
        assert comp.preserve_nested_frame_rate == comp_json["preserveNestedFrameRate"]

    def test_preserveNestedResolution_true(self) -> None:
        """Test preserve nested resolution."""
        expected = load_expected("preserveNestedResolution_true")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "preserveNestedResolution_true.aep")
        comp = project.compositions[0]
        assert comp_json["preserveNestedResolution"] is True
        assert comp.preserve_nested_resolution == comp_json["preserveNestedResolution"]


class TestCompItemFrameBlending:
    """Tests for frame blending attribute."""

    def test_frameBlending_true(self) -> None:
        """Test frame blending enabled."""
        expected = load_expected("frameBlending_true")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "frameBlending_true.aep")
        comp = project.compositions[0]
        assert comp_json["frameBlending"] is True
        assert comp.frame_blending == comp_json["frameBlending"]


class TestCompItemShyLayers:
    """Tests for hide shy layers attribute."""

    def test_hideShyLayers_true(self) -> None:
        """Test hide shy layers enabled."""
        expected = load_expected("hideShyLayers_true")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "hideShyLayers_true.aep")
        comp = project.compositions[0]
        assert comp_json["hideShyLayers"] is True
        assert comp.hide_shy_layers == comp_json["hideShyLayers"]


class TestCompItemTime:
    """Tests for time-related attributes.

    NOTE: Time values are derived from frame_rate, which has precision issues.
    Using rel_tol=0.001 for comparisons.
    """

    def test_time_0(self) -> None:
        """Test time at 0 seconds."""
        expected = load_expected("time_0")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "time_0.aep")
        comp = project.compositions[0]
        assert comp_json["time"] == 0
        assert math.isclose(comp.time, comp_json["time"])

    def test_time_5(self) -> None:
        """Test time at 5 seconds."""
        expected = load_expected("time_5")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "time_5.aep")
        comp = project.compositions[0]
        assert comp_json["time"] == 5
        assert math.isclose(comp.time, comp_json["time"], rel_tol=0.001)

    def test_time_15(self) -> None:
        """Test time at 15 seconds."""
        expected = load_expected("time_15")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "time_15.aep")
        comp = project.compositions[0]
        assert comp_json["time"] == 15
        assert math.isclose(comp.time, comp_json["time"], rel_tol=0.001)


class TestCompItemWorkArea:
    """Tests for work area attributes.

    NOTE: Work area values are derived from frame_rate, which has precision issues.
    Using rel_tol=0.001 for comparisons.
    """

    def test_workAreaStart_5(self) -> None:
        """Test work area start at 5 seconds."""
        expected = load_expected("workAreaStart_5")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "workAreaStart_5.aep")
        comp = project.compositions[0]
        assert math.isclose(comp.in_point, comp_json["workAreaStart"], rel_tol=0.001)

    def test_workAreaDuration_10(self) -> None:
        """Test work area duration of 10 seconds."""
        expected = load_expected("workAreaDuration_10")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "workAreaDuration_10.aep")
        comp = project.compositions[0]
        work_area_duration = comp.out_point - comp.in_point
        assert math.isclose(work_area_duration, comp_json["workAreaDuration"], rel_tol=0.001)


class TestCompItemDisplayStart:
    """Tests for display start attributes."""

    def test_displayStartFrame_100(self) -> None:
        """Test display start frame at 100."""
        expected = load_expected("displayStartFrame_100")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "displayStartFrame_100.aep")
        comp = project.compositions[0]
        assert comp_json["displayStartFrame"] == 100
        assert comp.display_start_frame == comp_json["displayStartFrame"]

    def test_displayStartTime_10(self) -> None:
        """Test display start time at 10 seconds."""
        expected = load_expected("displayStartTime_10")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "displayStartTime_10.aep")
        comp = project.compositions[0]
        assert comp_json["displayStartTime"] == 10
        assert math.isclose(comp.display_start_time, comp_json["displayStartTime"])


class TestCompItemPixelAspect:
    """Tests for pixel aspect ratio attributes."""

    def test_pixelAspect_0_75(self) -> None:
        """Test 0.75 pixel aspect ratio (DV NTSC Widescreen)."""
        expected = load_expected("pixelAspect_0.75")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "pixelAspect_0.75.aep")
        comp = project.compositions[0]
        assert comp_json["pixelAspect"] == 0.75
        assert math.isclose(comp.pixel_aspect, comp_json["pixelAspect"])

    def test_pixelAspect_2_0(self) -> None:
        """Test 2.0 pixel aspect ratio."""
        expected = load_expected("pixelAspect_2")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "pixelAspect_2.aep")
        comp = project.compositions[0]
        assert comp_json["pixelAspect"] == 2
        assert math.isclose(comp.pixel_aspect, comp_json["pixelAspect"])


class TestCompItemName:
    """Tests for composition name attribute."""

    def test_name_renamed(self) -> None:
        """Test renamed composition."""
        expected = load_expected("name_renamed")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "name_renamed.aep")
        comp = project.compositions[0]
        assert comp_json["name"] == "RenamedComp"
        assert comp.name == comp_json["name"]


class TestCompItemComment:
    """Tests for composition comment attribute."""

    def test_comment(self) -> None:
        """Test composition with comment."""
        expected = load_expected("comment")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "comment.aep")
        comp = project.compositions[0]
        assert comp_json["comment"] == "Test comment"
        assert comp.comment == comp_json["comment"]


class TestCompItemLabel:
    """Tests for composition label attribute."""

    def test_label_5(self) -> None:
        """Test composition with label 5."""
        expected = load_expected("label_5")
        comp_json = get_comp_from_json(expected)
        project = parse_project(SAMPLES_DIR / "label_5.aep")
        comp = project.compositions[0]
        assert comp_json["label"] == 5
        assert comp.label.value == comp_json["label"]
