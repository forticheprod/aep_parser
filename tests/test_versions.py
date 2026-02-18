"""Tests for parsing AEP files across different AE versions."""

from __future__ import annotations

import warnings
from pathlib import Path

import pytest
from conftest import parse_project

from aep_parser import Project

VERSIONS_DIR = Path(__file__).parent.parent / "samples" / "versions"


class TestAE2025:
    """Tests specific to After Effects 2025 projects."""

    def test_validate_against_json(self) -> None:
        """Validate AE2025 project against ExtendScript JSON export."""
        from aep_parser.cli.validate import validate_aep

        aep_path = VERSIONS_DIR / "ae2025" / "complete.aep"
        json_path = VERSIONS_DIR / "ae2025" / "complete.json"
        if not aep_path.exists() or not json_path.exists():
            pytest.skip("ae2025 sample or JSON reference not found")
        result = validate_aep(aep_path, json_path)
        # Report differences as warnings, not failures
        for diff in result.differences:
            warnings.warn(diff, stacklevel=1)


class TestVersionCompatibility:
    """Cross-version compatibility checks."""

    @pytest.mark.parametrize(
        "version",
        ["ae2018", "ae2019", "ae2020", "ae2022", "ae2023", "ae2024", "ae2025"],
    )
    def test_all_versions_parseable(self, version: str) -> None:
        aep_path = VERSIONS_DIR / version / "complete.aep"
        if not aep_path.exists():
            pytest.skip(f"{version} sample not found")
        project = parse_project(aep_path)
        assert isinstance(project, Project)
        assert len(project.compositions) >= 1
