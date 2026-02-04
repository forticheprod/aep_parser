"""Tests for Marker model parsing using samples from models/marker/.

These tests verify that aep_parser produces the same values as the JSON
reference files exported from After Effects.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from aep_parser import Project, parse_project

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "marker"


def get_sample_files() -> list[str]:
    """Get all .aep files in the marker samples directory."""
    if not SAMPLES_DIR.exists():
        return []
    return [f.stem for f in SAMPLES_DIR.glob("*.aep")]


def load_expected(sample_name: str) -> dict:
    """Load the expected JSON for a sample."""
    json_path = SAMPLES_DIR / f"{sample_name}.json"
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def get_comp_marker_from_json(expected: dict) -> dict:
    """Extract first composition marker from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Composition":
                markers = item.get("markers", [])
                if isinstance(markers, list) and len(markers) > 0:
                    return markers[0]
    return {}


def get_layer_marker_from_json(expected: dict) -> dict:
    """Extract first layer marker from expected JSON."""
    if "items" in expected:
        for item in expected["items"]:
            if item.get("typeName") == "Composition" and "layers" in item:
                for layer in item["layers"]:
                    if "markers" in layer and len(layer["markers"]) > 0:
                        return layer["markers"][0]
    return {}


@pytest.mark.parametrize("sample_name", get_sample_files())
def test_parse_marker_sample(sample_name: str) -> None:
    """Test that each marker sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


def get_first_comp_marker(project: Project):
    """Get the first marker from the first composition."""
    assert len(project.compositions) >= 1
    comp = project.compositions[0]
    assert len(comp.markers) >= 1
    return comp.markers[0]


def get_first_layer_marker(project: Project):
    """Get the first marker from the first layer."""
    assert len(project.compositions) >= 1
    comp = project.compositions[0]
    assert len(comp.layers) >= 1
    layer = comp.layers[0]
    assert len(layer.markers) >= 1
    return layer.markers[0]


class TestCompMarkerLabel:
    """Tests for composition marker label attribute."""

    def test_label_0(self) -> None:
        """Test marker with label 0."""
        expected = load_expected("label_0")
        marker_json = get_comp_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "label_0.aep")
        marker = get_first_comp_marker(project)
        assert marker_json["label"] == 0
        assert marker.label.value == marker_json["label"]

    def test_label_3(self) -> None:
        """Test marker with label 3."""
        expected = load_expected("label_3")
        marker_json = get_comp_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "label_3.aep")
        marker = get_first_comp_marker(project)
        assert marker_json["label"] == 3
        assert marker.label.value == marker_json["label"]

    def test_label_8(self) -> None:
        """Test marker with label 8."""
        expected = load_expected("label_8")
        marker_json = get_comp_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "label_8.aep")
        marker = get_first_comp_marker(project)
        assert marker_json["label"] == 8
        assert marker.label.value == marker_json["label"]


class TestCompMarkerDuration:
    """Tests for composition marker duration attribute."""

    def test_duration_5(self) -> None:
        """Test marker with 5 second duration."""
        expected = load_expected("duration_5")
        marker_json = get_comp_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "duration_5.aep")
        marker = get_first_comp_marker(project)
        assert marker_json["duration"] == 5
        assert math.isclose(marker.duration, marker_json["duration"])


class TestCompMarkerComment:
    """Tests for composition marker comment attribute."""

    def test_comment(self) -> None:
        """Test marker with comment."""
        expected = load_expected("comment")
        marker_json = get_comp_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "comment.aep")
        marker = get_first_comp_marker(project)
        assert marker_json["comment"] == "Test comment"
        assert marker.comment == marker_json["comment"]


class TestCompMarkerChapter:
    """Tests for composition marker chapter attribute."""

    def test_chapter(self) -> None:
        """Test marker with chapter."""
        expected = load_expected("chapter")
        marker_json = get_comp_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "chapter.aep")
        marker = get_first_comp_marker(project)
        assert marker_json["chapter"] == "Chapter 1"
        assert marker.chapter == marker_json["chapter"]


class TestCompMarkerUrl:
    """Tests for composition marker URL attribute."""

    def test_url(self) -> None:
        """Test marker with URL."""
        expected = load_expected("url")
        marker_json = get_comp_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "url.aep")
        marker = get_first_comp_marker(project)
        assert marker_json["url"] == "https://example.com"
        assert marker.url == marker_json["url"]


class TestCompMarkerFrameTarget:
    """Tests for composition marker frame target attribute."""

    def test_frameTarget(self) -> None:
        """Test marker with frame target."""
        expected = load_expected("frameTarget")
        marker_json = get_comp_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "frameTarget.aep")
        marker = get_first_comp_marker(project)
        assert marker_json["frameTarget"] == "_blank"
        assert marker.frame_target == marker_json["frameTarget"]


class TestCompMarkerCuePoint:
    """Tests for composition marker cue point attribute."""

    def test_cuePointName(self) -> None:
        """Test marker with cue point name."""
        expected = load_expected("cuePointName")
        marker_json = get_comp_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "cuePointName.aep")
        marker = get_first_comp_marker(project)
        assert marker_json["cuePointName"] == "cue_test"
        assert marker.cue_point_name == marker_json["cuePointName"]


class TestCompMarkerProtectedRegion:
    """Tests for composition marker protected region attribute."""

    def test_protectedRegion_true(self) -> None:
        """Test marker with protected region."""
        expected = load_expected("protectedRegion_true")
        marker_json = get_comp_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "protectedRegion_true.aep")
        marker = get_first_comp_marker(project)
        assert marker_json["protectedRegion"] is True
        assert marker.protected_region == marker_json["protectedRegion"]


class TestLayerMarker:
    """Tests for layer markers."""

    def test_layer_marker_comment(self) -> None:
        """Test layer marker with comment."""
        expected = load_expected("layer_comment")
        marker_json = get_layer_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "layer_comment.aep")
        marker = get_first_layer_marker(project)
        assert marker_json["comment"] == "Layer marker comment"
        assert marker.comment == marker_json["comment"]

    def test_layer_marker_duration(self) -> None:
        """Test layer marker with duration."""
        expected = load_expected("layer_duration")
        marker_json = get_layer_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "layer_duration.aep")
        marker = get_first_layer_marker(project)
        assert marker_json["duration"] == 3
        assert math.isclose(marker.duration, marker_json["duration"])

    def test_layer_marker_cuePointName(self) -> None:
        """Test layer marker with cue point name."""
        expected = load_expected("layer_cuePointName")
        marker_json = get_layer_marker_from_json(expected)
        project = parse_project(SAMPLES_DIR / "layer_cuePointName.aep")
        marker = get_first_layer_marker(project)
        assert marker_json["cuePointName"] == "layer_cue_1"
        assert marker.cue_point_name == marker_json["cuePointName"]
