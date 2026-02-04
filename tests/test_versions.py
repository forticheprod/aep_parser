"""Tests for version-specific complete.aep samples from samples/versions/.

These tests verify that aep_parser can parse files from different
After Effects versions correctly.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aep_parser import Project, parse_project

VERSIONS_DIR = Path(__file__).parent.parent / "samples" / "versions"


def get_version_dirs() -> list[str]:
    """Get all version directories that contain complete.aep."""
    if not VERSIONS_DIR.exists():
        return []
    versions = []
    for version_dir in VERSIONS_DIR.iterdir():
        if version_dir.is_dir() and (version_dir / "complete.aep").exists():
            versions.append(version_dir.name)
    return sorted(versions)


def load_expected(version: str) -> dict:
    """Load the expected JSON for a version sample."""
    json_path = VERSIONS_DIR / version / "complete.json"
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("version", get_version_dirs())
def test_parse_version_sample(version: str) -> None:
    """Test that each version's complete.aep can be parsed."""
    aep_path = VERSIONS_DIR / version / "complete.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)


@pytest.mark.parametrize("version", get_version_dirs())
def test_version_has_compositions(version: str) -> None:
    """Test that each version sample has compositions."""
    aep_path = VERSIONS_DIR / version / "complete.aep"
    project = parse_project(aep_path)
    assert len(project.compositions) >= 1, f"{version} should have compositions"


@pytest.mark.parametrize("version", get_version_dirs())
def test_version_has_layers(version: str) -> None:
    """Test that each version sample has layers."""
    aep_path = VERSIONS_DIR / version / "complete.aep"
    project = parse_project(aep_path)
    total_layers = sum(len(comp.layers) for comp in project.compositions)
    assert total_layers >= 1, f"{version} should have layers"


@pytest.mark.parametrize("version", get_version_dirs())
def test_version_has_folders(version: str) -> None:
    """Test that each version sample has folders."""
    aep_path = VERSIONS_DIR / version / "complete.aep"
    project = parse_project(aep_path)
    # At least root folder should exist
    assert project.root_folder is not None, f"{version} should have root folder"


class TestAE2018:
    """Tests specific to After Effects 2018 (CC 15.x)."""

    @pytest.fixture
    def project(self) -> Project | None:
        """Load the AE 2018 sample project."""
        aep_path = VERSIONS_DIR / "ae2018" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("AE 2018 sample not available")
        return parse_project(aep_path)

    def test_parses_successfully(self, project: Project) -> None:
        """Test that AE 2018 project parses."""
        assert isinstance(project, Project)


class TestAE2019:
    """Tests specific to After Effects 2019 (CC 16.x)."""

    @pytest.fixture
    def project(self) -> Project | None:
        """Load the AE 2019 sample project."""
        aep_path = VERSIONS_DIR / "ae2019" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("AE 2019 sample not available")
        return parse_project(aep_path)

    def test_parses_successfully(self, project: Project) -> None:
        """Test that AE 2019 project parses."""
        assert isinstance(project, Project)

    def test_expression_engine(self, project: Project) -> None:
        """Test that expression engine is available in 2019+."""
        assert project.expression_engine is not None


class TestAE2020:
    """Tests specific to After Effects 2020 (CC 17.x)."""

    @pytest.fixture
    def project(self) -> Project | None:
        """Load the AE 2020 sample project."""
        aep_path = VERSIONS_DIR / "ae2020" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("AE 2020 sample not available")
        return parse_project(aep_path)

    def test_parses_successfully(self, project: Project) -> None:
        """Test that AE 2020 project parses."""
        assert isinstance(project, Project)


class TestAE2022:
    """Tests specific to After Effects 2022 (CC 22.x)."""

    @pytest.fixture
    def project(self) -> Project | None:
        """Load the AE 2022 sample project."""
        aep_path = VERSIONS_DIR / "ae2022" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("AE 2022 sample not available")
        return parse_project(aep_path)

    def test_parses_successfully(self, project: Project) -> None:
        """Test that AE 2022 project parses."""
        assert isinstance(project, Project)


class TestAE2023:
    """Tests specific to After Effects 2023 (CC 23.x)."""

    @pytest.fixture
    def project(self) -> Project | None:
        """Load the AE 2023 sample project."""
        aep_path = VERSIONS_DIR / "ae2023" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("AE 2023 sample not available")
        return parse_project(aep_path)

    def test_parses_successfully(self, project: Project) -> None:
        """Test that AE 2023 project parses."""
        assert isinstance(project, Project)


class TestAE2024:
    """Tests specific to After Effects 2024 (CC 24.x)."""

    @pytest.fixture
    def project(self) -> Project | None:
        """Load the AE 2024 sample project."""
        aep_path = VERSIONS_DIR / "ae2024" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("AE 2024 sample not available")
        return parse_project(aep_path)

    def test_parses_successfully(self, project: Project) -> None:
        """Test that AE 2024 project parses."""
        assert isinstance(project, Project)


class TestAE2025:
    """Tests specific to After Effects 2025 (CC 25.x)."""

    @pytest.fixture
    def project(self) -> Project | None:
        """Load the AE 2025 sample project."""
        aep_path = VERSIONS_DIR / "ae2025" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("AE 2025 sample not available")
        return parse_project(aep_path)

    def test_parses_successfully(self, project: Project) -> None:
        """Test that AE 2025 project parses."""
        assert isinstance(project, Project)

    def test_has_main_composition(self, project: Project) -> None:
        """Test that Main_Composition exists."""
        comp_names = [c.name for c in project.compositions]
        assert "Main_Composition" in comp_names

    def test_main_comp_has_markers(self, project: Project) -> None:
        """Test that main composition has markers."""
        main_comp = project.composition("Main_Composition")
        assert main_comp is not None
        assert len(main_comp.markers) >= 1

    def test_has_folder_structure(self, project: Project) -> None:
        """Test that folder structure exists."""
        folder_names = [f.name for f in project.folders]
        assert "_Project Assets" in folder_names or "Compositions" in folder_names
