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
    """Get the first marker from the first composition."""
    assert len(project.compositions) >= 1
    comp = project.compositions[0]
    assert len(comp.markers) >= 1
    return comp.markers[0]


def get_first_layer_marker(project: Project) -> MarkerValue:
    """Get the first marker from the first layer."""
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
        marker = get_first_comp_marker(parse_project(SAMPLES_DIR / "protectedRegion_true.aep"))
        assert marker_json["protectedRegion"] is True
        assert marker.protected_region == marker_json["protectedRegion"]


class TestLayerMarker:
    """Tests for layer markers."""

    def test_layer_marker_comment(self) -> None:
        expected = load_expected(SAMPLES_DIR, "layer_comment")
        marker_json = get_layer_marker_from_json(expected)
        marker = get_first_layer_marker(parse_project(SAMPLES_DIR / "layer_comment.aep"))
        assert marker.comment == marker_json["comment"] == "Layer marker comment"

    def test_layer_marker_duration(self) -> None:
        expected = load_expected(SAMPLES_DIR, "layer_duration")
        marker_json = get_layer_marker_from_json(expected)
        marker = get_first_layer_marker(parse_project(SAMPLES_DIR / "layer_duration.aep"))
        assert marker_json["duration"] == 3
        assert math.isclose(marker.duration, marker_json["duration"])

    def test_layer_marker_cuePointName(self) -> None:
        expected = load_expected(SAMPLES_DIR, "layer_cuePointName")
        marker_json = get_layer_marker_from_json(expected)
        marker = get_first_layer_marker(parse_project(SAMPLES_DIR / "layer_cuePointName.aep"))
        assert marker.cue_point_name == marker_json["cuePointName"] == "layer_cue_1"
