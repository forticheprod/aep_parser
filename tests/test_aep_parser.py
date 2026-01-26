"""Basic tests for aep_parser package."""

from __future__ import annotations

from pathlib import Path

import pytest

import aep_parser
from aep_parser import parse_project, Project


SAMPLES_DIR = Path(__file__).parent.parent / "samples"


def test_version():
    """Test that the package has a version string."""
    assert isinstance(aep_parser.__version__, str)
    assert len(aep_parser.__version__) > 0


def test_exports():
    """Test that main exports are available."""
    assert hasattr(aep_parser, "parse_project")
    assert hasattr(aep_parser, "Project")


class TestParseProject:
    """Tests for parse_project function."""

    def test_parse_empty_project(self):
        """Test parsing an empty project file."""
        project = parse_project(str(SAMPLES_DIR / "01_empty.aep"))
        assert isinstance(project, Project)
        assert project.root_folder is not None

    def test_parse_comp_project(self):
        """Test parsing a project with a composition."""
        project = parse_project(str(SAMPLES_DIR / "02_comp.aep"))
        assert isinstance(project, Project)
        assert len(project.compositions) >= 1

    def test_parse_solid_project(self):
        """Test parsing a project with a solid."""
        project = parse_project(str(SAMPLES_DIR / "03_solid.aep"))
        assert isinstance(project, Project)

    def test_project_iteration(self):
        """Test that project items can be iterated."""
        project = parse_project(str(SAMPLES_DIR / "02_comp.aep"))
        items = list(project)
        assert len(items) > 0

    def test_bits_per_channel_8bpc(self):
        """Test 8 bits per channel project."""
        project = parse_project(str(SAMPLES_DIR / "8bpc.aep"))
        assert project.bits_per_channel.name == "bpc_8"

    def test_bits_per_channel_32bpc(self):
        """Test 32 bits per channel project."""
        project = parse_project(str(SAMPLES_DIR / "32bpc.aep"))
        assert project.bits_per_channel.name == "bpc_32"


class TestComposition:
    """Tests for composition parsing."""

    def test_composition_by_name(self):
        """Test getting a composition by name."""
        project = parse_project(str(SAMPLES_DIR / "comp_names.aep"))
        # Project has at least one composition
        if project.compositions:
            comp_name = project.compositions[0].name
            found_comp = project.composition(comp_name)
            assert found_comp is not None
            assert found_comp.name == comp_name

    def test_composition_layers(self):
        """Test that compositions have layers."""
        project = parse_project(str(SAMPLES_DIR / "02_comp.aep"))
        for comp in project.compositions:
            assert isinstance(comp.layers, list)


class TestMarkers:
    """Tests for marker parsing."""

    def test_marker_parsing(self):
        """Test that markers are parsed correctly."""
        project = parse_project(str(SAMPLES_DIR / "marker.aep"))
        # Check that project parses without error
        assert isinstance(project, Project)

    def test_two_markers(self):
        """Test parsing a project with two markers."""
        project = parse_project(str(SAMPLES_DIR / "two_markers.aep"))
        assert isinstance(project, Project)
