"""Tests for FootageItem model parsing using samples from models/footage/.

These tests verify that aep_parser produces the same values as the JSON
reference files exported from After Effects.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from aep_parser import AlphaMode, FieldSeparationType, Project, parse_project

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "footage"


def get_sample_files() -> list[str]:
    """Get all .aep files in the footage samples directory."""
    if not SAMPLES_DIR.exists():
        return []
    return [f.stem for f in SAMPLES_DIR.glob("*.aep")]


def load_expected(sample_name: str) -> dict:
    """Load the expected JSON for a sample."""
    json_path = SAMPLES_DIR / f"{sample_name}.json"
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def get_footage_from_json(expected: dict) -> dict:
    """Extract footage data from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Footage":
                return item
    return {}


@pytest.mark.parametrize("sample_name", get_sample_files())
def test_parse_footage_sample(sample_name: str) -> None:
    """Test that each footage sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


def get_first_footage(project: Project):
    """Get the first footage item."""
    if project.footages:
        return project.footages[0]
    return None


class TestFootageSize:
    """Tests for footage size attributes."""

    def test_size_1920x1080(self) -> None:
        """Test 1920x1080 footage."""
        expected = load_expected("size_1920x1080")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "size_1920x1080.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["width"] == 1920
        assert footage_json["height"] == 1080
        assert footage.width == footage_json["width"]
        assert footage.height == footage_json["height"]

    def test_size_3840x2160(self) -> None:
        """Test 4K footage."""
        expected = load_expected("size_3840x2160")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "size_3840x2160.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["width"] == 3840
        assert footage_json["height"] == 2160
        assert footage.width == footage_json["width"]
        assert footage.height == footage_json["height"]


class TestPlaceholders:
    """Tests for placeholder footage."""

    def test_placeholder_still(self) -> None:
        """Test still image placeholder."""
        expected = load_expected("placeholder_still")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "placeholder_still.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["isStill"] is True
        assert footage.main_source.is_still == footage_json["mainSource"]["isStill"]

    def test_placeholder_movie(self) -> None:
        """Test movie placeholder."""
        expected = load_expected("placeholder_movie")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "placeholder_movie.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["isStill"] is False
        assert footage.main_source.is_still == footage_json["mainSource"]["isStill"]

    def test_placeholder_720p(self) -> None:
        """Test 720p placeholder."""
        expected = load_expected("placeholder_720p")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "placeholder_720p.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["width"] == 1280
        assert footage_json["height"] == 720
        assert footage.width == footage_json["width"]
        assert footage.height == footage_json["height"]

    def test_placeholder_4K(self) -> None:
        """Test 4K placeholder."""
        expected = load_expected("placeholder_4K")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "placeholder_4K.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["width"] == 3840
        assert footage_json["height"] == 2160
        assert footage.width == footage_json["width"]
        assert footage.height == footage_json["height"]

    def test_placeholder_30fps(self) -> None:
        """Test 30fps placeholder."""
        expected = load_expected("placeholder_30fps")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "placeholder_30fps.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["frameRate"] == 30
        assert math.isclose(footage.frame_rate, footage_json["frameRate"])

    def test_placeholder_60fps(self) -> None:
        """Test 60fps placeholder."""
        expected = load_expected("placeholder_60fps")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "placeholder_60fps.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["frameRate"] == 60
        assert math.isclose(footage.frame_rate, footage_json["frameRate"])

    def test_frameRate_23976(self) -> None:
        """Test 23.976 fps footage (NTSC).

        Frame rate is stored as 16.16 fixed point:
        frame_rate_base + frame_rate_dividend / 65536
        """
        expected = load_expected("frameRate_23976")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "frameRate_23976.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert math.isclose(footage_json["frameRate"], 23.976, rel_tol=0.001)
        assert math.isclose(footage.frame_rate, footage_json["frameRate"], rel_tol=0.001)


class TestSolidColors:
    """Tests for solid footage colors."""

    def test_color_red(self) -> None:
        """Test red solid."""
        expected = load_expected("color_red")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "color_red.aep")
        footage = get_first_footage(project)
        assert footage is not None
        # Color is [R, G, B, A] in parser, [R, G, B] in JSON
        assert footage_json["mainSource"]["color"] == [1, 0, 0]
        assert footage.main_source.color[:3] == footage_json["mainSource"]["color"]

    def test_color_green(self) -> None:
        """Test green solid."""
        expected = load_expected("color_green")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "color_green.aep")
        footage = get_first_footage(project)
        assert footage is not None
        # Color is [R, G, B, A] in parser, [R, G, B] in JSON
        assert footage_json["mainSource"]["color"] == [0, 1, 0]
        assert footage.main_source.color[:3] == footage_json["mainSource"]["color"]

    def test_color_blue(self) -> None:
        """Test blue solid."""
        expected = load_expected("color_blue")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "color_blue.aep")
        footage = get_first_footage(project)
        assert footage is not None
        # Color is [R, G, B, A] in parser, [R, G, B] in JSON
        assert footage_json["mainSource"]["color"] == [0, 0, 1]
        assert footage.main_source.color[:3] == footage_json["mainSource"]["color"]

    def test_color_gray(self) -> None:
        """Test gray solid."""
        expected = load_expected("color_gray")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "color_gray.aep")
        footage = get_first_footage(project)
        assert footage is not None
        # Color is [R, G, B, A] in parser, [R, G, B] in JSON
        assert footage_json["mainSource"]["color"] == [0.5, 0.5, 0.5]
        assert footage.main_source.color[:3] == footage_json["mainSource"]["color"]


class TestAlphaMode:
    """Tests for alpha mode attribute.

    Samples use image_with_alpha.png which has an alpha channel.
    """

    def test_alphaMode_IGNORE(self) -> None:
        """Test ignore alpha mode."""
        expected = load_expected("alphaMode_IGNORE")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "alphaMode_IGNORE.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["alphaMode"] == AlphaMode.IGNORE
        assert footage.main_source.alpha_mode == footage_json["mainSource"]["alphaMode"]
        assert footage.main_source.alpha_mode == AlphaMode.IGNORE

    def test_alphaMode_STRAIGHT(self) -> None:
        """Test straight alpha mode."""
        expected = load_expected("alphaMode_STRAIGHT")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "alphaMode_STRAIGHT.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["alphaMode"] == AlphaMode.STRAIGHT
        assert footage.main_source.alpha_mode == footage_json["mainSource"]["alphaMode"]
        assert footage.main_source.alpha_mode == AlphaMode.STRAIGHT

    def test_alphaMode_PREMULTIPLIED(self) -> None:
        """Test premultiplied alpha mode."""
        expected = load_expected("alphaMode_PREMULTIPLIED")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "alphaMode_PREMULTIPLIED.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["alphaMode"] == AlphaMode.PREMULTIPLIED
        assert footage.main_source.alpha_mode == footage_json["mainSource"]["alphaMode"]
        assert footage.main_source.alpha_mode == AlphaMode.PREMULTIPLIED


class TestFieldSeparation:
    """Tests for field separation settings."""

    def test_fieldSeparationType_OFF(self) -> None:
        """Test field separation off."""
        expected = load_expected("fieldSeparationType_OFF")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "fieldSeparationType_OFF.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["fieldSeparationType"] == FieldSeparationType.OFF
        assert footage.main_source.field_separation_type == footage_json["mainSource"]["fieldSeparationType"]
        assert footage.main_source.field_separation_type == FieldSeparationType.OFF

    def test_fieldSeparationType_UPPER(self) -> None:
        """Test upper field first."""
        expected = load_expected("fieldSeparationType_UPPER")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "fieldSeparationType_UPPER.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["fieldSeparationType"] == FieldSeparationType.UPPER_FIELD_FIRST
        assert footage.main_source.field_separation_type == footage_json["mainSource"]["fieldSeparationType"]

    def test_fieldSeparationType_LOWER(self) -> None:
        """Test lower field first."""
        expected = load_expected("fieldSeparationType_LOWER")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "fieldSeparationType_LOWER.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["fieldSeparationType"] == FieldSeparationType.LOWER_FIELD_FIRST
        assert footage.main_source.field_separation_type == footage_json["mainSource"]["fieldSeparationType"]

    def test_highQualityFieldSeparation_true(self) -> None:
        """Test high quality field separation."""
        expected = load_expected("highQualityFieldSeparation_true")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "highQualityFieldSeparation_true.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["highQualityFieldSeparation"] is True
        assert footage.main_source.high_quality_field_separation == footage_json["mainSource"]["highQualityFieldSeparation"]


class TestFootageSettings:
    """Tests for various footage settings."""

    def test_conformFrameRate_24(self) -> None:
        """Test conform to 24 fps."""
        expected = load_expected("conformFrameRate_24")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "conformFrameRate_24.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["conformFrameRate"] == 24
        assert footage.main_source.conform_frame_rate == footage_json["mainSource"]["conformFrameRate"]

    def test_conformFrameRate_30(self) -> None:
        """Test conform to 30 fps."""
        expected = load_expected("conformFrameRate_30")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "conformFrameRate_30.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["conformFrameRate"] == 30
        assert footage.main_source.conform_frame_rate == footage_json["mainSource"]["conformFrameRate"]

    def test_loop_3(self) -> None:
        """Test footage loop 3 times."""
        expected = load_expected("loop_3")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "loop_3.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["loop"] == 3
        assert footage.main_source.loop == footage_json["mainSource"]["loop"]

    def test_pixelAspect_2(self) -> None:
        """Test pixel aspect ratio of 2."""
        expected = load_expected("pixelAspect_2")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "pixelAspect_2.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["pixelAspect"] == 2
        assert math.isclose(footage.pixel_aspect, footage_json["pixelAspect"])

    def test_invertAlpha_true(self) -> None:
        """Test invert alpha."""
        expected = load_expected("invertAlpha_true")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "invertAlpha_true.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage.main_source.invert_alpha == footage_json["mainSource"]["invertAlpha"]
        assert footage.main_source.invert_alpha is True

    def test_premulColor_black(self) -> None:
        """Test premultiply color black."""
        expected = load_expected("premulColor_black")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "premulColor_black.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage.main_source.premul_color == footage_json["mainSource"]["premulColor"]
        assert footage.main_source.premul_color == [0, 0, 0]

    def test_premulColor_red(self) -> None:
        """Test premultiply color red."""
        expected = load_expected("premulColor_red")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "premulColor_red.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["mainSource"]["premulColor"] == [1, 0, 0]
        assert footage.main_source.premul_color == footage_json["mainSource"]["premulColor"]

    def test_removePulldown_OFF(self) -> None:
        """Test remove pulldown off."""
        load_expected("removePulldown_OFF")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "removePulldown_OFF.aep")
        assert isinstance(project, Project)

    def test_name_renamed(self) -> None:
        """Test renamed footage item."""
        expected = load_expected("name_renamed")
        footage_json = get_footage_from_json(expected)
        project = parse_project(SAMPLES_DIR / "name_renamed.aep")
        footage = get_first_footage(project)
        assert footage is not None
        assert footage_json["name"] == "RenamedFootage"
        assert footage.name == footage_json["name"]
