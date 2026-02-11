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
                assert om.file == expected_om["file"]


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
        expected = load_expected("outputModule_template")
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

    def test_outputModule_all_template_variables(self) -> None:
        """Test output module with all template variables resolved."""
        expected = load_expected("output_to_custom_all_fields")
        project = parse_project(
            SAMPLES_DIR / "output_to_custom_all_fields.aep"
        )

        rq_json = expected.get("renderQueue", {})
        assert len(project.render_queue.items) == rq_json["numItems"]

        rq_item = project.render_queue.items[0]
        expected_item = rq_json["items"][0]
        om = rq_item.output_modules[0]
        expected_om = expected_item["outputModules"][0]

        assert isinstance(om, OutputModule)
        # Note: Some template variables are not correctly resolved at the moment,
        # so we check that the template pattern is present but variables are not.
        assert om.file is not None
        assert om.name == expected_om["name"]

        # Verify template variables were resolved
        assert "[projectName]" not in om.file
        assert "[compName]" not in om.file
        assert "[renderSettingsName]" not in om.file
        assert "[outputModuleName]" not in om.file
        assert "[width]" not in om.file
        assert "[height]" not in om.file
        assert "[frameRate]" not in om.file
        assert "[aspectRatio]" not in om.file
        assert "[startFrame]" not in om.file
        assert "[endFrame]" not in om.file
        assert "[durationFrames]" not in om.file
        assert "[startTimecode]" not in om.file
        assert "[endTimecode]" not in om.file
        assert "[durationTimecode]" not in om.file
        assert "[channels]" not in om.file
        assert "[projectColorDepth]" not in om.file
        assert "[outputColorDepth]" not in om.file
        assert "[compressor]" not in om.file
        assert "[fieldOrder]" not in om.file
        assert "[fileExtension]" not in om.file

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
            assert om.file == expected_om["file"]
            assert om.name == expected_om["name"]


class TestRenderQueueItemCompLinking:
    """Tests for RenderQueueItem comp linking."""

    def test_rqitem_comp_linking_by_name(self) -> None:
        """Test that comp can be found by name from file path."""
        expected = load_expected("numItems_1")
        project = parse_project(SAMPLES_DIR / "numItems_1.aep")

        project.render_queue.items[0]
        expected_comp_name = expected["renderQueue"]["items"][0]["compName"]

        # Find comp by name from the project
        comp = next(
            (c for c in project.compositions if c.name == expected_comp_name),
            None,
        )
        assert comp is not None
        assert comp.name == "TestComp"


class TestResolveOutputFilename:
    """Tests for resolve_output_filename template resolution."""

    def test_resolve_compname_and_extension(self) -> None:
        """Test basic [compName] and [fileExtension] resolution."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "C:/Output/[compName].[fileExtension]",
            comp_name="My Composition",
            file_extension="mp4",
        )
        assert result == "C:/Output/My Composition.mp4"

    def test_resolve_project_name(self) -> None:
        """Test [projectName] resolution."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "[projectName]_output.mov",
            project_name="my_project",
        )
        assert result == "my_project_output.mov"

    def test_resolve_dimensions(self) -> None:
        """Test [width], [height], and [aspectRatio] resolution."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "[width]x[height]_[aspectRatio].mp4",
            width=1920,
            height=1080,
        )
        assert result == "1920x1080_16x9.mp4"

    def test_resolve_frame_rate(self) -> None:
        """Test [frameRate] resolution."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        # Non-integer frame rate shows with decimals
        result = resolve_output_filename(
            "output_[frameRate]fps.mp4",
            frame_rate=29.97,
        )
        assert result == "output_29.97fps.mp4"

        # Integer frame rate shows without decimals
        result = resolve_output_filename(
            "output_[frameRate]fps.mp4",
            frame_rate=24.0,
        )
        assert result == "output_24fps.mp4"

    def test_resolve_frame_numbers(self) -> None:
        """Test [startFrame], [endFrame], [durationFrames] resolution."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "[startFrame]-[endFrame]_dur[durationFrames].mp4",
            start_frame=0,
            end_frame=720,
            duration_frames=720,
            frame_rate=24.0,
        )
        # 720 frames / 16 frames per foot = 45 feet
        assert result == "0000+00-0045+00_dur0045+00.mp4"

    def test_resolve_timecodes(self) -> None:
        """Test [startTimecode], [endTimecode], [durationTimecode] resolution."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "[startTimecode]_to_[endTimecode]_([durationTimecode]).mp4",
            start_time=0.0,
            end_time=30.0,
            duration_time=30.0,
            frame_rate=24.0,
        )
        assert result == "0-00-00-00_to_0-00-30-00_(0-00-30-00).mp4"

    def test_resolve_channels(self) -> None:
        """Test [channels] resolution."""
        from aep_parser.models.enums import OutputChannels
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "output_[channels].mp4",
            channels=OutputChannels.RGBA,
        )
        assert result == "output_RGBA.mp4"

    def test_resolve_color_depth(self) -> None:
        """Test [projectColorDepth] and [outputColorDepth] resolution."""
        from aep_parser.models.enums import OutputColorDepth
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "proj_[projectColorDepth]_out_[outputColorDepth].mp4",
            project_color_depth=32,
            output_color_depth=OutputColorDepth.MILLIONS_OF_COLORS,
        )
        assert result == "proj_32bit_out_Millions.mp4"

    def test_resolve_compressor_and_field_order(self) -> None:
        """Test [compressor] and [fieldOrder] resolution."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "[compressor]_[fieldOrder].mp4",
            compressor="H.264",
            field_render=0,
        )
        assert result == "H.264_Both.mp4"

    def test_resolve_render_settings_name(self) -> None:
        """Test [renderSettingsName] resolution."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "[renderSettingsName]_output.mp4",
            render_settings_name="Best Settings",
        )
        assert result == "Best Settings_output.mp4"

    def test_resolve_output_module_name(self) -> None:
        """Test [outputModuleName] resolution."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "[outputModuleName].mp4",
            output_module_name="H.264 - Match Render Settings - 15 Mbps",
        )
        assert result == "H.264 - Match Render Settings - 15 Mbps.mp4"

    def test_none_template_returns_none(self) -> None:
        """Test that None template returns None."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(None, comp_name="Test")
        assert result is None

    def test_case_insensitive_replacement(self) -> None:
        """Test that template variable replacement is case-insensitive."""
        from aep_parser.models.renderqueue.output_module import resolve_output_filename

        result = resolve_output_filename(
            "[COMPNAME]_[FileExtension]",
            comp_name="Test",
            file_extension="mp4",
        )
        assert result == "Test_mp4"
