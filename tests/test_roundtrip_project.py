"""Roundtrip tests: parse -> modify -> save -> parse -> verify for Project fields."""

from __future__ import annotations

from pathlib import Path

from aep_parser import parse as parse_aep
from aep_parser.enums import (
    BitsPerChannel,
    ColorManagementSystem,
    FeetFramesFilmType,
    FootageTimecodeDisplayStartType,
    FramesCountType,
    GpuAccelType,
    LutInterpolationMethod,
    TimeDisplayType,
)

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
        project = parse_aep(SAMPLES_DIR / "linearizeWorkingSpace_false.aep").project
        assert project.linearize_working_space is False

        project.linearize_working_space = True

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.linearize_working_space is True

    def test_disable_linearize_working_space(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "linearizeWorkingSpace_true.aep").project
        assert project.linearize_working_space is True

        project.linearize_working_space = False

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.linearize_working_space is False

    def test_set_same_value_is_noop(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "linearizeWorkingSpace_false.aep").project
        assert project.linearize_working_space is False

        project.linearize_working_space = False  # no change

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.linearize_working_space is False


# ---- expression_engine ----


class TestRoundtripExpressionEngine:
    """Roundtrip tests for Project.expression_engine."""

    def test_set_extendscript(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "expressionEngine_javascript.aep").project
        assert project.expression_engine == "javascript-1.0"

        project.expression_engine = "extendscript"

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.expression_engine == "extendscript"

    def test_set_javascript(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "linearBlending_false.aep").project
        assert project.expression_engine == "extendscript"

        project.expression_engine = "javascript-1.0"

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.expression_engine == "javascript-1.0"

    def test_set_same_value_is_noop(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "expressionEngine_javascript.aep").project
        assert project.expression_engine == "javascript-1.0"

        project.expression_engine = "javascript-1.0"

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.expression_engine == "javascript-1.0"


# ---- color_management_system ----


class TestRoundtripColorManagementSystem:
    """Roundtrip tests for Project.color_management_system."""

    def test_set_ocio(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "colorManagementSystem_adobe.aep").project
        assert project.color_management_system == ColorManagementSystem.ADOBE

        project.color_management_system = ColorManagementSystem.OCIO

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.color_management_system == ColorManagementSystem.OCIO

    def test_set_adobe(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "colorManagementSystem_ocio.aep").project
        assert project.color_management_system == ColorManagementSystem.OCIO

        project.color_management_system = ColorManagementSystem.ADOBE

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.color_management_system == ColorManagementSystem.ADOBE


# ---- lut_interpolation_method ----


class TestRoundtripLutInterpolationMethod:
    """Roundtrip tests for Project.lut_interpolation_method."""

    def test_set_tetrahedral(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "lutInterpolationMethod_trilinear.aep"
        ).project
        assert project.lut_interpolation_method == LutInterpolationMethod.TRILINEAR

        project.lut_interpolation_method = LutInterpolationMethod.TETRAHEDRAL

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.lut_interpolation_method == LutInterpolationMethod.TETRAHEDRAL

    def test_set_trilinear(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "lutInterpolationMethod_tetrahedral.aep"
        ).project
        assert project.lut_interpolation_method == LutInterpolationMethod.TETRAHEDRAL

        project.lut_interpolation_method = LutInterpolationMethod.TRILINEAR

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.lut_interpolation_method == LutInterpolationMethod.TRILINEAR


# ---- ocio_configuration_file ----


class TestRoundtripOcioConfigurationFile:
    """Roundtrip tests for Project.ocio_configuration_file."""

    def test_set_ocio_config(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "colorManagementSystem_ocio.aep").project

        project.ocio_configuration_file = "new_config.ocio"

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.ocio_configuration_file == "new_config.ocio"


# ---- working_space ----


class TestRoundtripWorkingSpace:
    """Roundtrip tests for Project.working_space."""

    def test_set_working_space(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "workingSpace_sRGB.aep").project
        assert project.working_space == "sRGB IEC61966-2.1"

        project.working_space = "custom profile"

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.working_space == "custom profile"

    def test_set_same_value_is_noop(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "workingSpace_Image_P3.aep").project
        original = project.working_space

        project.working_space = original

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.working_space == original


# ---- display_color_space ----


class TestRoundtripDisplayColorSpace:
    """Roundtrip tests for Project.display_color_space."""

    def test_set_display_color_space(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "display_color_space_ACES_DCDM.aep").project
        assert project.display_color_space == "ACES/DCDM"

        project.display_color_space = "ACES/sRGB"

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.display_color_space == "ACES/sRGB"


# ---- bits_per_channel ----


class TestRoundtripBitsPerChannel:
    """Roundtrip tests for Project.bits_per_channel."""

    def test_set_sixteen(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "bitsPerChannel_8.aep").project
        assert project.bits_per_channel == BitsPerChannel.EIGHT

        project.bits_per_channel = BitsPerChannel.SIXTEEN

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.bits_per_channel == BitsPerChannel.SIXTEEN

    def test_set_thirty_two(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "bitsPerChannel_8.aep").project
        assert project.bits_per_channel == BitsPerChannel.EIGHT

        project.bits_per_channel = BitsPerChannel.THIRTY_TWO

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.bits_per_channel == BitsPerChannel.THIRTY_TWO

    def test_set_eight(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "bitsPerChannel_32.aep").project
        assert project.bits_per_channel == BitsPerChannel.THIRTY_TWO

        project.bits_per_channel = BitsPerChannel.EIGHT

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.bits_per_channel == BitsPerChannel.EIGHT


# ---- feet_frames_film_type ----


class TestRoundtripFeetFramesFilmType:
    """Roundtrip tests for Project.feet_frames_film_type."""

    def test_set_mm16(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "feetFramesFilmType_MM35.aep").project
        assert project.feet_frames_film_type == FeetFramesFilmType.MM35

        project.feet_frames_film_type = FeetFramesFilmType.MM16

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.feet_frames_film_type == FeetFramesFilmType.MM16

    def test_set_mm35(self, tmp_path: Path) -> None:
        """Set to MM16 then back to MM35 via chained roundtrip."""
        project = parse_aep(SAMPLES_DIR / "feetFramesFilmType_MM35.aep").project
        project.feet_frames_film_type = FeetFramesFilmType.MM16
        mid = tmp_path / "mid.aep"
        project.save(mid)

        project2 = parse_aep(mid).project
        project2.feet_frames_film_type = FeetFramesFilmType.MM35
        out = tmp_path / "modified.aep"
        project2.save(out)
        project3 = parse_aep(out).project

        assert project3.feet_frames_film_type == FeetFramesFilmType.MM35


# ---- footage_timecode_display_start_type ----


class TestRoundtripFootageTimecodeDisplayStartType:
    """Roundtrip tests for Project.footage_timecode_display_start_type."""

    def test_set_start_0(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "footageTimecodeDisplayStartType_source.aep"
        ).project
        assert (
            project.footage_timecode_display_start_type
            == FootageTimecodeDisplayStartType.FTCS_USE_SOURCE_MEDIA
        )

        project.footage_timecode_display_start_type = (
            FootageTimecodeDisplayStartType.FTCS_START_0
        )

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert (
            project2.footage_timecode_display_start_type
            == FootageTimecodeDisplayStartType.FTCS_START_0
        )

    def test_set_use_source_media(self, tmp_path: Path) -> None:
        """Set to START_0 then back to USE_SOURCE_MEDIA via chained roundtrip."""
        project = parse_aep(
            SAMPLES_DIR / "footageTimecodeDisplayStartType_source.aep"
        ).project
        project.footage_timecode_display_start_type = (
            FootageTimecodeDisplayStartType.FTCS_START_0
        )
        mid = tmp_path / "mid.aep"
        project.save(mid)

        project2 = parse_aep(mid).project
        project2.footage_timecode_display_start_type = (
            FootageTimecodeDisplayStartType.FTCS_USE_SOURCE_MEDIA
        )
        out = tmp_path / "modified.aep"
        project2.save(out)
        project3 = parse_aep(out).project

        assert (
            project3.footage_timecode_display_start_type
            == FootageTimecodeDisplayStartType.FTCS_USE_SOURCE_MEDIA
        )


# ---- frames_count_type ----


class TestRoundtripFramesCountType:
    """Roundtrip tests for Project.frames_count_type."""

    def test_set_start_1(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "framesCountType_start0.aep").project
        assert project.frames_count_type == FramesCountType.FC_START_0

        project.frames_count_type = FramesCountType.FC_START_1

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.frames_count_type == FramesCountType.FC_START_1

    def test_set_start_0(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "displayStartFrame_1.aep").project
        assert project.frames_count_type == FramesCountType.FC_START_1

        project.frames_count_type = FramesCountType.FC_START_0

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.frames_count_type == FramesCountType.FC_START_0


# ---- display_start_frame ----


class TestRoundtripDisplayStartFrame:
    """Roundtrip tests for Project.display_start_frame."""

    def test_set_1(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "framesCountType_start0.aep").project
        assert project.display_start_frame == 0

        project.display_start_frame = 1

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.display_start_frame == 1

    def test_set_0(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "displayStartFrame_1.aep").project
        assert project.display_start_frame == 1

        project.display_start_frame = 0

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.display_start_frame == 0


# ---- frames_use_feet_frames ----


class TestRoundtripFramesUseFeetFrames:
    """Roundtrip tests for Project.frames_use_feet_frames."""

    def test_enable(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "framesUseFeetFrames_false.aep").project
        assert project.frames_use_feet_frames == 0

        project.frames_use_feet_frames = 1

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.frames_use_feet_frames == 1

    def test_disable(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "framesUseFeetFrames_true.aep").project
        assert project.frames_use_feet_frames == 1

        project.frames_use_feet_frames = 0

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.frames_use_feet_frames == 0


# ---- time_display_type ----


class TestRoundtripTimeDisplayType:
    """Roundtrip tests for Project.time_display_type."""

    def test_set_frames(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "timeDisplayType_timecode.aep").project
        assert project.time_display_type == TimeDisplayType.TIMECODE

        project.time_display_type = TimeDisplayType.FRAMES

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.time_display_type == TimeDisplayType.FRAMES

    def test_set_timecode(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "timeDisplayType_frames.aep").project
        assert project.time_display_type == TimeDisplayType.FRAMES

        project.time_display_type = TimeDisplayType.TIMECODE

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.time_display_type == TimeDisplayType.TIMECODE


# ---- transparency_grid_thumbnails ----


class TestRoundtripTransparencyGridThumbnails:
    """Roundtrip tests for Project.transparency_grid_thumbnails."""

    def test_enable(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "transparencyGridThumbnails_false.aep"
        ).project
        assert project.transparency_grid_thumbnails is False

        project.transparency_grid_thumbnails = True

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.transparency_grid_thumbnails is True

    def test_disable(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "transparencyGridThumbnails_true.aep"
        ).project
        assert project.transparency_grid_thumbnails is True

        project.transparency_grid_thumbnails = False

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.transparency_grid_thumbnails is False


# ---- compensate_for_scene_referred_profiles ----


class TestRoundtripCompensateForSceneReferredProfiles:
    """Roundtrip tests for Project.compensate_for_scene_referred_profiles."""

    def test_enable(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "compensateForSceneReferredProfiles_false.aep"
        ).project
        assert project.compensate_for_scene_referred_profiles is False

        project.compensate_for_scene_referred_profiles = True

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.compensate_for_scene_referred_profiles is True

    def test_disable(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "compensateForSceneReferredProfiles_true.aep"
        ).project
        assert project.compensate_for_scene_referred_profiles is True

        project.compensate_for_scene_referred_profiles = False

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.compensate_for_scene_referred_profiles is False


# ---- audio_sample_rate ----


class TestRoundtripAudioSampleRate:
    """Roundtrip tests for Project.audio_sample_rate."""

    def test_set_96000(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "Audio_sample_rate_22050.aep").project
        assert project.audio_sample_rate == 22050.0

        project.audio_sample_rate = 96000.0

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.audio_sample_rate == 96000.0

    def test_set_22050(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "Audio_sample_rate_96000.aep").project
        assert project.audio_sample_rate == 96000.0

        project.audio_sample_rate = 22050.0

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.audio_sample_rate == 22050.0


# ---- working_gamma ----


class TestRoundtripWorkingGamma:
    """Roundtrip tests for Project.working_gamma."""

    def test_set_2_2(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "workingGamma_2.4.aep").project
        assert project.working_gamma == 2.4

        project.working_gamma = 2.2

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.working_gamma == 2.2

    def test_set_2_4(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "workingGamma_2.2.aep").project
        assert project.working_gamma == 2.2

        project.working_gamma = 2.4

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.working_gamma == 2.4


# ---- gpu_accel_type ----


class TestRoundtripGpuAccelType:
    """Roundtrip tests for Project.gpu_accel_type."""

    def test_set_software(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "gpuAccelType_mercury_gpu_acceleration_CUDA.aep"
        ).project
        assert project.gpu_accel_type == GpuAccelType.CUDA

        project.gpu_accel_type = GpuAccelType.SOFTWARE

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.gpu_accel_type == GpuAccelType.SOFTWARE

    def test_set_cuda(self, tmp_path: Path) -> None:
        project = parse_aep(
            SAMPLES_DIR / "gpuAccelType_mercury_software_only.aep"
        ).project
        assert project.gpu_accel_type == GpuAccelType.SOFTWARE

        project.gpu_accel_type = GpuAccelType.CUDA

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.gpu_accel_type == GpuAccelType.CUDA


# ---- revision ----


class TestRoundtripRevision:
    """Roundtrip tests for Project.revision."""

    def test_set_revision(self, tmp_path: Path) -> None:
        project = parse_aep(SAMPLES_DIR / "save_01.aep").project
        original = project.revision

        project.revision = original + 10

        out = tmp_path / "modified.aep"
        project.save(out)
        project2 = parse_aep(out).project

        assert project2.revision == original + 10
