"""Roundtrip tests: parse → modify → save → parse → verify for CompItem fields."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
from conftest import parse_project

from aep_parser import parse as parse_aep

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "composition"


# ---- bg_color ----

class TestRoundtripBgColor:
    """Roundtrip tests for CompItem.bg_color."""

    def test_modify_bg_color(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "bgColor_red.aep").project
        comp = project.compositions[0]

        # Modify
        comp.bg_color = [0.1, 0.2, 0.3]

        # Save and re-parse
        out = tmp_path / "modified_bg.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]

        assert math.isclose(comp2.bg_color[0], 0.1, abs_tol=0.005)
        assert math.isclose(comp2.bg_color[1], 0.2, abs_tol=0.005)
        assert math.isclose(comp2.bg_color[2], 0.3, abs_tol=0.005)

    def test_bg_color_validation_rejects_bad_length(self) -> None:
        comp = parse_project(SAMPLES_DIR / "bgColor_red.aep").compositions[0]
        with pytest.raises(ValueError, match="expected 3 elements"):
            comp.bg_color = [0.1, 0.2]

    def test_bg_color_validation_rejects_out_of_range(self) -> None:
        comp = parse_project(SAMPLES_DIR / "bgColor_red.aep").compositions[0]
        with pytest.raises(ValueError, match="must be <= 1.0"):
            comp.bg_color = [1.5, 0.0, 0.0]


# ---- frame_rate ----

class TestRoundtripFrameRate:
    """Roundtrip tests for CompItem.frame_rate."""

    def test_modify_frame_rate_integer(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "frameRate_30.aep").project
        comp = project.compositions[0]
        assert math.isclose(comp.frame_rate, 30.0, rel_tol=0.001)

        comp.frame_rate = 24.0
        out = tmp_path / "modified_fps.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]
        assert math.isclose(comp2.frame_rate, 24.0, rel_tol=0.001)

    def test_modify_frame_rate_fractional(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "frameRate_30.aep").project
        comp = project.compositions[0]

        comp.frame_rate = 60.0
        out = tmp_path / "modified_fps60.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]
        assert math.isclose(comp2.frame_rate, 60.0, rel_tol=0.001)

    def test_frame_rate_validation_rejects_zero(self) -> None:
        comp = parse_project(SAMPLES_DIR / "frameRate_30.aep").compositions[0]
        with pytest.raises(ValueError, match="must be >= 1.0"):
            comp.frame_rate = 0.0

    def test_frame_rate_validation_rejects_too_high(self) -> None:
        comp = parse_project(SAMPLES_DIR / "frameRate_30.aep").compositions[0]
        with pytest.raises(ValueError, match="must be <= 999.0"):
            comp.frame_rate = 1000.0


# ---- pixel_aspect ----

class TestRoundtripPixelAspect:
    """Roundtrip tests for CompItem.pixel_aspect."""

    def test_modify_pixel_aspect(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "pixelAspect_2.aep").project
        comp = project.compositions[0]
        assert math.isclose(comp.pixel_aspect, 2.0, rel_tol=0.01)

        comp.pixel_aspect = 1.0
        out = tmp_path / "modified_par.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]
        assert math.isclose(comp2.pixel_aspect, 1.0, rel_tol=0.01)

    def test_pixel_aspect_validation_rejects_invalid(self) -> None:
        comp = parse_project(SAMPLES_DIR / "pixelAspect_2.aep").compositions[0]
        with pytest.raises(ValueError, match="must be one of"):
            comp.pixel_aspect = 1.5555


# ---- width / height ----

class TestRoundtripSize:
    """Roundtrip tests for CompItem.width and .height."""

    def test_modify_width_and_height(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "size_1920x1080.aep").project
        comp = project.compositions[0]
        assert comp.width == 1920
        assert comp.height == 1080

        comp.width = 3840
        comp.height = 2160
        out = tmp_path / "modified_size.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]
        assert comp2.width == 3840
        assert comp2.height == 2160


# ---- boolean flags ----

class TestRoundtripFlags:
    """Roundtrip tests for boolean CompItem flags."""

    def test_toggle_motion_blur(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "motionBlur_true.aep").project
        comp = project.compositions[0]
        assert comp.motion_blur is True

        comp.motion_blur = False
        out = tmp_path / "modified_mb.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]
        assert comp2.motion_blur is False

    def test_toggle_frame_blending(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "frameBlending_true.aep").project
        comp = project.compositions[0]
        assert comp.frame_blending is True

        comp.frame_blending = False
        out = tmp_path / "modified_fb.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]
        assert comp2.frame_blending is False

    def test_toggle_hide_shy_layers(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "hideShyLayers_true.aep").project
        comp = project.compositions[0]
        assert comp.hide_shy_layers is True

        comp.hide_shy_layers = False
        out = tmp_path / "modified_shy.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]
        assert comp2.hide_shy_layers is False


# ---- shutter_angle / shutter_phase ----

class TestRoundtripShutter:
    """Roundtrip tests for shutter settings."""

    def test_modify_shutter_angle(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "shutterAngle_180.aep").project
        comp = project.compositions[0]

        comp.shutter_angle = 360
        out = tmp_path / "modified_shutter.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]
        assert comp2.shutter_angle == 360


# ---- resolution_factor ----

class TestRoundtripResolution:
    """Roundtrip tests for CompItem.resolution_factor."""

    def test_modify_resolution_factor(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "resolutionFactor_half.aep").project
        comp = project.compositions[0]

        comp.resolution_factor = [1, 1]
        out = tmp_path / "modified_res.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]
        assert comp2.resolution_factor == [1, 1]


# ---- time_scale (read-only) ----

class TestTimeScaleReadOnly:
    """Test that time_scale is read-only."""

    def test_time_scale_is_read_only(self) -> None:
        comp = parse_project(SAMPLES_DIR / "frameRate_30.aep").compositions[0]
        with pytest.raises(AttributeError, match="read-only"):
            comp.time_scale = 12345


# ---- duration / display_start_time ----

class TestRoundtripDerivedTimes:
    """Roundtrip tests: changing frame_rate affects derived time fields."""

    def test_frame_rate_change_updates_frame_duration(
        self, tmp_path: Path
    ) -> None:
        project = parse_aep(SAMPLES_DIR / "frameRate_30.aep").project
        comp = project.compositions[0]
        original_frame_duration = comp.frame_duration

        comp.frame_rate = 60.0
        out = tmp_path / "modified_fps60b.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]

        # Duration in seconds should be the same
        assert math.isclose(comp2.duration, comp.duration, rel_tol=0.01)
        # Frame duration should be roughly double at 60fps
        assert comp2.frame_duration > original_frame_duration


# ---- combined modifications ----

class TestRoundtripCombined:
    """Test multiple modifications at once."""

    def test_multiple_fields_at_once(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "size_1920x1080.aep").project
        comp = project.compositions[0]

        comp.width = 1280
        comp.height = 720
        comp.bg_color = [0.0, 0.0, 0.0]
        comp.frame_rate = 25.0

        out = tmp_path / "modified_multi.aep"
        project.save(out)
        comp2 = parse_aep(out).project.compositions[0]

        assert comp2.width == 1280
        assert comp2.height == 720
        assert math.isclose(comp2.bg_color[0], 0.0, abs_tol=0.005)
        assert math.isclose(comp2.bg_color[1], 0.0, abs_tol=0.005)
        assert math.isclose(comp2.bg_color[2], 0.0, abs_tol=0.005)
        assert math.isclose(comp2.frame_rate, 25.0, rel_tol=0.001)
