"""Tests for render queue settings parsing."""

from __future__ import annotations

from pathlib import Path

import pytest

from aep_parser import parse_project
from aep_parser.models.renderqueue import (
    AudioBitDepth,
    AudioChannels,
    ColorDepthSetting,
    EffectsSetting,
    FieldRender,
    FrameBlendingSetting,
    GuideLayers,
    MotionBlurSetting,
    ProxyUseSetting,
    RenderQuality,
    SoloSwitchesSetting,
    TimeSpanSource,
)


SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "debug"


class TestRenderSettings:
    """Tests for RenderSettings parsing."""

    def test_base_settings(self) -> None:
        """Test base render settings template."""
        project = parse_project(SAMPLES_DIR / "render_queue_base.aep")
        rs = project.render_queue.render_settings

        assert rs is not None
        assert rs.template_name == "Best Settings"
        assert rs.quality == RenderQuality.BEST
        assert rs.resolution_x == 1
        assert rs.resolution_y == 1
        assert rs.resolution_name == "Full"
        assert rs.frame_rate == 30.0
        assert rs.use_this_frame_rate is False

    def test_quality_draft(self) -> None:
        """Test draft quality setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_custom_quality_draft.aep")
        rs = project.render_queue.render_settings

        assert rs.quality == RenderQuality.DRAFT

    def test_quality_wireframe(self) -> None:
        """Test wireframe quality setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_custom_quality_wireframe.aep")
        rs = project.render_queue.render_settings

        assert rs.quality == RenderQuality.WIREFRAME

    def test_resolution_half(self) -> None:
        """Test half resolution setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_custom_resolution_half.aep")
        rs = project.render_queue.render_settings

        assert rs.resolution_x == 2
        assert rs.resolution_y == 2
        assert rs.resolution_name == "Half"

    def test_resolution_third(self) -> None:
        """Test third resolution setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_custom_resolution_third.aep")
        rs = project.render_queue.render_settings

        assert rs.resolution_x == 3
        assert rs.resolution_y == 3
        assert rs.resolution_name == "Third"

    def test_resolution_quarter(self) -> None:
        """Test quarter resolution setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_custom_resolution_quarter.aep")
        rs = project.render_queue.render_settings

        assert rs.resolution_x == 4
        assert rs.resolution_y == 4
        assert rs.resolution_name == "Quarter"

    def test_resolution_custom(self) -> None:
        """Test custom resolution setting."""
        project = parse_project(
            SAMPLES_DIR / "render_queue_custom_resolution_custom_7_horizontal_3_vertical.aep"
        )
        rs = project.render_queue.render_settings

        assert rs.resolution_x == 7
        assert rs.resolution_y == 3
        assert rs.resolution_name == "Custom (7×3)"

    def test_color_depth_8bit(self) -> None:
        """Test 8-bit color depth setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_color_depth_8.aep")
        rs = project.render_queue.render_settings

        assert rs.color_depth == ColorDepthSetting.EIGHT_BITS_PER_CHANNEL

    def test_color_depth_16bit(self) -> None:
        """Test 16-bit color depth setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_color_depth_16.aep")
        rs = project.render_queue.render_settings

        assert rs.color_depth == ColorDepthSetting.SIXTEEN_BITS_PER_CHANNEL

    def test_color_depth_32bit(self) -> None:
        """Test 32-bit color depth setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_color_depth_32.aep")
        rs = project.render_queue.render_settings

        assert rs.color_depth == ColorDepthSetting.THIRTY_TWO_BITS_PER_CHANNEL

    def test_field_render_lower_first(self) -> None:
        """Test lower field first setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_field_render_lower_field_first.aep")
        rs = project.render_queue.render_settings

        assert rs.field_render == FieldRender.LOWER_FIELD_FIRST

    def test_field_render_upper_first(self) -> None:
        """Test upper field first setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_field_render_upper_field_first.aep")
        rs = project.render_queue.render_settings

        assert rs.field_render == FieldRender.UPPER_FIELD_FIRST

    def test_frame_blending_current(self) -> None:
        """Test frame blending current settings."""
        project = parse_project(SAMPLES_DIR / "render_queue_frame_blending_current.aep")
        rs = project.render_queue.render_settings

        assert rs.frame_blending == FrameBlendingSetting.ON_FOR_ALL_LAYERS

    def test_frame_blending_off(self) -> None:
        """Test frame blending off for all layers."""
        project = parse_project(SAMPLES_DIR / "render_queue_frame_blending_off_for_all_layers.aep")
        rs = project.render_queue.render_settings

        assert rs.frame_blending == FrameBlendingSetting.OFF_FOR_ALL_LAYERS

    def test_motion_blur_current(self) -> None:
        """Test motion blur current settings."""
        project = parse_project(SAMPLES_DIR / "render_queue_motion_blur_current.aep")
        rs = project.render_queue.render_settings

        assert rs.motion_blur == MotionBlurSetting.ON_FOR_ALL_LAYERS

    def test_motion_blur_off(self) -> None:
        """Test motion blur off for all layers."""
        project = parse_project(SAMPLES_DIR / "render_queue_motion_blur_off_for_all_layers.aep")
        rs = project.render_queue.render_settings

        assert rs.motion_blur == MotionBlurSetting.OFF_FOR_ALL_LAYERS

    def test_use_this_frame_rate_24(self) -> None:
        """Test custom frame rate 24fps."""
        project = parse_project(SAMPLES_DIR / "render_queue_use_this_frame_rate_24.aep")
        rs = project.render_queue.render_settings

        assert rs.frame_rate == 24.0
        assert rs.use_this_frame_rate is True

    def test_use_this_frame_rate_30(self) -> None:
        """Test custom frame rate 30fps."""
        project = parse_project(SAMPLES_DIR / "render_queue_use_this_frame_rate_30.aep")
        rs = project.render_queue.render_settings

        assert rs.frame_rate == 30.0
        assert rs.use_this_frame_rate is True

    def test_proxy_use_all_proxies(self) -> None:
        """Test use all proxies setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_custom_proxy_use_use_all_proxies.aep")
        rs = project.render_queue.render_settings

        assert rs.proxy_use == ProxyUseSetting.USE_ALL_PROXIES

    def test_proxy_use_comp_proxies_only(self) -> None:
        """Test use comp proxies only setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_custom_proxy_use_use_comp_proxies_only.aep")
        rs = project.render_queue.render_settings

        assert rs.proxy_use == ProxyUseSetting.USE_COMP_PROXIES_ONLY

    def test_effects_all_on(self) -> None:
        """Test effects all on setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_custom_effects_all_on.aep")
        rs = project.render_queue.render_settings

        assert rs.effects == EffectsSetting.ALL_ON

    def test_effects_all_off(self) -> None:
        """Test effects all off setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_custom_effects_all_off.aep")
        rs = project.render_queue.render_settings

        assert rs.effects == EffectsSetting.ALL_OFF

    def test_solo_switches_all_off(self) -> None:
        """Test solo switches all off setting."""
        project = parse_project(SAMPLES_DIR / "render_queue_custom_solo_switches_all_off.aep")
        rs = project.render_queue.render_settings

        assert rs.solo_switches == SoloSwitchesSetting.ALL_OFF

    def test_guide_layers_current(self) -> None:
        """Test guide layers current settings."""
        project = parse_project(SAMPLES_DIR / "render_queue_guide_layers_current.aep")
        rs = project.render_queue.render_settings

        assert rs.guide_layers == GuideLayers.CURRENT_SETTINGS

    def test_time_span_length_of_comp(self) -> None:
        """Test time span length of comp."""
        project = parse_project(SAMPLES_DIR / "render_queue_time_span_length_of_comp.aep")
        rs = project.render_queue.render_settings

        assert rs.time_span_source == TimeSpanSource.LENGTH_OF_COMP


class TestOutputModuleSettings:
    """Tests for OutputModuleSettings parsing."""

    def test_base_output_module(self) -> None:
        """Test base output module settings."""
        project = parse_project(SAMPLES_DIR / "render_queue_base.aep")
        om = project.render_queue.items[0].output_modules[0]

        assert om.om_settings is not None
        assert om.om_settings.has_audio is True
        assert om.om_settings.audio_channels == AudioChannels.STEREO
        assert om.om_settings.audio_bit_depth == AudioBitDepth.SIXTEEN_BIT
        assert om.om_settings.color_premultiplied is True

    def test_audio_output_off(self) -> None:
        """Test audio output disabled."""
        project = parse_project(SAMPLES_DIR / "render_queue_output_module_audio_output_off.aep")
        om = project.render_queue.items[0].output_modules[0].om_settings

        assert om.has_audio is False

    def test_audio_mono(self) -> None:
        """Test mono audio channel."""
        project = parse_project(SAMPLES_DIR / "render_queue_output_module_audio_mono.aep")
        om = project.render_queue.items[0].output_modules[0].om_settings

        assert om.audio_channels == AudioChannels.MONO

    def test_audio_8bit(self) -> None:
        """Test 8-bit audio depth."""
        project = parse_project(SAMPLES_DIR / "render_queue_output_module_audio_8bit.aep")
        om = project.render_queue.items[0].output_modules[0].om_settings

        assert om.audio_bit_depth == AudioBitDepth.EIGHT_BIT

    def test_audio_32bit(self) -> None:
        """Test 32-bit audio depth."""
        project = parse_project(SAMPLES_DIR / "render_queue_output_module_audio_32bit.aep")
        om = project.render_queue.items[0].output_modules[0].om_settings

        assert om.audio_bit_depth == AudioBitDepth.THIRTY_TWO_BIT

    def test_color_straight_unmatted(self) -> None:
        """Test straight (unmatted) color mode."""
        project = parse_project(SAMPLES_DIR / "render_queue_output_module_color_straight_unmatted.aep")
        om = project.render_queue.items[0].output_modules[0].om_settings

        assert om.color_premultiplied is False
        assert om.color_matted is False
