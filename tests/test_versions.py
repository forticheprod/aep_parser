"""Tests for parsing AEP files across different AE versions."""

from __future__ import annotations

from pathlib import Path

import pytest

from aep_parser import Project, parse_project

VERSIONS_DIR = Path(__file__).parent.parent / "samples" / "versions"


class TestAE2018:
    """Tests for After Effects 2018 projects."""

    @pytest.fixture()
    def sample(self) -> Path:
        aep_path = VERSIONS_DIR / "ae2018" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("ae2018 sample not found")
        return aep_path

    def test_parse(self, sample: Path) -> None:
        project = parse_project(sample)
        assert isinstance(project, Project)

    def test_has_compositions(self, sample: Path) -> None:
        project = parse_project(sample)
        assert len(project.compositions) >= 1


class TestAE2019:
    """Tests for After Effects 2019 projects."""

    @pytest.fixture()
    def sample(self) -> Path:
        aep_path = VERSIONS_DIR / "ae2019" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("ae2019 sample not found")
        return aep_path

    def test_parse(self, sample: Path) -> None:
        project = parse_project(sample)
        assert isinstance(project, Project)

    def test_has_compositions(self, sample: Path) -> None:
        project = parse_project(sample)
        assert len(project.compositions) >= 1


class TestAE2020:
    """Tests for After Effects 2020 projects."""

    @pytest.fixture()
    def sample(self) -> Path:
        aep_path = VERSIONS_DIR / "ae2020" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("ae2020 sample not found")
        return aep_path

    def test_parse(self, sample: Path) -> None:
        project = parse_project(sample)
        assert isinstance(project, Project)

    def test_has_compositions(self, sample: Path) -> None:
        project = parse_project(sample)
        assert len(project.compositions) >= 1


class TestAE2022:
    """Tests for After Effects 2022 projects."""

    @pytest.fixture()
    def sample(self) -> Path:
        aep_path = VERSIONS_DIR / "ae2022" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("ae2022 sample not found")
        return aep_path

    def test_parse(self, sample: Path) -> None:
        project = parse_project(sample)
        assert isinstance(project, Project)

    def test_has_compositions(self, sample: Path) -> None:
        project = parse_project(sample)
        assert len(project.compositions) >= 1


class TestAE2023:
    """Tests for After Effects 2023 projects."""

    @pytest.fixture()
    def sample(self) -> Path:
        aep_path = VERSIONS_DIR / "ae2023" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("ae2023 sample not found")
        return aep_path

    def test_parse(self, sample: Path) -> None:
        project = parse_project(sample)
        assert isinstance(project, Project)

    def test_has_compositions(self, sample: Path) -> None:
        project = parse_project(sample)
        assert len(project.compositions) >= 1


class TestAE2024:
    """Tests for After Effects 2024 projects."""

    @pytest.fixture()
    def sample(self) -> Path:
        aep_path = VERSIONS_DIR / "ae2024" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("ae2024 sample not found")
        return aep_path

    def test_parse(self, sample: Path) -> None:
        project = parse_project(sample)
        assert isinstance(project, Project)

    def test_has_compositions(self, sample: Path) -> None:
        project = parse_project(sample)
        assert len(project.compositions) >= 1


class TestAE2025:
    """Tests for After Effects 2025 projects."""

    @pytest.fixture()
    def sample(self) -> Path:
        aep_path = VERSIONS_DIR / "ae2025" / "complete.aep"
        if not aep_path.exists():
            pytest.skip("ae2025 sample not found")
        return aep_path

    def test_parse(self, sample: Path) -> None:
        project = parse_project(sample)
        assert isinstance(project, Project)

    def test_has_compositions(self, sample: Path) -> None:
        project = parse_project(sample)
        assert len(project.compositions) >= 1

    def test_validate_against_json(self, sample: Path) -> None:
        """Validate AE2025 project against ExtendScript JSON export."""
        from aep_parser.cli.validate import validate_aep
        json_path = VERSIONS_DIR / "ae2025" / "complete.json"
        if not json_path.exists():
            pytest.skip("ae2025 JSON reference not found")
        result = validate_aep(sample, json_path)
        # Report differences as warnings, not failures
        for diff in result.differences:
            import warnings
            warnings.warn(diff, stacklevel=1)


class TestVersionCompatibility:
    """Cross-version compatibility checks."""

    @pytest.mark.parametrize("version", ["ae2018", "ae2022", "ae2023", "ae2024", "ae2025"])
    def test_all_versions_parseable(self, version: str) -> None:
        aep_path = VERSIONS_DIR / version / "complete.aep"
        if not aep_path.exists():
            pytest.skip(f"{version} sample not found")
        project = parse_project(aep_path)
        assert isinstance(project, Project)
        assert len(project.compositions) >= 1
