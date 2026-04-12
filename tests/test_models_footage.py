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

from aep_parser import (
    AlphaMode,
    FieldSeparationType,
    LinearLightMode,
    Project,
    PulldownPhase,
)
from aep_parser import parse as parse_aep

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
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "placeholder_still.aep")
        )
        assert footage is not None
        assert footage_json["mainSource"]["isStill"] is True
        assert footage.main_source.is_still == footage_json["mainSource"]["isStill"]

    def test_placeholder_movie(self) -> None:
        expected = load_expected(SAMPLES_DIR, "placeholder_movie")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "placeholder_movie.aep")
        )
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
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "placeholder_30fps.aep")
        )
        assert footage is not None
        assert footage_json["frameRate"] == 30
        assert math.isclose(footage.frame_rate, footage_json["frameRate"])

    def test_placeholder_60fps(self) -> None:
        expected = load_expected(SAMPLES_DIR, "placeholder_60fps")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "placeholder_60fps.aep")
        )
        assert footage is not None
        assert footage_json["frameRate"] == 60
        assert math.isclose(footage.frame_rate, footage_json["frameRate"])

    def test_frameRate_23976(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameRate_23976")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "frameRate_23976.aep"))
        assert footage is not None
        assert math.isclose(
            footage.frame_rate, footage_json["frameRate"], rel_tol=0.001
        )


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


class TestAlphaMode:
    """Tests for alpha mode attribute."""

    def test_alphaMode_IGNORE(self) -> None:
        expected = load_expected(SAMPLES_DIR, "alphaMode_IGNORE")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "alphaMode_IGNORE.aep"))
        assert footage is not None
        assert (
            footage.main_source.alpha_mode
            == footage_json["mainSource"]["alphaMode"]
            == AlphaMode.IGNORE
        )

    def test_alphaMode_STRAIGHT(self) -> None:
        expected = load_expected(SAMPLES_DIR, "alphaMode_STRAIGHT")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "alphaMode_STRAIGHT.aep")
        )
        assert footage is not None
        assert (
            footage.main_source.alpha_mode
            == footage_json["mainSource"]["alphaMode"]
            == AlphaMode.STRAIGHT
        )

    def test_alphaMode_PREMULTIPLIED(self) -> None:
        expected = load_expected(SAMPLES_DIR, "alphaMode_PREMULTIPLIED")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "alphaMode_PREMULTIPLIED.aep")
        )
        assert footage is not None
        assert (
            footage.main_source.alpha_mode
            == footage_json["mainSource"]["alphaMode"]
            == AlphaMode.PREMULTIPLIED
        )


class TestFieldSeparation:
    """Tests for field separation settings."""

    def test_fieldSeparationType_OFF(self) -> None:
        expected = load_expected(SAMPLES_DIR, "fieldSeparationType_OFF")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "fieldSeparationType_OFF.aep")
        )
        assert footage is not None
        assert (
            footage.main_source.field_separation_type
            == footage_json["mainSource"]["fieldSeparationType"]
            == FieldSeparationType.OFF
        )

    def test_fieldSeparationType_UPPER(self) -> None:
        expected = load_expected(SAMPLES_DIR, "fieldSeparationType_UPPER")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "fieldSeparationType_UPPER.aep")
        )
        assert footage is not None
        assert (
            footage.main_source.field_separation_type
            == footage_json["mainSource"]["fieldSeparationType"]
            == FieldSeparationType.UPPER_FIELD_FIRST
        )

    def test_fieldSeparationType_LOWER(self) -> None:
        expected = load_expected(SAMPLES_DIR, "fieldSeparationType_LOWER")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "fieldSeparationType_LOWER.aep")
        )
        assert footage is not None
        assert (
            footage.main_source.field_separation_type
            == footage_json["mainSource"]["fieldSeparationType"]
            == FieldSeparationType.LOWER_FIELD_FIRST
        )

    def test_highQualityFieldSeparation_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "highQualityFieldSeparation_true")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "highQualityFieldSeparation_true.aep")
        )
        assert footage is not None
        assert (
            footage.main_source.high_quality_field_separation
            == footage_json["mainSource"]["highQualityFieldSeparation"]
            is True
        )


class TestFootageSettings:
    """Tests for various footage settings."""

    def test_conformFrameRate_24(self) -> None:
        expected = load_expected(SAMPLES_DIR, "conformFrameRate_24")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "conformFrameRate_24.aep")
        )
        assert footage is not None
        assert (
            footage.main_source.conform_frame_rate
            == footage_json["mainSource"]["conformFrameRate"]
            == 24
        )

    def test_conformFrameRate_30(self) -> None:
        expected = load_expected(SAMPLES_DIR, "conformFrameRate_30")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "conformFrameRate_30.aep")
        )
        assert footage is not None
        assert (
            footage.main_source.conform_frame_rate
            == footage_json["mainSource"]["conformFrameRate"]
            == 30
        )

    def test_conform_frame_rate_2_5(self) -> None:
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "conform_frame_rate_2.5.aep")
        )
        assert footage is not None
        assert footage.main_source.conform_frame_rate == 2.5

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
        assert (
            footage.main_source.invert_alpha
            == footage_json["mainSource"]["invertAlpha"]
            is True
        )

    def test_premulColor_black(self) -> None:
        expected = load_expected(SAMPLES_DIR, "premulColor_black")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(
            parse_project(SAMPLES_DIR / "premulColor_black.aep")
        )
        assert footage is not None
        assert (
            footage.main_source.premul_color
            == footage_json["mainSource"]["premulColor"]
            == [0, 0, 0]
        )

    def test_premulColor_red(self) -> None:
        expected = load_expected(SAMPLES_DIR, "premulColor_red")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "premulColor_red.aep"))
        assert footage is not None
        assert footage_json["mainSource"]["premulColor"] == [1, 0, 0]
        assert (
            footage.main_source.premul_color
            == footage_json["mainSource"]["premulColor"]
        )

    def test_name_renamed(self) -> None:
        expected = load_expected(SAMPLES_DIR, "name_renamed")
        footage_json = get_footage_from_json(expected)
        footage = get_first_footage(parse_project(SAMPLES_DIR / "name_renamed.aep"))
        assert footage is not None
        assert footage.name == footage_json["name"] == "RenamedFootage"


def _get_first_footage(aep_path: Path) -> object:
    """Parse an .aep and return the first footage item."""
    project = parse_aep(aep_path).project
    return project.footages[0]


class TestFootageReadOnly:
    """All descriptor-backed FootageItem fields are read-only."""

    def test_width_is_read_only(self) -> None:
        footage = _get_first_footage(SAMPLES_DIR / "size_1920x1080.aep")
        with pytest.raises(AttributeError, match="read-only"):
            footage.width = 100  # type: ignore[misc]

    def test_height_is_read_only(self) -> None:
        footage = _get_first_footage(SAMPLES_DIR / "size_1920x1080.aep")
        with pytest.raises(AttributeError, match="read-only"):
            footage.height = 100  # type: ignore[misc]

    def test_duration_is_read_only(self) -> None:
        footage = _get_first_footage(SAMPLES_DIR / "placeholder_movie.aep")
        with pytest.raises(AttributeError, match="read-only"):
            footage.duration = 5.0  # type: ignore[misc]

    def test_frame_rate_is_read_only(self) -> None:
        footage = _get_first_footage(SAMPLES_DIR / "frameRate_23976.aep")
        with pytest.raises(AttributeError, match="read-only"):
            footage.frame_rate = 30.0  # type: ignore[misc]

    def test_frame_duration_is_read_only(self) -> None:
        footage = _get_first_footage(SAMPLES_DIR / "placeholder_movie.aep")
        with pytest.raises(AttributeError, match="read-only"):
            footage.frame_duration = 100  # type: ignore[misc]

    def test_pixel_aspect_is_read_only(self) -> None:
        footage = _get_first_footage(SAMPLES_DIR / "pixelAspect_2.aep")
        with pytest.raises(AttributeError, match="read-only"):
            footage.pixel_aspect = 1.5  # type: ignore[misc]

    def test_footage_missing_is_read_only(self) -> None:
        footage = _get_first_footage(SAMPLES_DIR / "footage_missing.aep")
        with pytest.raises(AttributeError, match="read-only"):
            footage.footage_missing = False  # type: ignore[misc]




class TestRoundtripLoop:
    """Roundtrip tests for FootageSource.loop."""

    def test_modify_loop(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "loop_3.aep").project
        footage = project.footages[0]
        source = footage.main_source
        assert source.loop == 3

        source.loop = 5
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert source2.loop == 5

    def test_loop_validation_rejects_zero(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "loop_3.aep")
        ).main_source
        with pytest.raises(ValueError, match="must be >= 1"):
            source.loop = 0

    def test_loop_validation_rejects_too_high(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "loop_3.aep")
        ).main_source
        with pytest.raises(ValueError, match="must be <= 9999"):
            source.loop = 10000




class TestRoundtripInvertAlpha:
    """Roundtrip tests for FootageSource.invert_alpha."""

    def test_modify_invert_alpha(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "invertAlpha_true.aep").project
        footage = project.footages[0]
        source = footage.main_source
        assert source.invert_alpha is True

        source.invert_alpha = False
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert source2.invert_alpha is False




class TestRoundtripHighQualityFieldSeparation:
    """Roundtrip tests for FootageSource.high_quality_field_separation."""

    def test_modify_high_quality_field_separation(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "highQualityFieldSeparation_true.aep"
        ).project
        footage = project.footages[0]
        source = footage.main_source
        assert source.high_quality_field_separation is True

        source.high_quality_field_separation = False
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert source2.high_quality_field_separation is False




class TestRoundtripAlphaMode:
    """Roundtrip tests for FootageSource.alpha_mode."""

    def test_modify_alpha_mode_straight_to_premultiplied(
        self, tmp_path: Path
    ) -> None:
        project = parse_aep(SAMPLES_DIR / "alphaMode_STRAIGHT.aep").project
        footage = project.footages[0]
        source = footage.main_source
        assert source.alpha_mode == AlphaMode.STRAIGHT

        source.alpha_mode = AlphaMode.PREMULTIPLIED
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert source2.alpha_mode == AlphaMode.PREMULTIPLIED

    def test_modify_alpha_mode_to_ignore(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "alphaMode_STRAIGHT.aep").project
        footage = project.footages[0]
        source = footage.main_source

        source.alpha_mode = AlphaMode.IGNORE
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert source2.alpha_mode == AlphaMode.IGNORE

    def test_alpha_mode_validation_rejects_invalid(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "alphaMode_STRAIGHT.aep")
        ).main_source
        with pytest.raises(ValueError, match="Invalid value.*alpha_mode"):
            source.alpha_mode = 999  # type: ignore[assignment]




class TestRoundtripFieldSeparationType:
    """Roundtrip tests for FootageSource.field_separation_type."""

    def test_modify_field_separation_upper_to_lower(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "fieldSeparationType_UPPER.aep"
        ).project
        footage = project.footages[0]
        source = footage.main_source
        assert source.field_separation_type == FieldSeparationType.UPPER_FIELD_FIRST

        source.field_separation_type = FieldSeparationType.LOWER_FIELD_FIRST
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert source2.field_separation_type == FieldSeparationType.LOWER_FIELD_FIRST

    def test_modify_field_separation_to_off(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "fieldSeparationType_UPPER.aep"
        ).project
        footage = project.footages[0]
        source = footage.main_source

        source.field_separation_type = FieldSeparationType.OFF
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert source2.field_separation_type == FieldSeparationType.OFF

    def test_field_separation_type_validation_rejects_invalid(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "fieldSeparationType_UPPER.aep")
        ).main_source
        with pytest.raises(ValueError, match="is not a valid FieldSeparationType"):
            source.field_separation_type = "invalid"  # type: ignore[assignment]




class TestRoundtripPremulColor:
    """Roundtrip tests for FootageSource.premul_color."""

    def test_modify_premul_color(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "premulColor_red.aep").project
        footage = project.footages[0]
        source = footage.main_source

        source.premul_color = [0.0, 1.0, 0.5]
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert math.isclose(source2.premul_color[0], 0.0, abs_tol=0.005)
        assert math.isclose(source2.premul_color[1], 1.0, abs_tol=0.005)
        assert math.isclose(source2.premul_color[2], 0.5, abs_tol=0.02)

    def test_premul_color_validation_rejects_bad_length(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "premulColor_red.aep")
        ).main_source
        with pytest.raises(ValueError, match="expected 3 elements"):
            source.premul_color = [0.1, 0.2]

    def test_premul_color_validation_rejects_out_of_range(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "premulColor_red.aep")
        ).main_source
        with pytest.raises(ValueError, match="must be <= 1.0"):
            source.premul_color = [1.5, 0.0, 0.0]




class TestRoundtripConformFrameRate:
    """Roundtrip tests for FootageSource.conform_frame_rate."""

    def test_modify_conform_frame_rate(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "conformFrameRate_30.aep").project
        footage = project.footages[0]
        source = footage.main_source
        assert source.conform_frame_rate == 30.0

        source.conform_frame_rate = 24.0
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert source2.conform_frame_rate == 24.0

    def test_modify_conform_frame_rate_to_zero(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "conformFrameRate_30.aep").project
        footage = project.footages[0]
        source = footage.main_source

        source.conform_frame_rate = 0.0
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert source2.conform_frame_rate == 0.0

    def test_modify_conform_frame_rate_fractional(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "conform_frame_rate_2.5.aep").project
        footage = project.footages[0]
        source = footage.main_source
        assert source.conform_frame_rate == 2.5

        source.conform_frame_rate = 29.97
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert math.isclose(source2.conform_frame_rate, 29.97, rel_tol=1e-4)

    def test_conform_frame_rate_validation_rejects_negative(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conformFrameRate_30.aep")
        ).main_source
        with pytest.raises(ValueError, match="must be >= 0"):
            source.conform_frame_rate = -1.0

    def test_conform_frame_rate_validation_rejects_too_high(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conformFrameRate_30.aep")
        ).main_source
        with pytest.raises(ValueError, match="must be <= 999"):
            source.conform_frame_rate = 1000.0




class TestNativeFrameRate:
    """Read-only tests for FootageSource.native_frame_rate."""

    def test_native_frame_rate(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conformFrameRate_24.aep")
        ).main_source
        assert source.native_frame_rate == 30.0




class TestDisplayFrameRate:
    """Read-only tests for FootageSource.display_frame_rate."""

    def test_display_frame_rate_with_conform(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conformFrameRate_24.aep")
        ).main_source
        assert source.display_frame_rate == 24.0

    def test_display_frame_rate_without_conform(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "loop_3.aep")
        ).main_source
        assert source.conform_frame_rate == 0.0
        assert source.display_frame_rate == 30.0

    def test_display_frame_rate_with_pulldown(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conform_frame_rate_2.5_uff_wssww.aep")
        ).main_source
        assert source.conform_frame_rate == 2.5
        assert source.display_frame_rate == 2.0

    def test_display_frame_rate_without_pulldown(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conform_frame_rate_2.5_uff_off.aep")
        ).main_source
        assert source.conform_frame_rate == 2.5
        assert source.display_frame_rate == 2.5




class TestRemovePulldown:
    """Roundtrip tests for FootageSource.remove_pulldown."""

    def test_read_off(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conform_frame_rate_2.5_uff_off.aep")
        ).main_source
        assert source.remove_pulldown == PulldownPhase.OFF

    def test_read_wssww(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conform_frame_rate_2.5_uff_wssww.aep")
        ).main_source
        assert source.remove_pulldown == PulldownPhase.WSSWW

    def test_read_sswww(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conform_frame_rate_2.5_uff_sswww.aep")
        ).main_source
        assert source.remove_pulldown == PulldownPhase.SSWWW

    def test_read_wwwsw_24p(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conform_frame_rate_2.5_uff_wwwsw.aep")
        ).main_source
        assert source.remove_pulldown == PulldownPhase.WWWSW_24P_ADVANCE

    def test_modify_pulldown(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "conform_frame_rate_2.5_uff_off.aep").project
        source = project.footages[0].main_source
        assert source.remove_pulldown == PulldownPhase.OFF

        source.remove_pulldown = PulldownPhase.WSSWW
        out = tmp_path / "out.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source
        assert source2.remove_pulldown == PulldownPhase.WSSWW

    def test_modify_pulldown_invalidates_display_frame_rate(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "conform_frame_rate_2.5_uff_off.aep")
        ).main_source
        assert source.display_frame_rate == 2.5
        source.remove_pulldown = PulldownPhase.WSSWW
        assert source.display_frame_rate == 2.0




class TestInterpretAsLinearLight:
    """Tests for FootageSource.interpret_as_linear_light."""

    def test_off(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "interpret_as_linear_light_off.aep")
        ).main_source
        assert source.interpret_as_linear_light == LinearLightMode.OFF

    def test_on(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "interpret_as_linear_light_on.aep")
        ).main_source
        assert source.interpret_as_linear_light == LinearLightMode.ON

    def test_on_for_32_bpc(self) -> None:
        source = get_first_footage(
            parse_project(
                SAMPLES_DIR / "interpret_as_linear_light_on_for_32_bpc.aep"
            )
        ).main_source
        assert source.interpret_as_linear_light == LinearLightMode.ON_FOR_32BPC

    def test_is_writable(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "interpret_as_linear_light_off.aep")
        ).main_source
        source.interpret_as_linear_light = LinearLightMode.ON
        assert source.interpret_as_linear_light == LinearLightMode.ON

    def test_modify_roundtrip(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "interpret_as_linear_light_off.aep"
        ).project
        source = get_first_footage(project).main_source
        assert source.interpret_as_linear_light == LinearLightMode.OFF

        source.interpret_as_linear_light = LinearLightMode.ON
        out = tmp_path / "modified.aep"
        project.save(out)
        source2 = get_first_footage(parse_aep(out).project).main_source
        assert source2.interpret_as_linear_light == LinearLightMode.ON




class TestPreserveRgb:
    """Tests for FootageSource.preserve_rgb."""

    def test_on(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "preserve_rgb_on.aep")
        ).main_source
        assert source.preserve_rgb is True

    def test_off(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "preserve_rgb_off.aep")
        ).main_source
        assert source.preserve_rgb is False

    def test_is_writable(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "preserve_rgb_on.aep")
        ).main_source
        source.preserve_rgb = False
        assert source.preserve_rgb is False




class TestOverrideMediaColorSpace:
    """Tests for FootageSource.media_color_space."""

    def test_embedded(self) -> None:
        source = get_first_footage(
            parse_project(
                SAMPLES_DIR / "override_media_colorspace_embedded.aep"
            )
        ).main_source
        assert source.media_color_space == "Embedded"

    def test_custom_profile(self) -> None:
        source = get_first_footage(
            parse_project(
                SAMPLES_DIR / "override_media_colorspace_apple_rgb.aep"
            )
        ).main_source
        assert source.media_color_space == "Apple RGB"

    def test_working_colorspace(self) -> None:
        source = get_first_footage(
            parse_project(
                SAMPLES_DIR / "override_media_colorspace_working_colorspace_-.aep"
            )
        ).main_source
        assert source.media_color_space == "Working Color Space"

    def test_working_colorspace_aces(self) -> None:
        source = get_first_footage(
            parse_project(
                SAMPLES_DIR
                / "override_media_colorspace_working_colorspace_-aces_cg_or_cct.aep"
            )
        ).main_source
        assert source.media_color_space == "Working Color Space"

    def test_is_read_only(self) -> None:
        source = get_first_footage(
            parse_project(
                SAMPLES_DIR / "override_media_colorspace_embedded.aep"
            )
        ).main_source
        with pytest.raises(AttributeError):
            source.media_color_space = "Apple RGB"  # type: ignore[misc]




class TestRoundtripSolidColor:
    """Roundtrip tests for SolidSource.color."""

    def test_modify_color(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "color_red.aep").project
        footage = project.footages[0]
        source = footage.main_source

        # Modify
        source.color = [0.1, 0.2, 0.3]

        # Save and re-parse
        out = tmp_path / "modified_solid.aep"
        project.save(out)
        source2 = parse_aep(out).project.footages[0].main_source

        assert math.isclose(source2.color[0], 0.1, abs_tol=0.005)
        assert math.isclose(source2.color[1], 0.2, abs_tol=0.005)
        assert math.isclose(source2.color[2], 0.3, abs_tol=0.005)

    def test_validation_rejects_bad_length(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "color_red.aep")
        ).main_source
        with pytest.raises(ValueError, match="expected 3 elements"):
            source.color = [0.1, 0.2]

    def test_validation_rejects_out_of_range(self) -> None:
        source = get_first_footage(
            parse_project(SAMPLES_DIR / "color_red.aep")
        ).main_source
        with pytest.raises(ValueError, match="must be <= 1.0"):
            source.color = [1.5, 0.0, 0.0]


class TestHasAudio:
    """Tests for FootageItem.has_audio."""

    def test_footage_with_audio(self) -> None:
        project = parse_project(SAMPLES_DIR / "no_audio.aep")
        footage = next(
            f for f in project.footages if f.name == "mov_23_976.mov"
        )
        assert footage.has_audio is True

    def test_footage_without_audio(self) -> None:
        project = parse_project(SAMPLES_DIR / "no_audio.aep")
        footage = next(
            f for f in project.footages
            if f.name == "mov_23_976_no_audio.mov"
        )
        assert footage.has_audio is False
