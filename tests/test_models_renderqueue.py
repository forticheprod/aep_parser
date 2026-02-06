"""Tests for RenderQueue, RenderQueueItem, and OutputModule model parsing.

These tests verify that aep_parser correctly parses render queue data
from AEP files.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aep_parser import Project, parse_project
from aep_parser.models.renderqueue import (
    OutputModule,
    RenderQueue,
    RenderQueueItem,
)
from aep_parser.models.renderqueue.output_module import (
    get_extension_for_template,
    resolve_output_filename,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "renderqueue"


def get_sample_files() -> list[str]:
    """Get all .aep files in the renderqueue samples directory."""
    if not SAMPLES_DIR.exists():
        return []
    return [f.stem for f in SAMPLES_DIR.glob("*.aep")]


def load_expected(sample_name: str) -> dict:
    """Load the expected JSON for a sample."""
    json_path = SAMPLES_DIR / f"{sample_name}.json"
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("sample_name", get_sample_files())
def test_parse_renderqueue_sample(sample_name: str) -> None:
    """Test that each render queue sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)
    assert isinstance(project.render_queue, RenderQueue)


class TestRenderQueueBasic:
    """Tests for basic RenderQueue attributes."""

    def test_empty_renderqueue(self) -> None:
        """Test project with empty render queue."""
        expected = load_expected("empty")
        project = parse_project(SAMPLES_DIR / "empty.aep")

        rq_json = expected.get("renderQueue", {})
        assert rq_json["numItems"] == 0
        assert len(project.render_queue.items) == rq_json["numItems"]

    def test_numItems_1(self) -> None:
        """Test render queue with one item."""
        expected = load_expected("numItems_1")
        project = parse_project(SAMPLES_DIR / "numItems_1.aep")

        rq_json = expected.get("renderQueue", {})
        assert rq_json["numItems"] == 1
        assert len(project.render_queue.items) == rq_json["numItems"]
        assert isinstance(project.render_queue.items[0], RenderQueueItem)

        # Compare first item
        expected_item = rq_json["items"][0]
        rq_item = project.render_queue.items[0]
        assert len(rq_item.output_modules) == expected_item["numOutputModules"]

        # Compare first output module
        expected_om = expected_item["outputModules"][0]
        om = rq_item.output_modules[0]
        assert om.name == expected_om["name"]
        assert om.file == expected_om["file"]

    def test_numItems_2(self) -> None:
        """Test render queue with multiple items."""
        expected = load_expected("numItems_2")
        project = parse_project(SAMPLES_DIR / "numItems_2.aep")

        rq_json = expected.get("renderQueue", {})
        assert len(project.render_queue.items) == rq_json["numItems"]
        assert rq_json["numItems"] == 2

        # Compare each item
        for i, expected_item in enumerate(rq_json["items"]):
            rq_item = project.render_queue.items[i]
            assert len(rq_item.output_modules) == expected_item["numOutputModules"]

            # Compare output modules
            for j, expected_om in enumerate(expected_item["outputModules"]):
                om = rq_item.output_modules[j]
                assert om.name == expected_om["name"]
                # Note: om.file contains the template pattern, not resolved filename
                assert om.file == ected_om["file"]


class TestOutputModule:
    """Tests for OutputModule attributes."""

    def test_outputModule_file(self) -> None:
        """Test output module with file path."""
        expected = load_expected("outputModule_file")
        project = parse_project(SAMPLES_DIR / "outputModule_file.aep")

        rq_json = expected.get("renderQueue", {})
        assert len(project.render_queue.items) == rq_json["numItems"]

        rq_item = project.render_queue.items[0]
        expected_item = rq_json["items"][0]
        assert len(rq_item.output_modules) == expected_item["numOutputModules"]

        om = rq_item.output_modules[0]
        expected_om = expected_item["outputModules"][0]

        assert isinstance(om, OutputModule)
        assert om.file == expected_om["file"]
        assert om.name == expected_om["name"]
        assert "test_output" in om.file.lower()

    def test_outputModule_template(self) -> None:
        """Test output module with template."""
        project = parse_project(SAMPLES_DIR / "outputModule_template.aep")

        rq_json = expected.get("renderQueue", {})
        assert len(project.render_queue.items) == rq_json["numItems"]

        rq_item = project.render_queue.items[0]
        expected_item = rq_json["items"][0]
        assert len(rq_item.output_modules) == expected_item["numOutputModules"]

        om = rq_item.output_modules[0]
        expected_om = expected_item["outputModules"][0]

        assert isinstance(om, OutputModule)
        assert om.file == expected_om["file"]
        assert om.name == expected_om["name"]
        assert om.name == "Lossless"

    def test_multiple_output_modules(self) -> None:
        """Test render queue item with multiple output modules."""
        expected = load_expected("numOutputModules_2")
        project = parse_project(SAMPLES_DIR / "numOutputModules_2.aep")

        rq_json = expected.get("renderQueue", {})
        assert len(project.render_queue.items) == rq_json["numItems"]

        rq_item = project.render_queue.items[0]
        expected_item = rq_json["items"][0]
        assert len(rq_item.output_modules) == expected_item["numOutputModules"]

        # Compare each output module
        for i, expected_om in enumerate(expected_item["outputModules"]):
            om = rq_item.output_modules[i]
            assert om.file is not None
            assert om.name == expected_om["name"]


class TestRenderQueueItemCompLinking:
    """Tests for RenderQueueItem comp linking.

    Note: The binary format stores render queue items without explicit comp_id.
    Linking must be done by matching comp names or other heuristics.
    """

    def test_rqitem_has_comp_id_attribute(self) -> None:
        """Test that render queue item has comp_id attribute."""
        project = parse_project(SAMPLES_DIR / "numItems_1.aep")
        rq_item = project.render_queue.items[0]

        # comp_id is an attribute but may be None if not parsed from binary
        assert hasattr(rq_item, "comp_id")
        assert hasattr(rq_item, "comp")

    def test_rqitem_comp_linking_by_name(self) -> None:
        """Test that comp can be found by name from file path."""
        expected = load_expected("numItems_1")
        project = parse_project(SAMPLES_DIR / "numItems_1.aep")

        rq_item = project.render_queue.items[0]
        expected_comp_name = expected["renderQueue"]["items"][0]["compName"]

        # Find comp by name from the project
        comp = next(
            (c for c in project.compositions if c.name == expected_comp_name),
            None,
        )
        assert comp is not None
        assert comp.name == "TestComp"
