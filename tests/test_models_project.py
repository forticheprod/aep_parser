"""Tests for Project model parsing using samples from models/project/.

These tests verify that aep_parser produces the same values as the JSON
reference files exported from After Effects.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aep_parser import Project, parse_project

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "project"


def get_sample_files() -> list[str]:
    """Get all .aep files in the project samples directory."""
    if not SAMPLES_DIR.exists():
        return []
    return [f.stem for f in SAMPLES_DIR.glob("*.aep")]


def load_expected(sample_name: str) -> dict:
    """Load the expected JSON for a sample."""
    json_path = SAMPLES_DIR / f"{sample_name}.json"
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("sample_name", get_sample_files())
def test_parse_project_sample(sample_name: str) -> None:
    """Test that each project sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


class TestBitsPerChannel:
    """Tests for bitsPerChannel attribute."""

    def test_8bpc(self) -> None:
        """Test 8 bits per channel project."""
        expected = load_expected("bitsPerChannel_8")
        project = parse_project(SAMPLES_DIR / "bitsPerChannel_8.aep")
        assert expected["bitsPerChannel"] == 8
        assert project.bits_per_channel.value == expected["bitsPerChannel"]

    def test_16bpc(self) -> None:
        """Test 16 bits per channel project."""
        expected = load_expected("bitsPerChannel_16")
        project = parse_project(SAMPLES_DIR / "bitsPerChannel_16.aep")
        assert expected["bitsPerChannel"] == 16
        assert project.bits_per_channel.value == expected["bitsPerChannel"]

    def test_32bpc(self) -> None:
        """Test 32 bits per channel project."""
        expected = load_expected("bitsPerChannel_32")
        project = parse_project(SAMPLES_DIR / "bitsPerChannel_32.aep")
        assert expected["bitsPerChannel"] == 32
        assert project.bits_per_channel.value == expected["bitsPerChannel"]


class TestExpressionEngine:
    """Tests for expressionEngine attribute."""

    def test_javascript(self) -> None:
        """Test JavaScript expression engine."""
        expected = load_expected("expressionEngine_javascript")
        project = parse_project(SAMPLES_DIR / "expressionEngine_javascript.aep")
        assert expected["expressionEngine"] == "javascript-1.0"
        assert project.expression_engine == expected["expressionEngine"]


class TestDisplayStartFrame:
    """Tests for displayStartFrame attribute."""

    def test_displayStartFrame_1(self) -> None:
        """Test display start frame set to 1."""
        expected = load_expected("displayStartFrame_1")
        project = parse_project(SAMPLES_DIR / "displayStartFrame_1.aep")
        assert expected["displayStartFrame"] == 1
        assert project.display_start_frame == expected["displayStartFrame"]


class TestFramesCountType:
    """Tests for framesCountType attribute."""

    def test_start0(self) -> None:
        """Test frames count starting at 0."""
        load_expected("framesCountType_start0")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "framesCountType_start0.aep")
        # framesCountType START_ZERO means display_start_frame is 0
        assert project.display_start_frame == 0


class TestWorkingGamma:
    """Tests for workingGamma attribute."""

    def test_workingGamma_2_4(self) -> None:
        """Test working gamma of 2.4."""
        load_expected("workingGamma_2.4")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "workingGamma_2.4.aep")
        assert project.working_gamma == 2.4

    def test_workingGamma_2_2(self) -> None:
        """Test working gamma of 2.2."""
        load_expected("workingGamma_2.2")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "workingGamma_2.2.aep")
        assert project.working_gamma == 2.2


class TestWorkingSpace:
    """Tests for workingSpace attribute."""

    def test_workingSpace_sRGB(self) -> None:
        """Test sRGB working space."""
        load_expected("workingSpace_sRGB")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "workingSpace_sRGB.aep")
        # TODO: Add assertion when working_space is parsed
        assert isinstance(project, Project)


class TestLinearBlending:
    """Tests for linearBlending attribute."""

    def test_linearBlending_false(self) -> None:
        """Test linear blending enabled."""
        load_expected("linearBlending_false")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "linearBlending_false.aep")
        assert not project.linear_blending

    def test_linearBlending_true(self) -> None:
        """Test linear blending enabled."""
        load_expected("linearBlending_true")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "linearBlending_true.aep")
        assert project.linear_blending


class TestTransparencyGridThumbnails:
    """Tests for transparencyGridThumbnails attribute."""

    def test_transparencyGridThumbnails_true(self) -> None:
        """Test transparency grid thumbnails enabled."""
        load_expected("transparencyGridThumbnails_true")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "transparencyGridThumbnails_true.aep")
        # TODO: Add assertion when transparency_grid_thumbnails is parsed
        assert isinstance(project, Project)


class TestColorManagement:
    """Tests for CC 2024+ color management attributes."""

    def test_colorManagementSystem_adobe(self) -> None:
        """Test Adobe color management system."""
        json_path = SAMPLES_DIR / "colorManagementSystem_adobe.json"
        if not json_path.exists():
            pytest.skip("colorManagementSystem_adobe sample not available")
        load_expected("colorManagementSystem_adobe")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "colorManagementSystem_adobe.aep")
        assert project.color_management_system.name == "ADOBE"

    def test_colorManagementSystem_ocio(self) -> None:
        """Test OCIO color management system."""
        json_path = SAMPLES_DIR / "colorManagementSystem_ocio.json"
        if not json_path.exists():
            pytest.skip("colorManagementSystem_ocio sample not available")
        load_expected("colorManagementSystem_ocio")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "colorManagementSystem_ocio.aep")
        assert project.color_management_system.name == "OCIO"

    def test_lutInterpolationMethod_trilinear(self) -> None:
        """Test trilinear LUT interpolation."""
        json_path = SAMPLES_DIR / "lutInterpolationMethod_trilinear.json"
        if not json_path.exists():
            pytest.skip("lutInterpolationMethod_trilinear sample not available")
        load_expected("lutInterpolationMethod_trilinear")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "lutInterpolationMethod_trilinear.aep")
        assert project.lut_interpolation_method == project.lut_interpolation_method.TRILINEAR

    def test_lutInterpolationMethod_tetrahedral(self) -> None:
        """Test tetrahedral LUT interpolation."""
        json_path = SAMPLES_DIR / "lutInterpolationMethod_tetrahedral.json"
        if not json_path.exists():
            pytest.skip("lutInterpolationMethod_tetrahedral sample not available")
        load_expected("lutInterpolationMethod_tetrahedral")  # Verify JSON exists
        project = parse_project(SAMPLES_DIR / "lutInterpolationMethod_tetrahedral.aep")
        assert project.lut_interpolation_method == project.lut_interpolation_method.TETRAHEDRAL
