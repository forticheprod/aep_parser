"""Edge-case tests for 29.97fps / time_scale=3.125 compositions.

This file exercises the cdta binary parser with non-standard time-scale values
and sentinel out-point markers.  The sample file contains:

- Two 29.97 fps compositions (time_scale=3.125, divisor=23976)
- A short 24 fps precomp whose work-area covers the full duration (sentinel
  out_point_dividend = 0xFFFFFFFF)
- A 24 fps composition with non-zero display_start_time
- A 24 fps composition with a custom work-area range
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from conftest import parse_project

if TYPE_CHECKING:
    from aep_parser import Project
    from aep_parser.models.items.composition import CompItem

BUGS_DIR = Path(__file__).parent.parent / "samples" / "bugs"
AEP_PATH = BUGS_DIR / "29.97_fps_time_scale_3.125.aep"
JSON_PATH = BUGS_DIR / "29.97_fps_time_scale_3.125.json"


@pytest.fixture(scope="module")
def project() -> Project:
    """Parse the 29.97fps sample once for all tests in this module."""
    return parse_project(AEP_PATH)


@pytest.fixture(scope="module")
def expected() -> dict:
    """Load the expected JSON."""
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def _comp_by_id(project: Project, comp_id: int) -> CompItem:
    """Return the composition with the given id."""
    for comp in project.compositions:
        if comp.id == comp_id:
            return comp
    raise ValueError(f"Composition with id {comp_id} not found")


def _expected_comp(expected: dict, comp_id: int) -> dict:
    """Return the expected JSON block for the given item id."""
    for item in expected["items"]:
        if item.get("id") == comp_id and item.get("typeName") == "Composition":
            return item
    raise ValueError(f"Expected comp {comp_id} not found")


# -----------------------------------------------------------------------
#  29.97 fps / time_scale=3.125 compositions (id=155 and id=11516)
# -----------------------------------------------------------------------


class TestTimeScale3_125:
    """Tests for the 29.97fps compositions that use time_scale=3.125"""

    @pytest.mark.parametrize("comp_id", [155, 11516])
    def test_frame_rate(
        self, project: Project, expected: dict, comp_id: int
    ) -> None:
        comp = _comp_by_id(project, comp_id)
        exp = _expected_comp(expected, comp_id)
        assert math.isclose(comp.frame_rate, exp["frameRate"], rel_tol=1e-6)

    @pytest.mark.parametrize("comp_id", [155, 11516])
    def test_duration(
        self, project: Project, expected: dict, comp_id: int
    ) -> None:
        comp = _comp_by_id(project, comp_id)
        exp = _expected_comp(expected, comp_id)
        assert math.isclose(comp.duration, exp["duration"], rel_tol=1e-6)

    @pytest.mark.parametrize("comp_id", [155, 11516])
    def test_work_area_duration(
        self, project: Project, expected: dict, comp_id: int
    ) -> None:
        comp = _comp_by_id(project, comp_id)
        exp = _expected_comp(expected, comp_id)
        assert math.isclose(
            comp.work_area_duration, exp["workAreaDuration"], rel_tol=1e-6
        )

    @pytest.mark.parametrize("comp_id", [155, 11516])
    def test_work_area_start(
        self, project: Project, expected: dict, comp_id: int
    ) -> None:
        comp = _comp_by_id(project, comp_id)
        exp = _expected_comp(expected, comp_id)
        assert math.isclose(
            comp.work_area_start, exp["workAreaStart"], abs_tol=1e-9
        )

    @pytest.mark.parametrize("comp_id", [155, 11516])
    def test_frame_out_point(self, project: Project, comp_id: int) -> None:
        comp = _comp_by_id(project, comp_id)
        expected_frame = comp.out_point * comp.frame_rate
        assert math.isclose(comp.frame_out_point, expected_frame, abs_tol=1)


# -----------------------------------------------------------------------
#  Sentinel out_point (full work area) — id=281855
# -----------------------------------------------------------------------


class TestSentinelOutPoint:
    """Tests for the precomp where work area == full duration (sentinel)."""

    COMP_ID = 281855

    def test_work_area_equals_duration(
        self, project: Project, expected: dict
    ) -> None:
        """When out_point is sentinel, work_area_duration must equal duration."""
        comp = _comp_by_id(project, self.COMP_ID)
        exp = _expected_comp(expected, self.COMP_ID)
        assert math.isclose(
            comp.work_area_duration, exp["workAreaDuration"], rel_tol=1e-6
        )
        assert math.isclose(
            comp.work_area_duration, comp.duration, rel_tol=1e-9
        )

    def test_out_point_equals_duration(self, project: Project) -> None:
        """Sentinel out_point should resolve to display_start_time + duration."""
        comp = _comp_by_id(project, self.COMP_ID)
        assert math.isclose(
            comp.out_point,
            comp.display_start_time + comp.duration,
            rel_tol=1e-9,
        )

    def test_frame_out_point(self, project: Project) -> None:
        """Frame out_point should equal frame_duration for sentinel case."""
        comp = _comp_by_id(project, self.COMP_ID)
        assert comp.frame_out_point == comp.frame_duration

    def test_duration_short(self, project: Project, expected: dict) -> None:
        """This is a very short comp (0.75s = 18 frames at 24fps)."""
        comp = _comp_by_id(project, self.COMP_ID)
        exp = _expected_comp(expected, self.COMP_ID)
        assert math.isclose(comp.duration, exp["duration"], rel_tol=1e-6)
        assert comp.frame_duration == 18


# -----------------------------------------------------------------------
#  Non-zero display_start_time — id=12173, id=2767
# -----------------------------------------------------------------------


class TestNonZeroDisplayStartTime:
    """Tests for comps with display_start_time > 0 (start frame = 1)."""

    @pytest.mark.parametrize("comp_id", [12173, 2767])
    def test_display_start_frame(
        self, project: Project, comp_id: int
    ) -> None:
        comp = _comp_by_id(project, comp_id)
        assert comp.display_start_frame == 1

    @pytest.mark.parametrize("comp_id", [12173, 2767])
    def test_display_start_time(
        self, project: Project, expected: dict, comp_id: int
    ) -> None:
        comp = _comp_by_id(project, comp_id)
        exp = _expected_comp(expected, comp_id)
        assert math.isclose(
            comp.display_start_time, exp["displayStartTime"], rel_tol=1e-6
        )

    def test_work_area_with_offset(
        self, project: Project, expected: dict
    ) -> None:
        """Comp 2767 has a non-trivial work-area that starts mid-timeline."""
        comp = _comp_by_id(project, 2767)
        exp = _expected_comp(expected, 2767)
        assert math.isclose(
            comp.work_area_start, exp["workAreaStart"], rel_tol=1e-4
        )
        assert math.isclose(
            comp.work_area_duration, exp["workAreaDuration"], rel_tol=1e-4
        )
