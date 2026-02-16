"""Tests for RenderQueue model parsing."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import get_sample_files, load_expected, parse_project

from aep_parser import Project
from aep_parser.models.enums import OutputChannels, OutputColorDepth
from aep_parser.models.renderqueue import OutputModule, RenderQueue, RenderQueueItem
from aep_parser.models.renderqueue.output_module import resolve_output_filename

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "renderqueue"


@pytest.mark.parametrize("sample_name", get_sample_files(SAMPLES_DIR))
def test_parse_renderqueue_sample(sample_name: str) -> None:
    """Each renderqueue sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)
    assert isinstance(project.render_queue, RenderQueue)


class TestRenderQueueBasic:
    """Tests for basic render queue attributes."""

    def test_empty(self) -> None:
        expected = load_expected(SAMPLES_DIR, "empty")
        project = parse_project(SAMPLES_DIR / "empty.aep")
        assert len(project.render_queue.items) == 0
        assert expected["renderQueue"]["numItems"] == 0

    def test_numItems_1(self) -> None:
        expected = load_expected(SAMPLES_DIR, "numItems_1")
        project = parse_project(SAMPLES_DIR / "numItems_1.aep")
        assert expected["renderQueue"]["numItems"] == 1
        assert len(project.render_queue.items) == 1
        assert isinstance(project.render_queue.items[0], RenderQueueItem)

    def test_numItems_2(self) -> None:
        expected = load_expected(SAMPLES_DIR, "numItems_2")
        project = parse_project(SAMPLES_DIR / "numItems_2.aep")
        assert expected["renderQueue"]["numItems"] == 2
        assert len(project.render_queue.items) == 2


class TestOutputModule:
    """Tests for output module attributes."""

    def test_outputModule_file(self) -> None:
        _ = load_expected(SAMPLES_DIR, "outputModule_file")
        project = parse_project(SAMPLES_DIR / "outputModule_file.aep")
        rqi = project.render_queue.items[0]
        assert len(rqi.output_modules) >= 1
        om = rqi.output_modules[0]
        assert isinstance(om, OutputModule)
        assert om.file is not None

    def test_outputModule_template(self) -> None:
        _ = load_expected(SAMPLES_DIR, "outputModule_template")
        project = parse_project(SAMPLES_DIR / "outputModule_template.aep")
        rqi = project.render_queue.items[0]
        assert len(rqi.output_modules) >= 1
        om = rqi.output_modules[0]
        assert om.name is not None

    def test_numOutputModules_2(self) -> None:
        expected = load_expected(SAMPLES_DIR, "numOutputModules_2")
        project = parse_project(SAMPLES_DIR / "numOutputModules_2.aep")
        rqi = project.render_queue.items[0]
        exp_oms = expected["renderQueue"]["items"][0]["outputModules"]
        assert len(rqi.output_modules) == len(exp_oms) == 2

    def test_output_module_include_source_xmp_on(self) -> None:
        _ = load_expected(SAMPLES_DIR, "output_module_include_source_xmp_data_on")
        project = parse_project(SAMPLES_DIR / "output_module_include_source_xmp_data_on.aep")
        om = project.render_queue.items[0].output_modules[0]
        assert om.include_source_xmp is True

    def test_output_module_include_source_xmp_off(self) -> None:
        _ = load_expected(SAMPLES_DIR, "output_module_include_source_xmp_data_off")
        project = parse_project(SAMPLES_DIR / "output_module_include_source_xmp_data_off.aep")
        om = project.render_queue.items[0].output_modules[0]
        assert om.include_source_xmp is False

    def test_output_module_crop_checked(self) -> None:
        _ = load_expected(SAMPLES_DIR, "output_module_crop_checked")
        project = parse_project(SAMPLES_DIR / "output_module_crop_checked.aep")
        om = project.render_queue.items[0].output_modules[0]
        assert om.crop is True

    def test_output_module_crop_unchecked(self) -> None:
        _ = load_expected(SAMPLES_DIR, "output_module_crop_unchecked")
        project = parse_project(SAMPLES_DIR / "output_module_crop_unchecked.aep")
        om = project.render_queue.items[0].output_modules[0]
        assert om.crop is False


class TestCompLinking:
    """Tests for render queue item composition linking."""

    def test_comp_name_matches(self) -> None:
        expected = load_expected(SAMPLES_DIR, "base")
        project = parse_project(SAMPLES_DIR / "base.aep")
        rqi = project.render_queue.items[0]
        exp_rqi = expected["renderQueue"]["items"][0]
        assert rqi.comp_name == exp_rqi["compName"]

    def test_2_rqitems_comp_linking(self) -> None:
        expected = load_expected(SAMPLES_DIR, "2_rqitems")
        project = parse_project(SAMPLES_DIR / "2_rqitems.aep")
        assert len(project.render_queue.items) == 2
        for i, rqi in enumerate(project.render_queue.items):
            exp_name = expected["renderQueue"]["items"][i]["compName"]
            assert rqi.comp_name == exp_name


class TestRenderQueueItemAttributes:
    """Tests for render queue item attributes."""

    def test_render_unchecked(self) -> None:
        expected = load_expected(SAMPLES_DIR, "render_unchecked")
        project = parse_project(SAMPLES_DIR / "render_unchecked.aep")
        rqi = project.render_queue.items[0]
        exp_rqi = expected["renderQueue"]["items"][0]
        assert rqi.render is False
        assert exp_rqi["render"] is False

    def test_comment(self) -> None:
        project = parse_project(SAMPLES_DIR / "comment_aaaaa.aep")
        rqi = project.render_queue.items[0]
        assert rqi.comment == "aaaaa"

    def test_skip_frames_3(self) -> None:
        expected = load_expected(SAMPLES_DIR, "skip_frames_3")
        project = parse_project(SAMPLES_DIR / "skip_frames_3.aep")
        rqi = project.render_queue.items[0]
        exp_rqi = expected["renderQueue"]["items"][0]
        assert rqi.skip_frames == exp_rqi["skipFrames"] == 3


class TestResolveOutputFilename:
    """Unit tests for resolve_output_filename()."""

    def test_none_template(self) -> None:
        assert resolve_output_filename(None) is None

    def test_project_name(self) -> None:
        result = resolve_output_filename("[projectName]", project_name="MyProject")
        assert result == "MyProject"

    def test_comp_name(self) -> None:
        result = resolve_output_filename("[compName]", comp_name="Comp 1")
        assert result == "Comp 1"

    def test_render_settings_name(self) -> None:
        result = resolve_output_filename("[renderSettingsName]", render_settings_name="Best Settings")
        assert result == "Best Settings"

    def test_output_module_name(self) -> None:
        result = resolve_output_filename("[outputModuleName]", output_module_name="Lossless")
        assert result == "Lossless"

    def test_width(self) -> None:
        result = resolve_output_filename("[width]", width=1920)
        assert result == "1920"

    def test_height(self) -> None:
        result = resolve_output_filename("[height]", height=1080)
        assert result == "1080"

    def test_frame_rate_integer(self) -> None:
        result = resolve_output_filename("[frameRate]", frame_rate=30.0)
        assert result == "30"

    def test_frame_rate_float(self) -> None:
        result = resolve_output_filename("[frameRate]", frame_rate=29.97)
        assert result == "29.97"

    def test_aspect_ratio(self) -> None:
        result = resolve_output_filename("[aspectRatio]", width=1920, height=1080)
        assert result == "16x9"

    def test_channels_rgb(self) -> None:
        result = resolve_output_filename("[channels]", channels=OutputChannels.RGB)
        assert result == "RGB"

    def test_channels_rgba(self) -> None:
        result = resolve_output_filename("[channels]", channels=OutputChannels.RGBA)
        assert result == "RGBA"

    def test_channels_alpha(self) -> None:
        result = resolve_output_filename("[channels]", channels=OutputChannels.ALPHA)
        assert result == "Alpha"

    def test_project_color_depth_8bit(self) -> None:
        result = resolve_output_filename("[projectColorDepth]", project_color_depth=8)
        assert result == "8bit"

    def test_project_color_depth_16bit(self) -> None:
        result = resolve_output_filename("[projectColorDepth]", project_color_depth=16)
        assert result == "16bit"

    def test_project_color_depth_32bit(self) -> None:
        result = resolve_output_filename("[projectColorDepth]", project_color_depth=32)
        assert result == "32bit"

    def test_output_color_depth_millions(self) -> None:
        result = resolve_output_filename("[outputColorDepth]", output_color_depth=OutputColorDepth.MILLIONS_OF_COLORS)
        assert result == "Millions"

    def test_output_color_depth_trillions(self) -> None:
        result = resolve_output_filename("[outputColorDepth]", output_color_depth=OutputColorDepth.TRILLIONS_OF_COLORS)
        assert result == "Trillions"

    def test_output_color_depth_float(self) -> None:
        result = resolve_output_filename("[outputColorDepth]", output_color_depth=OutputColorDepth.FLOATING_POINT)
        assert result == "Float"

    def test_file_extension(self) -> None:
        result = resolve_output_filename("[compName].[fileExtension]", comp_name="MyComp", file_extension="mp4")
        assert result == "MyComp.mp4"

    def test_compressor(self) -> None:
        result = resolve_output_filename("[compressor]", compressor="H.264")
        assert result == "H.264"

    def test_combined_template(self) -> None:
        result = resolve_output_filename(
            "[projectName]_[compName]_[width]x[height].[fileExtension]",
            project_name="Proj",
            comp_name="Comp1",
            width=1920,
            height=1080,
            file_extension="mov",
        )
        assert result == "Proj_Comp1_1920x1080.mov"

    def test_case_insensitive(self) -> None:
        result = resolve_output_filename("[COMPNAME]", comp_name="MyComp")
        assert result == "MyComp"

    def test_start_timecode(self) -> None:
        result = resolve_output_filename("[startTimecode]", start_time=0.0, frame_rate=24.0)
        assert result == "0-00-00-00"

    def test_end_timecode(self) -> None:
        result = resolve_output_filename("[endTimecode]", end_time=10.0, frame_rate=24.0)
        assert result == "0-00-10-00"

    def test_duration_timecode(self) -> None:
        result = resolve_output_filename("[durationTimecode]", duration_time=5.0, frame_rate=24.0)
        assert result == "0-00-05-00"

    def test_project_folder_empty(self) -> None:
        result = resolve_output_filename("[projectFolder][compName]", comp_name="MyComp")
        assert result == "MyComp"
