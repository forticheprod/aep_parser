"""Tests for FootageItem model parsing."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
from conftest import (
    get_first_footage,
    get_footage_from_json,
    get_sample_files,
    load_expected,
    parse_project,
)

from aep_parser import AlphaMode, FieldSeparationType, Project

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "footage"


@pytest.mark.parametrize("sample_name", get_sample_files(SAMPLES_DIR))
def test_parse_footage_sample(sample_name: str) -> None:
    """Each footage sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


class TestFootageSize:
    """Tests for footage size attributes."""

    def test_size_1920x1080(self) -> None:
        expected = load_expected(SAMPLES_DIR, "size_1920x1080")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "size_1920x1080.aep"))
        assert footage is not None
        assert footage.width == footage_json["width"] == 1920
        assert footage.height == footage_json["height"] == 1080

    def test_size_3840x2160(self) -> None:
        expected = load_expected(SAMPLES_DIR, "size_3840x2160")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "size_3840x2160.aep"))
        assert footage is not None
        assert footage.width == footage_json["width"] == 3840
        assert footage.height == footage_json["height"] == 2160


class TestPlaceholders:
    """Tests for placeholder footage."""

    def test_placeholder_still(self) -> None:
        expected = load_expected(SAMPLES_DIR, "placeholder_still")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "placeholder_still.aep"))
        assert footage is not None
        assert footage_json["mainSource"]["isStill"] is True
        assert footage.main_source.is_still == footage_json["mainSource"]["isStill"]

    def test_placeholder_movie(self) -> None:
        expected = load_expected(SAMPLES_DIR, "placeholder_movie")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "placeholder_movie.aep"))
        assert footage is not None
        assert footage_json["mainSource"]["isStill"] is False
        assert footage.main_source.is_still == footage_json["mainSource"]["isStill"]

    def test_placeholder_720p(self) -> None:
        expected = load_expected(SAMPLES_DIR, "placeholder_720p")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "placeholder_720p.aep"))
        assert footage is not None
        assert footage.width == footage_json["width"] == 1280
        assert footage.height == footage_json["height"] == 720

    def test_placeholder_4K(self) -> None:
        expected = load_expected(SAMPLES_DIR, "placeholder_4K")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "placeholder_4K.aep"))
        assert footage is not None
        assert footage.width == footage_json["width"] == 3840
        assert footage.height == footage_json["height"] == 2160

    def test_placeholder_30fps(self) -> None:
        expected = load_expected(SAMPLES_DIR, "placeholder_30fps")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "placeholder_30fps.aep"))
        assert footage is not None
        assert footage_json["frameRate"] == 30
        assert math.isclose(footage.frame_rate, footage_json["frameRate"])

    def test_placeholder_60fps(self) -> None:
        expected = load_expected(SAMPLES_DIR, "placeholder_60fps")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "placeholder_60fps.aep"))
        assert footage is not None
        assert footage_json["frameRate"] == 60
        assert math.isclose(footage.frame_rate, footage_json["frameRate"])

    def test_frameRate_23976(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameRate_23976")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "frameRate_23976.aep"))
        assert footage is not None
        assert math.isclose(footage.frame_rate, footage_json["frameRate"], rel_tol=0.001)


class TestSolidColors:
    """Tests for solid footage colors."""

    def test_color_red(self) -> None:
        expected = load_expected(SAMPLES_DIR, "color_red")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "color_red.aep"))
        assert footage is not None
        assert footage_json["mainSource"]["color"] == [1, 0, 0]
        assert footage.main_source.color[:3] == footage_json["mainSource"]["color"]

    def test_color_green(self) -> None:
        expected = load_expected(SAMPLES_DIR, "color_green")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "color_green.aep"))
        assert footage is not None
        assert footage_json["mainSource"]["color"] == [0, 1, 0]
        assert footage.main_source.color[:3] == footage_json["mainSource"]["color"]

    def test_color_blue(self) -> None:
        expected = load_expected(SAMPLES_DIR, "color_blue")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "color_blue.aep"))
        assert footage is not None
        assert footage_json["mainSource"]["color"] == [0, 0, 1]
        assert footage.main_source.color[:3] == footage_json["mainSource"]["color"]

    def test_color_gray(self) -> None:
        expected = load_expected(SAMPLES_DIR, "color_gray")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "color_gray.aep"))
        assert footage is not None
        assert footage_json["mainSource"]["color"] == [0.5, 0.5, 0.5]
        assert footage.main_source.color[:3] == footage_json["mainSource"]["color"]


class TestAlphaMode:
    """Tests for alpha mode attribute."""

    def test_alphaMode_IGNORE(self) -> None:
        expected = load_expected(SAMPLES_DIR, "alphaMode_IGNORE")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "alphaMode_IGNORE.aep"))
        assert footage is not None
        assert footage.main_source.alpha_mode == footage_json["mainSource"]["alphaMode"] == AlphaMode.IGNORE

    def test_alphaMode_STRAIGHT(self) -> None:
        expected = load_expected(SAMPLES_DIR, "alphaMode_STRAIGHT")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "alphaMode_STRAIGHT.aep"))
        assert footage is not None
        assert footage.main_source.alpha_mode == footage_json["mainSource"]["alphaMode"] == AlphaMode.STRAIGHT

    def test_alphaMode_PREMULTIPLIED(self) -> None:
        expected = load_expected(SAMPLES_DIR, "alphaMode_PREMULTIPLIED")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "alphaMode_PREMULTIPLIED.aep"))
        assert footage is not None
        assert footage.main_source.alpha_mode == footage_json["mainSource"]["alphaMode"] == AlphaMode.PREMULTIPLIED


class TestFieldSeparation:
    """Tests for field separation settings."""

    def test_fieldSeparationType_OFF(self) -> None:
        expected = load_expected(SAMPLES_DIR, "fieldSeparationType_OFF")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "fieldSeparationType_OFF.aep"))
        assert footage is not None
        assert footage.main_source.field_separation_type == footage_json["mainSource"]["fieldSeparationType"] == FieldSeparationType.OFF

    def test_fieldSeparationType_UPPER(self) -> None:
        expected = load_expected(SAMPLES_DIR, "fieldSeparationType_UPPER")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "fieldSeparationType_UPPER.aep"))
        assert footage is not None
        assert footage.main_source.field_separation_type == footage_json["mainSource"]["fieldSeparationType"] == FieldSeparationType.UPPER_FIELD_FIRST

    def test_fieldSeparationType_LOWER(self) -> None:
        expected = load_expected(SAMPLES_DIR, "fieldSeparationType_LOWER")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "fieldSeparationType_LOWER.aep"))
        assert footage is not None
        assert footage.main_source.field_separation_type == footage_json["mainSource"]["fieldSeparationType"] == FieldSeparationType.LOWER_FIELD_FIRST

    def test_highQualityFieldSeparation_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "highQualityFieldSeparation_true")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "highQualityFieldSeparation_true.aep"))
        assert footage is not None
        assert footage.main_source.high_quality_field_separation == footage_json["mainSource"]["highQualityFieldSeparation"] is True


class TestFootageSettings:
    """Tests for various footage settings."""

    def test_conformFrameRate_24(self) -> None:
        expected = load_expected(SAMPLES_DIR, "conformFrameRate_24")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "conformFrameRate_24.aep"))
        assert footage is not None
        assert footage.main_source.conform_frame_rate == footage_json["mainSource"]["conformFrameRate"] == 24

    def test_conformFrameRate_30(self) -> None:
        expected = load_expected(SAMPLES_DIR, "conformFrameRate_30")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "conformFrameRate_30.aep"))
        assert footage is not None
        assert footage.main_source.conform_frame_rate == footage_json["mainSource"]["conformFrameRate"] == 30

    def test_loop_3(self) -> None:
        expected = load_expected(SAMPLES_DIR, "loop_3")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "loop_3.aep"))
        assert footage is not None
        assert footage.main_source.loop == footage_json["mainSource"]["loop"] == 3

    def test_pixelAspect_2(self) -> None:
        expected = load_expected(SAMPLES_DIR, "pixelAspect_2")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "pixelAspect_2.aep"))
        assert footage is not None
        assert footage_json["pixelAspect"] == 2
        assert math.isclose(footage.pixel_aspect, footage_json["pixelAspect"])

    def test_invertAlpha_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "invertAlpha_true")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "invertAlpha_true.aep"))
        assert footage is not None
        assert footage.main_source.invert_alpha == footage_json["mainSource"]["invertAlpha"] is True

    def test_premulColor_black(self) -> None:
        expected = load_expected(SAMPLES_DIR, "premulColor_black")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "premulColor_black.aep"))
        assert footage is not None
        assert footage.main_source.premul_color == footage_json["mainSource"]["premulColor"] == [0, 0, 0]

    def test_premulColor_red(self) -> None:
        expected = load_expected(SAMPLES_DIR, "premulColor_red")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "premulColor_red.aep"))
        assert footage is not None
        assert footage_json["mainSource"]["premulColor"] == [1, 0, 0]
        assert footage.main_source.premul_color == footage_json["mainSource"]["premulColor"]

    def test_removePulldown_OFF(self) -> None:
        project = parse_project(SAMPLES_DIR / "removePulldown_OFF.aep")
        assert isinstance(project, Project)

    def test_name_renamed(self) -> None:
        expected = load_expected(SAMPLES_DIR, "name_renamed")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "name_renamed.aep"))
        assert footage is not None
        assert footage.name == footage_json["name"] == "RenamedFootage"
