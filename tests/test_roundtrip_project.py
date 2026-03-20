"""Roundtrip tests: parse -> modify -> save -> parse -> verify for Project fields."""

from __future__ import annotations

from pathlib import Path

from aep_parser import parse as parse_aep

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "project"


# ---- linear_blending ----


class TestRoundtripLinearBlending:
    """Roundtrip tests for Project.linear_blending."""

    def test_enable_linear_blending(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "linearBlending_false.aep").project
        assert project.linear_blending is False

        project.linear_blending = True

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.linear_blending is True

    def test_disable_linear_blending(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "linearBlending_true.aep").project
        assert project.linear_blending is True

        project.linear_blending = False

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.linear_blending is False

    def test_set_same_value_is_noop(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "linearBlending_true.aep").project
        assert project.linear_blending is True

        project.linear_blending = True  # no change

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.linear_blending is True


# ---- linearize_working_space ----


class TestRoundtripLinearizeWorkingSpace:
    """Roundtrip tests for Project.linearize_working_space."""

    def test_enable_linearize_working_space(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "linearizeWorkingSpace_false.aep"
        ).project
        assert project.linearize_working_space is False

        project.linearize_working_space = True

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.linearize_working_space is True

    def test_disable_linearize_working_space(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "linearizeWorkingSpace_true.aep"
        ).project
        assert project.linearize_working_space is True

        project.linearize_working_space = False

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.linearize_working_space is False

    def test_set_same_value_is_noop(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "linearizeWorkingSpace_false.aep"
        ).project
        assert project.linearize_working_space is False

        project.linearize_working_space = False  # no change

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.linearize_working_space is False
