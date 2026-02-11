"""Tests for prefs_indep_output parser."""

from pathlib import Path

import pytest

from aep_parser.parsers.prefs_indep_output import (
    ExporterParam,
    OutputFileInfo,
    OutputFileOptions,
    OutputModulePreferences,
    OutputModuleTemplate,
    Settings,
    parse_prefs_indep_output,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples"


class TestPrefsIndepOutputParser:
    """Tests for parsing prefs_indep_output.txt files."""

    @pytest.fixture
    def sample_prefs_path(self) -> Path:
        """Return path to the sample prefs file."""
        return SAMPLES_DIR / "assets" / "prefs_indep_output.txt"

    def test_parse_returns_settings(self, sample_prefs_path: Path) -> None:
        """Parser returns a Settings object."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        assert isinstance(settings, Settings)

    def test_parse_extracts_version(self, sample_prefs_path: Path) -> None:
        """Parser extracts the file version."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        assert settings.version == "1.1"

    def test_parse_extracts_templates(self, sample_prefs_path: Path) -> None:
        """Parser extracts output module templates."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        assert len(settings.output_module_templates) > 0

        # Check that templates have names
        for template in settings.output_module_templates:
            assert isinstance(template, OutputModuleTemplate)
            assert template.name

    def test_parse_common_templates(self, sample_prefs_path: Path) -> None:
        """Parser extracts common template names."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        template_names = [t.name for t in settings.output_module_templates]

        # Check for common templates
        assert "Lossless" in template_names
        assert "Lossless with Alpha" in template_names
        assert "Photoshop" in template_names

    def test_parse_extracts_file_info(self, sample_prefs_path: Path) -> None:
        """Parser extracts output file info entries."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        assert len(settings.output_file_info) > 0

        for info_id, info in settings.output_file_info.items():
            assert isinstance(info, OutputFileInfo)
            assert info.id == info_id

    def test_parse_extracts_format_codes(self, sample_prefs_path: Path) -> None:
        """Parser extracts format codes from file info."""
        settings = parse_prefs_indep_output(sample_prefs_path)

        # Check that some format codes are extracted
        format_codes = [
            info.format_code
            for info in settings.output_file_info.values()
            if info.format_code
        ]
        assert len(format_codes) > 0

    def test_file_not_found_raises(self) -> None:
        """Parser raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            parse_prefs_indep_output("/nonexistent/path/prefs.txt")

    def test_accepts_path_string(self, sample_prefs_path: Path) -> None:
        """Parser accepts path as string."""
        settings = parse_prefs_indep_output(str(sample_prefs_path))
        assert isinstance(settings, Settings)

    def test_accepts_path_object(self, sample_prefs_path: Path) -> None:
        """Parser accepts Path object."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        assert isinstance(settings, Settings)


class TestOutputModuleTemplate:
    """Tests for OutputModuleTemplate dataclass."""

    def test_template_attributes(self) -> None:
        """OutputModuleTemplate has expected attributes."""
        template = OutputModuleTemplate(
            name="Test Template",
            base_path="/output/path",
            file_pattern="[compName]_[#####].png",
        )
        assert template.name == "Test Template"
        assert template.base_path == "/output/path"
        assert template.file_pattern == "[compName]_[#####].png"

    def test_template_defaults(self) -> None:
        """OutputModuleTemplate has default empty strings."""
        template = OutputModuleTemplate(name="Test")
        assert template.base_path == ""
        assert template.file_pattern == ""


class TestOutputFileInfo:
    """Tests for OutputFileInfo dataclass."""

    def test_file_info_attributes(self) -> None:
        """OutputFileInfo has expected attributes."""
        info = OutputFileInfo(
            id=0,
            format_code="png!",
            raw_data="raw hex data",
        )
        assert info.id == 0
        assert info.format_code == "png!"
        assert info.raw_data == "raw hex data"


class TestSettings:
    """Tests for Settings dataclass."""

    def test_settings_defaults(self) -> None:
        """Settings has default empty values."""
        settings = Settings()
        assert settings.version == ""
        assert settings.output_module_templates == []
        assert settings.output_file_info == {}
        assert settings.output_file_options == {}
        assert isinstance(settings.output_module_prefs, OutputModulePreferences)


class TestOutputModulePreferences:
    """Tests for OutputModulePreferences dataclass."""

    def test_preferences_defaults(self) -> None:
        """OutputModulePreferences has default zero values."""
        prefs = OutputModulePreferences()
        assert prefs.default_om_index == 0
        assert prefs.prerender_om_index == 0
        assert prefs.proxy_movie_om_index == 0
        assert prefs.save_preview_om_index == 0
        assert prefs.still_frame_om_index == 0


class TestOutputFileOptions:
    """Tests for OutputFileOptions dataclass."""

    def test_file_options_attributes(self) -> None:
        """OutputFileOptions has expected attributes."""
        options = OutputFileOptions(
            id=0,
            format_code=".AVI",
            video_output=True,
            output_audio=True,
            params={"test": ExporterParam("test", 2, "value")},
            raw_data="raw data",
        )
        assert options.id == 0
        assert options.format_code == ".AVI"
        assert options.video_output is True
        assert options.output_audio is True
        assert "test" in options.params

    def test_file_options_defaults(self) -> None:
        """OutputFileOptions has default values."""
        options = OutputFileOptions(id=0, format_code="png!")
        assert options.video_output is False
        assert options.output_audio is False
        assert options.params == {}
        assert options.raw_data == ""


class TestExporterParam:
    """Tests for ExporterParam dataclass."""

    def test_exporter_param_attributes(self) -> None:
        """ExporterParam has expected attributes."""
        param = ExporterParam(
            identifier="ADBEAudioCodec",
            param_type=2,
            value="1380013856",
        )
        assert param.identifier == "ADBEAudioCodec"
        assert param.param_type == 2
        assert param.value == "1380013856"


class TestOutputModulePreferencesFromFile:
    """Tests for parsing Output Module Preferences from file."""

    @pytest.fixture
    def sample_prefs_path(self) -> Path:
        """Return path to the sample prefs file."""
        return SAMPLES_DIR / "assets" / "prefs_indep_output.txt"

    def test_parse_default_om_index(self, sample_prefs_path: Path) -> None:
        """Parser extracts default OM index."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        assert settings.output_module_prefs.default_om_index == 2

    def test_parse_prerender_om_index(self, sample_prefs_path: Path) -> None:
        """Parser extracts pre-render OM index."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        assert settings.output_module_prefs.prerender_om_index == 3

    def test_parse_still_frame_om_index(self, sample_prefs_path: Path) -> None:
        """Parser extracts still frame OM index."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        assert settings.output_module_prefs.still_frame_om_index == 4


class TestOutputFileOptionsFromFile:
    """Tests for parsing Output File Options from file."""

    @pytest.fixture
    def sample_prefs_path(self) -> Path:
        """Return path to the sample prefs file."""
        return SAMPLES_DIR / "assets" / "prefs_indep_output.txt"

    def test_parse_output_file_options(self, sample_prefs_path: Path) -> None:
        """Parser extracts output file options."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        assert len(settings.output_file_options) > 0

    def test_parse_avi_format_options(self, sample_prefs_path: Path) -> None:
        """Parser extracts AVI format options with video and audio."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        # Find an AVI entry
        avi_options = [
            opt for opt in settings.output_file_options.values()
            if opt.format_code == ".AVI"
        ]
        assert len(avi_options) > 0
        avi = avi_options[0]
        assert avi.video_output is True
        assert avi.output_audio is True

    def test_parse_wave_format_options(self, sample_prefs_path: Path) -> None:
        """Parser extracts WAVE format options with audio only."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        # Find WAVE entry (format code "wao_")
        wave_options = [
            opt for opt in settings.output_file_options.values()
            if opt.format_code == "wao_"
        ]
        assert len(wave_options) > 0
        wave = wave_options[0]
        assert wave.video_output is False
        assert wave.output_audio is True

    def test_parse_audio_params(self, sample_prefs_path: Path) -> None:
        """Parser extracts audio parameters from WAVE format."""
        settings = parse_prefs_indep_output(sample_prefs_path)
        wave_options = [
            opt for opt in settings.output_file_options.values()
            if opt.format_code == "wao_"
        ]
        assert len(wave_options) > 0
        wave = wave_options[0]
        # Check for expected audio params
        assert "ADBEAudioRatePerSecond" in wave.params
        assert "ADBEAudioNumChannels" in wave.params
        # Sample rate should be 48000
        assert wave.params["ADBEAudioRatePerSecond"].value == "48000"
