"""Tests for MarkerValue model parsing."""

from __future__ import annotations

import math
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from conftest import (
    get_comp_marker_from_json,
    get_layer_marker_from_json,
    get_sample_files,
    load_expected,
    parse_project,
)

from aep_parser import Project
from aep_parser.enums import Label

if TYPE_CHECKING:
    from aep_parser import MarkerValue

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "marker"


@pytest.mark.parametrize("sample_name", get_sample_files(SAMPLES_DIR))
def test_parse_marker_sample(sample_name: str) -> None:
    """Each marker sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


def get_first_comp_marker(project: Project) -> MarkerValue:
    """Get the first marker value from the first composition."""
    assert len(project.compositions) >= 1
    comp = project.compositions[0]
    assert len(comp.markers) >= 1
    return comp.markers[0]


def get_first_layer_marker(project: Project) -> MarkerValue:
    """Get the first marker value from the first layer."""
    assert len(project.compositions) >= 1
    comp = project.compositions[0]
    assert len(comp.layers) >= 1
    layer = comp.layers[0]
    assert len(layer.markers) >= 1
    return layer.markers[0]


class TestCompMarkerLabel:
    """Tests for composition marker label."""

    def test_label_0(self) -> None:
        expected = load_expected(SAMPLES_DIR, "label_0")
        marker_json = get_comp_marker_from_json(expected)
        marker = get_first_comp_marker(parse_project(SAMPLES_DIR / "label_0.aep"))
        assert marker.label.value == marker_json["label"] == 0

    def test_label_3(self) -> None:
        expected = load_expected(SAMPLES_DIR, "label_3")
        marker_json = get_comp_marker_from_json(expected)
        marker = get_first_comp_marker(parse_project(SAMPLES_DIR / "label_3.aep"))
        assert marker.label.value == marker_json["label"] == 3

    def test_label_8(self) -> None:
        expected = load_expected(SAMPLES_DIR, "label_8")
        marker_json = get_comp_marker_from_json(expected)
        marker = get_first_comp_marker(parse_project(SAMPLES_DIR / "label_8.aep"))
        assert marker.label.value == marker_json["label"] == 8


class TestCompMarkerDuration:
    """Tests for composition marker duration."""

    def test_duration_5(self) -> None:
        expected = load_expected(SAMPLES_DIR, "duration_5")
        marker_json = get_comp_marker_from_json(expected)
        marker = get_first_comp_marker(parse_project(SAMPLES_DIR / "duration_5.aep"))
        assert marker_json["duration"] == 5
        assert math.isclose(marker.duration, marker_json["duration"])


class TestCompMarkerComment:
    """Tests for composition marker comment."""

    def test_comment(self) -> None:
        expected = load_expected(SAMPLES_DIR, "comment")
        marker_json = get_comp_marker_from_json(expected)
        marker = get_first_comp_marker(parse_project(SAMPLES_DIR / "comment.aep"))
        assert marker.comment == marker_json["comment"] == "Test comment"


class TestCompMarkerChapter:
    """Tests for composition marker chapter."""

    def test_chapter(self) -> None:
        expected = load_expected(SAMPLES_DIR, "chapter")
        marker_json = get_comp_marker_from_json(expected)
        marker = get_first_comp_marker(parse_project(SAMPLES_DIR / "chapter.aep"))
        assert marker.chapter == marker_json["chapter"] == "Chapter 1"


class TestCompMarkerUrl:
    """Tests for composition marker URL."""

    def test_url(self) -> None:
        expected = load_expected(SAMPLES_DIR, "url")
        marker_json = get_comp_marker_from_json(expected)
        marker = get_first_comp_marker(parse_project(SAMPLES_DIR / "url.aep"))
        assert marker.url == marker_json["url"] == "https://example.com"


class TestCompMarkerFrameTarget:
    """Tests for composition marker frame target."""

    def test_frameTarget(self) -> None:
        expected = load_expected(SAMPLES_DIR, "frameTarget")
        marker_json = get_comp_marker_from_json(expected)
        marker = get_first_comp_marker(parse_project(SAMPLES_DIR / "frameTarget.aep"))
        assert marker.frame_target == marker_json["frameTarget"] == "_blank"


class TestCompMarkerCuePoint:
    """Tests for composition marker cue point."""

    def test_cuePointName(self) -> None:
        expected = load_expected(SAMPLES_DIR, "cuePointName")
        marker_json = get_comp_marker_from_json(expected)
        marker = get_first_comp_marker(parse_project(SAMPLES_DIR / "cuePointName.aep"))
        assert marker.cue_point_name == marker_json["cuePointName"] == "cue_test"


class TestCompMarkerProtectedRegion:
    """Tests for composition marker protected region."""

    def test_protectedRegion_true(self) -> None:
        expected = load_expected(SAMPLES_DIR, "protectedRegion_true")
        marker_json = get_comp_marker_from_json(expected)
        marker = get_first_comp_marker(
            parse_project(SAMPLES_DIR / "protectedRegion_true.aep")
        )
        assert marker_json["protectedRegion"] is True
        assert marker.protected_region == marker_json["protectedRegion"]


class TestLayerMarker:
    """Tests for layer markers."""

    def test_layer_marker_comment(self) -> None:
        expected = load_expected(SAMPLES_DIR, "layer_comment")
        marker_json = get_layer_marker_from_json(expected)
        marker = get_first_layer_marker(
            parse_project(SAMPLES_DIR / "layer_comment.aep")
        )
        assert marker.comment == marker_json["comment"] == "Layer marker comment"

    def test_layer_marker_duration(self) -> None:
        expected = load_expected(SAMPLES_DIR, "layer_duration")
        marker_json = get_layer_marker_from_json(expected)
        marker = get_first_layer_marker(
            parse_project(SAMPLES_DIR / "layer_duration.aep")
        )
        assert marker_json["duration"] == 3
        assert math.isclose(marker.duration, marker_json["duration"])

    def test_layer_marker_cuePointName(self) -> None:
        expected = load_expected(SAMPLES_DIR, "layer_cuePointName")
        marker_json = get_layer_marker_from_json(expected)
        marker = get_first_layer_marker(
            parse_project(SAMPLES_DIR / "layer_cuePointName.aep")
        )
        assert marker.cue_point_name == marker_json["cuePointName"] == "layer_cue_1"

    def test_layer_marker_with_startTime(self) -> None:
        """Marker time is at comp time 5, layer startTime is 3."""
        expected = load_expected(SAMPLES_DIR, "layer_marker_with_startTime")
        marker_json = get_layer_marker_from_json(expected)
        marker = get_first_layer_marker(
            parse_project(SAMPLES_DIR / "layer_marker_with_startTime.aep")
        )
        assert (
            marker.comment
            == marker_json["comment"]
            == "marker at comp time 5"
        )

    def test_layer_multiple_markers(self) -> None:
        """Three markers on one layer, parsed in correct order."""
        project = parse_project(SAMPLES_DIR / "layer_multiple_markers.aep")
        comp = project.compositions[0]
        layer = comp.layers[0]
        assert len(layer.markers) == 3
        assert layer.markers[0].comment == "first marker"
        assert layer.markers[1].comment == "second marker"
        assert layer.markers[2].comment == "Third"


class TestRoundtripMarkerComment:
    """Roundtrip tests for MarkerValue.comment."""

    def test_modify_comment(self, tmp_path: Path) -> None:
        project = parse_project(SAMPLES_DIR / "comment.aep")
        marker = get_first_comp_marker(project)
        original = marker.comment
        assert original != ""

        marker.comment = "modified comment"
        out = tmp_path / "modified_comment.aep"
        project.save(out)
        marker2 = get_first_comp_marker(parse_project(out))
        assert marker2.comment == "modified comment"


class TestRoundtripMarkerDuration:
    """Roundtrip tests for MarkerValue.duration and frame_duration."""

    def test_modify_frame_duration(self, tmp_path: Path) -> None:
        project = parse_project(SAMPLES_DIR / "duration_5.aep")
        marker = get_first_comp_marker(project)
        original_fd = marker.frame_duration

        marker.frame_duration = original_fd + 10
        out = tmp_path / "modified_frame_duration.aep"
        project.save(out)
        marker2 = get_first_comp_marker(parse_project(out))
        assert marker2.frame_duration == original_fd + 10

    def test_modify_duration(self, tmp_path: Path) -> None:
        project = parse_project(SAMPLES_DIR / "duration_5.aep")
        marker = get_first_comp_marker(project)

        marker.duration = 10.0
        out = tmp_path / "modified_duration.aep"
        project.save(out)
        marker2 = get_first_comp_marker(parse_project(out))
        assert math.isclose(marker2.duration, 10.0, abs_tol=0.01)


class TestValidateMarkerFrameDuration:
    """Validation tests for MarkerValue.frame_duration."""

    def test_frame_duration_rejects_negative(self) -> None:
        project = parse_project(SAMPLES_DIR / "duration_5.aep")
        marker = get_first_comp_marker(project)
        with pytest.raises(ValueError, match="must be >= 0"):
            marker.frame_duration = -1

    def test_frame_duration_rejects_float(self) -> None:
        project = parse_project(SAMPLES_DIR / "duration_5.aep")
        marker = get_first_comp_marker(project)
        with pytest.raises(TypeError, match="expected an integer"):
            marker.frame_duration = 1.5


class TestRoundtripMarkerLabel:
    """Roundtrip tests for MarkerValue.label."""

    def test_modify_label(self, tmp_path: Path) -> None:
        project = parse_project(SAMPLES_DIR / "label_3.aep")
        marker = get_first_comp_marker(project)
        assert marker.label == Label.AQUA

        marker.label = Label.RED
        out = tmp_path / "modified_label.aep"
        project.save(out)
        marker2 = get_first_comp_marker(parse_project(out))
        assert marker2.label == Label.RED


class TestRoundtripMarkerNavigation:
    """Roundtrip tests for MarkerValue.navigation."""

    def test_modify_navigation(self, tmp_path: Path) -> None:
        project = parse_project(SAMPLES_DIR / "comment.aep")
        marker = get_first_comp_marker(project)
        original = marker.navigation

        marker.navigation = not original
        out = tmp_path / "modified_navigation.aep"
        project.save(out)
        marker2 = get_first_comp_marker(parse_project(out))
        assert marker2.navigation == (not original)
        assert marker2.event_cue_point == original


class TestRoundtripMarkerProtectedRegion:
    """Roundtrip tests for MarkerValue.protected_region."""

    def test_modify_protected_region(self, tmp_path: Path) -> None:
        project = parse_project(SAMPLES_DIR / "protectedRegion_true.aep")
        marker = get_first_comp_marker(project)
        assert marker.protected_region is True

        marker.protected_region = False
        out = tmp_path / "modified_protected_region.aep"
        project.save(out)
        marker2 = get_first_comp_marker(parse_project(out))
        assert marker2.protected_region is False


class TestRoundtripMarkerChapter:
    """Roundtrip tests for MarkerValue.chapter."""

    def test_modify_chapter(self, tmp_path: Path) -> None:
        project = parse_project(SAMPLES_DIR / "chapter.aep")
        marker = get_first_comp_marker(project)
        assert marker.chapter != ""

        marker.chapter = "modified chapter"
        out = tmp_path / "modified_chapter.aep"
        project.save(out)
        marker2 = get_first_comp_marker(parse_project(out))
        assert marker2.chapter == "modified chapter"


class TestRoundtripMarkerUrl:
    """Roundtrip tests for MarkerValue.url."""

    def test_modify_url(self, tmp_path: Path) -> None:
        project = parse_project(SAMPLES_DIR / "url.aep")
        marker = get_first_comp_marker(project)
        assert marker.url != ""

        marker.url = "https://example.com/modified"
        out = tmp_path / "modified_url.aep"
        project.save(out)
        marker2 = get_first_comp_marker(parse_project(out))
        assert marker2.url == "https://example.com/modified"


class TestRoundtripMarkerFrameTarget:
    """Roundtrip tests for MarkerValue.frame_target."""

    def test_modify_frame_target(self, tmp_path: Path) -> None:
        project = parse_project(SAMPLES_DIR / "frameTarget.aep")
        marker = get_first_comp_marker(project)
        assert marker.frame_target != ""

        marker.frame_target = "_blank"
        out = tmp_path / "modified_frame_target.aep"
        project.save(out)
        marker2 = get_first_comp_marker(parse_project(out))
        assert marker2.frame_target == "_blank"


class TestRoundtripMarkerCuePointName:
    """Roundtrip tests for MarkerValue.cue_point_name."""

    def test_modify_cue_point_name(self, tmp_path: Path) -> None:
        project = parse_project(SAMPLES_DIR / "cuePointName.aep")
        marker = get_first_comp_marker(project)
        assert marker.cue_point_name != ""

        marker.cue_point_name = "modified_cue"
        out = tmp_path / "modified_cue_point_name.aep"
        project.save(out)
        marker2 = get_first_comp_marker(parse_project(out))
        assert marker2.cue_point_name == "modified_cue"
