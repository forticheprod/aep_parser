"""Tests for RenderQueue model parsing."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import get_sample_files, load_expected, parse_project

from aep_parser import Project
from aep_parser.models.enums import OutputChannels, OutputColorDepth
from aep_parser.models.renderqueue import OutputModule, RenderQueue
from aep_parser.resolvers.output import resolve_output_filename

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "renderqueue"
OM_SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "output_module"


@pytest.mark.parametrize("sample_name", get_sample_files(SAMPLES_DIR))
def test_parse_renderqueue_sample(sample_name: str) -> None:
    """Each renderqueue sample can be parsed without error."""
    aep_path = SAMPLES_DIR / f"{sample_name}.aep"
    project = parse_project(aep_path)
    assert isinstance(project, Project)
    assert isinstance(project.render_queue, RenderQueue)


class TestRenderQueueBasic:
    """Tests for basic render queue attributes."""

    @pytest.mark.parametrize(
        "sample_name, expected_count",
        [
            ("empty", 0),
            ("numItems_1", 1),
            ("numItems_2", 2),
        ],
    )
    def test_num_items(self, sample_name: str, expected_count: int) -> None:
        expected = load_expected(SAMPLES_DIR, sample_name)
        project = parse_project(SAMPLES_DIR / f"{sample_name}.aep")
        assert expected["renderQueue"]["numItems"] == expected_count
        assert len(project.render_queue.items) == expected_count


class TestOutputModule:
    """Tests for output module attributes."""

    def test_outputModule_file(self) -> None:
        _ = load_expected(OM_SAMPLES_DIR, "file")
        project = parse_project(OM_SAMPLES_DIR / "file.aep")
        rqi = project.render_queue.items[0]
        assert len(rqi.output_modules) >= 1
        om = rqi.output_modules[0]
        assert isinstance(om, OutputModule)
        assert om.file is not None

    def test_outputModule_template(self) -> None:
        _ = load_expected(OM_SAMPLES_DIR, "template")
        project = parse_project(OM_SAMPLES_DIR / "template.aep")
        rqi = project.render_queue.items[0]
        assert len(rqi.output_modules) >= 1
        om = rqi.output_modules[0]
        assert om.name is not None

    def test_numOutputModules_2(self) -> None:
        expected = load_expected(OM_SAMPLES_DIR, "numOutputModules_2")
        project = parse_project(OM_SAMPLES_DIR / "numOutputModules_2.aep")
        rqi = project.render_queue.items[0]
        exp_oms = expected["renderQueue"]["items"][0]["outputModules"]
        assert len(rqi.output_modules) == len(exp_oms) == 2

    @pytest.mark.parametrize(
        "sample_name, expected_value",
        [
            ("include_source_xmp_data_on", True),
            ("include_source_xmp_data_off", False),
        ],
    )
    def test_include_source_xmp(
        self, sample_name: str, expected_value: bool
    ) -> None:
        project = parse_project(OM_SAMPLES_DIR / f"{sample_name}.aep")
        om = project.render_queue.items[0].output_modules[0]
        assert om.include_source_xmp is expected_value

    @pytest.mark.parametrize(
        "sample_name, expected_value",
        [
            ("crop_checked", True),
            ("crop_unchecked", False),
        ],
    )
    def test_crop(self, sample_name: str, expected_value: bool) -> None:
        project = parse_project(OM_SAMPLES_DIR / f"{sample_name}.aep")
        om = project.render_queue.items[0].output_modules[0]
        assert om.settings["Crop"] is expected_value


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


class TestSkipFrames:
    """Tests for skip_frames calculation from frame rate ratio."""

    @pytest.mark.skip(
        reason="FIXME: Could not find parameter in UI and jsx generate"
        " script does not set this properly"
    )
    @pytest.mark.parametrize("n", [0, 1, 2, 3])
    def test_skip_frames(self, n: int) -> None:
        sample_name = f"skip_frames_{n}"
        expected = load_expected(SAMPLES_DIR, sample_name)
        project = parse_project(SAMPLES_DIR / f"{sample_name}.aep")
        rqi = project.render_queue.items[0]
        exp_rqi = expected["renderQueue"]["items"][0]
        assert rqi.skip_frames == exp_rqi["skipFrames"] == n


class TestOutputModuleSettings:
    """Tests for output module settings values."""

    @pytest.mark.parametrize(
        "sample_name, expected_value",
        [
            ("starting_0", 0),
            ("starting_101", 101),
            ("starting_9999999", 9999999),
        ],
    )
    def test_starting_number(
        self, sample_name: str, expected_value: int
    ) -> None:
        expected = load_expected(SAMPLES_DIR, sample_name)
        project = parse_project(SAMPLES_DIR / f"{sample_name}.aep")
        om = project.render_queue.items[0].output_modules[0]
        exp_om = expected["renderQueue"]["items"][0]["outputModules"][0]
        assert om.settings["Starting #"] == exp_om["settings"]["Starting #"]
        assert om.settings["Starting #"] == expected_value

    @pytest.mark.parametrize(
        "sample_name, expected_value",
        [
            ("use_comp_frame_number_off", False),
            ("use_comp_frame_number_on", True),
        ],
    )
    def test_use_comp_frame_number(
        self, sample_name: str, expected_value: bool
    ) -> None:
        expected = load_expected(SAMPLES_DIR, sample_name)
        project = parse_project(SAMPLES_DIR / f"{sample_name}.aep")
        om = project.render_queue.items[0].output_modules[0]
        exp_om = expected["renderQueue"]["items"][0]["outputModules"][0]
        assert om.settings["Use Comp Frame Number"] is expected_value
        assert exp_om["settings"]["Use Comp Frame Number"] is expected_value


class TestResolveOutputFilename:
    """Unit tests for resolve_output_filename()."""

    def test_empty_template(self) -> str:
        assert resolve_output_filename("") == ""

    @pytest.mark.parametrize(
        "template, kwargs, expected",
        [
            ("[projectName]", {"project_name": "MyProject"}, "MyProject"),
            ("[compName]", {"comp_name": "Comp 1"}, "Comp 1"),
            ("[renderSettingsName]", {"render_settings_name": "Best Settings"}, "Best Settings"),
            ("[outputModuleName]", {"output_module_name": "Lossless"}, "Lossless"),
            ("[width]", {"width": 1920}, "1920"),
            ("[height]", {"height": 1080}, "1080"),
            ("[frameRate]", {"frame_rate": 30.0}, "30"),
            ("[frameRate]", {"frame_rate": 29.97}, "29.97"),
            ("[compressor]", {"compressor": "H.264"}, "H.264"),
            ("[COMPNAME]", {"comp_name": "MyComp"}, "MyComp"),
        ],
    )
    def test_single_token(
        self, template: str, kwargs: dict[str, object], expected: str
    ) -> None:
        assert resolve_output_filename(template, **kwargs) == expected

    def test_aspect_ratio(self) -> None:
        result = resolve_output_filename("[aspectRatio]", width=1920, height=1080)
        assert result == "16x9"

    @pytest.mark.parametrize(
        "channels, expected",
        [
            (OutputChannels.RGB, "RGB"),
            (OutputChannels.RGBA, "RGBA"),
            (OutputChannels.ALPHA, "Alpha"),
        ],
    )
    def test_channels(
        self, channels: OutputChannels, expected: str
    ) -> None:
        assert resolve_output_filename("[channels]", channels=channels) == expected

    @pytest.mark.parametrize(
        "depth, expected",
        [
            (8, "8bit"),
            (16, "16bit"),
            (32, "32bit"),
        ],
    )
    def test_project_color_depth(self, depth: int, expected: str) -> None:
        assert resolve_output_filename("[projectColorDepth]", project_color_depth=depth) == expected

    @pytest.mark.parametrize(
        "color_depth, expected",
        [
            (OutputColorDepth.MILLIONS_OF_COLORS, "Millions"),
            (OutputColorDepth.MILLIONS_OF_COLORS_PLUS, "Millions+"),
            (OutputColorDepth.TRILLIONS_OF_COLORS, "Trillions"),
            (OutputColorDepth.TRILLIONS_OF_COLORS_PLUS, "Trillions+"),
            (OutputColorDepth.FLOATING_POINT, "Floating Point"),
            (OutputColorDepth.FLOATING_POINT_PLUS, "Floating Point+"),
        ],
    )
    def test_output_color_depth(
        self, color_depth: OutputColorDepth, expected: str
    ) -> None:
        assert resolve_output_filename("[outputColorDepth]", output_color_depth=color_depth) == expected

    def test_file_extension(self) -> None:
        result = resolve_output_filename("[compName].[fileExtension]", comp_name="MyComp", file_extension="mp4")
        assert result == "MyComp.mp4"

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

    @pytest.mark.parametrize(
        "template, kwargs, expected",
        [
            ("[startTimecode]", {"start_time": 0.0, "frame_rate": 24.0}, "0-00-00-00"),
            ("[endTimecode]", {"end_time": 10.0, "frame_rate": 24.0}, "0-00-10-00"),
            ("[durationTimecode]", {"duration_time": 5.0, "frame_rate": 24.0}, "0-00-05-00"),
        ],
    )
    def test_timecode(
        self, template: str, kwargs: dict[str, object], expected: str
    ) -> None:
        assert resolve_output_filename(template, **kwargs) == expected

    def test_project_folder_empty(self) -> None:
        result = resolve_output_filename("[projectFolder][compName]", comp_name="MyComp")
        assert result == "MyComp"
