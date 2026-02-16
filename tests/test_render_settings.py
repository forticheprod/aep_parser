"""Tests for render queue settings parsing."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import parse_project

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "renderqueue"


class TestRenderSettings:
    """Tests for render settings parsing as dict."""

    def test_base_settings(self) -> None:
        """Test base render settings template."""
        project = parse_project(SAMPLES_DIR / "base.aep")
        rs = project.render_queue.items[0].settings

        assert rs is not None
        assert rs["Quality"] == 2  # Best
        assert rs["Resolution"] == [1, 1]  # Full
        assert rs["Frame Rate"] == 0

    def test_quality_draft(self) -> None:
        """Test draft quality setting."""
        project = parse_project(SAMPLES_DIR / "custom_quality_draft.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Quality"] == 1  # Draft

    def test_quality_wireframe(self) -> None:
        """Test wireframe quality setting."""
        project = parse_project(SAMPLES_DIR / "custom_quality_wireframe.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Quality"] == 0  # Wireframe

    def test_resolution_half(self) -> None:
        """Test half resolution setting."""
        project = parse_project(SAMPLES_DIR / "custom_resolution_half.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Resolution"] == [2, 2]  # Half

    def test_resolution_third(self) -> None:
        """Test third resolution setting."""
        project = parse_project(SAMPLES_DIR / "custom_resolution_third.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Resolution"] == [3, 3]  # Third

    def test_resolution_quarter(self) -> None:
        """Test quarter resolution setting."""
        project = parse_project(SAMPLES_DIR / "custom_resolution_quarter.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Resolution"] == [4, 4]  # Quarter

    def test_resolution_custom(self) -> None:
        """Test custom resolution setting."""
        project = parse_project(
            SAMPLES_DIR / "custom_resolution_custom_7_horizontal_3_vertical.aep"
        )
        rs = project.render_queue.items[0].settings

        assert rs["Resolution"] == [7, 3]  # Custom 7x3

    def test_color_depth_8bit(self) -> None:
        """Test 8-bit color depth setting."""
        project = parse_project(SAMPLES_DIR / "color_depth_8.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Color Depth"] == 0  # 8-bit

    def test_color_depth_16bit(self) -> None:
        """Test 16-bit color depth setting."""
        project = parse_project(SAMPLES_DIR / "color_depth_16.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Color Depth"] == 1  # 16-bit

    def test_color_depth_32bit(self) -> None:
        """Test 32-bit color depth setting."""
        project = parse_project(SAMPLES_DIR / "color_depth_32.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Color Depth"] == 2  # 32-bit

    def test_field_render_lower_first(self) -> None:
        """Test lower field first setting."""
        project = parse_project(SAMPLES_DIR / "field_render_lower_field_first.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Field Render"] == 2  # Lower Field First

    def test_field_render_upper_first(self) -> None:
        """Test upper field first setting."""
        project = parse_project(SAMPLES_DIR / "field_render_upper_field_first.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Field Render"] == 1  # Upper Field First

    def test_pulldown_off(self) -> None:
        """Test pulldown off (default)."""
        project = parse_project(SAMPLES_DIR / "base.aep")
        rs = project.render_queue.items[0].settings

        assert rs["3:2 Pulldown"] == 0  # Off

    def test_pulldown_wssww(self) -> None:
        """Test 3:2 pulldown WSSWW setting."""
        project = parse_project(
            SAMPLES_DIR / "field_render_upper_field_first_pulldown_wssww.aep"
        )
        rs = project.render_queue.items[0].settings

        assert rs["3:2 Pulldown"] == 1  # WSSWW

    def test_pulldown_sswww(self) -> None:
        """Test 3:2 pulldown SSWWW setting."""
        project = parse_project(
            SAMPLES_DIR / "field_render_upper_field_first_pulldown_sswww.aep"
        )
        rs = project.render_queue.items[0].settings

        assert rs["3:2 Pulldown"] == 2  # SSWWW

    def test_pulldown_swwws(self) -> None:
        """Test 3:2 pulldown SWWWS setting."""
        project = parse_project(
            SAMPLES_DIR / "field_render_upper_field_first_pulldown_swwws.aep"
        )
        rs = project.render_queue.items[0].settings

        assert rs["3:2 Pulldown"] == 3  # SWWWS

    def test_pulldown_wwwss(self) -> None:
        """Test 3:2 pulldown WWWSS setting."""
        project = parse_project(
            SAMPLES_DIR / "field_render_upper_field_first_pulldown_wwwss.aep"
        )
        rs = project.render_queue.items[0].settings

        assert rs["3:2 Pulldown"] == 4  # WWWSS

    def test_pulldown_wwssw(self) -> None:
        """Test 3:2 pulldown WWSSW setting."""
        project = parse_project(
            SAMPLES_DIR / "field_render_upper_field_first_pulldown_wwssw.aep"
        )
        rs = project.render_queue.items[0].settings

        assert rs["3:2 Pulldown"] == 5  # WWSSW

    def test_frame_blending_current(self) -> None:
        """Test frame blending current settings."""
        project = parse_project(SAMPLES_DIR / "frame_blending_current.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Frame Blending"] == 2  # Current Settings

    def test_frame_blending_off(self) -> None:
        """Test frame blending off for all layers."""
        project = parse_project(SAMPLES_DIR / "frame_blending_off_for_all_layers.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Frame Blending"] == 0  # Off for All Layers

    def test_motion_blur_current(self) -> None:
        """Test motion blur current settings."""
        project = parse_project(SAMPLES_DIR / "motion_blur_current.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Motion Blur"] == 2  # Current Settings

    def test_motion_blur_off(self) -> None:
        """Test motion blur off for all layers."""
        project = parse_project(SAMPLES_DIR / "motion_blur_off_for_all_layers.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Motion Blur"] == 0  # Off for All Layers

    def test_use_this_frame_rate_24(self) -> None:
        """Test custom frame rate 24fps."""
        project = parse_project(SAMPLES_DIR / "use_this_frame_rate_24.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Frame Rate"]
        assert rs["Use this frame rate"] == 24.0

    def test_use_this_frame_rate_30(self) -> None:
        """Test custom frame rate 30fps."""
        project = parse_project(SAMPLES_DIR / "use_this_frame_rate_30.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Frame Rate"]
        assert rs["Use this frame rate"] == 30.0

    def test_proxy_use_all_proxies(self) -> None:
        """Test use all proxies setting."""
        project = parse_project(SAMPLES_DIR / "custom_proxy_use_use_all_proxies.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Proxy Use"] == 1  # Use All Proxies

    def test_proxy_use_comp_proxies_only(self) -> None:
        """Test use comp proxies only setting."""
        project = parse_project(SAMPLES_DIR / "custom_proxy_use_use_comp_proxies_only.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Proxy Use"] == 3  # Use Comp Proxies Only

    def test_effects_all_on(self) -> None:
        """Test effects all on setting."""
        project = parse_project(SAMPLES_DIR / "custom_effects_all_on.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Effects"] == 1  # All On

    def test_effects_all_off(self) -> None:
        """Test effects all off setting."""
        project = parse_project(SAMPLES_DIR / "custom_effects_all_off.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Effects"] == 0  # All Off

    def test_solo_switches_all_off(self) -> None:
        """Test solo switches all off setting."""
        project = parse_project(SAMPLES_DIR / "custom_solo_switches_all_off.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Solo Switches"] == 0  # All Off

    def test_guide_layers_current(self) -> None:
        """Test guide layers current settings."""
        project = parse_project(SAMPLES_DIR / "guide_layers_current.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Guide Layers"] == 2  # Current Settings

    def test_disk_cache_read_only(self) -> None:
        """Test disk cache read only (default)."""
        project = parse_project(SAMPLES_DIR / "custom.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Disk Cache"] == 0  # Read Only

    def test_disk_cache_current_settings(self) -> None:
        """Test disk cache current settings."""
        project = parse_project(SAMPLES_DIR / "custom_disk_cache_current.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Disk Cache"] == 2  # Current Settings

    def test_time_span_length_of_comp(self) -> None:
        """Test time span length of comp."""
        project = parse_project(SAMPLES_DIR / "time_span_length_of_comp.aep")
        rs = project.render_queue.items[0].settings

        assert rs["Time Span"] == 0  # Length of Comp

    def test_time_span_start_zero(self) -> None:
        """Test time span start of zero."""
        project = parse_project(
            SAMPLES_DIR / "time_span_custom_start_00_duration_24s13f.aep"
        )
        rs = project.render_queue.items[0].settings

        assert rs["Time Span Start"] == 0.0

    def test_time_span_start_custom(self) -> None:
        """Test custom time span start (1s 23f at 24fps)."""
        project = parse_project(
            SAMPLES_DIR / "time_span_custom_start_01s_23f_duration_24s13f.aep"
        )
        rs = project.render_queue.items[0].settings

        # 1s + 23 frames at 24fps = 1 + 23/24 = 1.9583... seconds
        assert abs(rs["Time Span Start"] - (1 + 23 / 24)) < 0.0001

    def test_time_span_duration(self) -> None:
        """Test time span duration (24s 13f at 24fps)."""
        project = parse_project(
            SAMPLES_DIR / "time_span_custom_start_00_duration_24s13f.aep"
        )
        rs = project.render_queue.items[0].settings

        # 24s + 13 frames at 24fps = 24 + 13/24 = 24.5416... seconds
        assert abs(rs["Time Span Duration"] - (24 + 13 / 24)) < 0.0001

    def test_time_span_duration_30s(self) -> None:
        """Test time span duration of exactly 30 seconds."""
        project = parse_project(
            SAMPLES_DIR / "time_span_custom_start_00_duration_30s.aep"
        )
        rs = project.render_queue.items[0].settings

        assert rs["Time Span Duration"] == 30.0


class TestOutputModuleSettings:
    """Tests for OutputModuleSettings parsing."""

    def test_base_output_module(self) -> None:
        """Test base output module settings."""
        project = parse_project(SAMPLES_DIR / "base.aep")
        om = project.render_queue.items[0].output_modules[0]

        assert om.settings is not None
        assert om.settings["Audio Channels"] == 2  # Stereo
        assert om.settings["Audio Bit Depth"] == 2  # 16-bit
        assert om.settings["Color"] == 1  # Premultiplied

    def test_audio_output_off(self) -> None:
        """Test audio output disabled."""
        project = parse_project(SAMPLES_DIR / "output_module_audio_output_off.aep")
        settings = project.render_queue.items[0].output_modules[0].settings

        # Audio settings still present even when disabled
        assert settings is not None

    def test_audio_mono(self) -> None:
        """Test mono audio channel."""
        project = parse_project(SAMPLES_DIR / "output_module_audio_mono.aep")
        settings = project.render_queue.items[0].output_modules[0].settings

        assert settings["Audio Channels"] == 1  # Mono

    def test_audio_8bit(self) -> None:
        """Test 8-bit audio depth."""
        project = parse_project(SAMPLES_DIR / "output_module_audio_8bit.aep")
        settings = project.render_queue.items[0].output_modules[0].settings

        assert settings["Audio Bit Depth"] == 1  # 8-bit

    def test_audio_32bit(self) -> None:
        """Test 32-bit audio depth."""
        project = parse_project(SAMPLES_DIR / "output_module_audio_32bit.aep")
        settings = project.render_queue.items[0].output_modules[0].settings

        assert settings["Audio Bit Depth"] == 4  # 32-bit

    @pytest.mark.skip(
        reason="Cannot generate via ExtendScript - Color setting ignored by AE API"
    )
    def test_color_straight_unmatted(self) -> None:
        """Test straight (unmatted) color mode."""
        project = parse_project(SAMPLES_DIR / "output_module_color_straight_unmatted.aep")
        settings = project.render_queue.items[0].output_modules[0].settings

        assert settings["Color"] == 0  # Straight (Unmatted)

    def test_include_source_xmp_off(self) -> None:
        """Test include source XMP is False when disabled."""
        project = parse_project(
            SAMPLES_DIR / "output_module_include_source_xmp_data_off.aep"
        )
        om = project.render_queue.items[0].output_modules[0]

        assert om.include_source_xmp is False

    def test_include_source_xmp_on(self) -> None:
        """Test include source XMP is True when enabled."""
        project = parse_project(
            SAMPLES_DIR / "output_module_include_source_xmp_data_on.aep"
        )
        om = project.render_queue.items[0].output_modules[0]

        assert om.include_source_xmp is True

    def test_video_output_on(self) -> None:
        """Test video output is enabled (default)."""
        project = parse_project(SAMPLES_DIR / "output_module_custom_h264.aep")
        settings = project.render_queue.items[0].output_modules[0].settings

        assert settings["Video Output"] is True
        assert settings["Width"] == 1920
        assert settings["Height"] == 1080

    def test_video_output_off(self) -> None:
        """Test video output is disabled."""
        project = parse_project(SAMPLES_DIR / "output_module_custom_has_video_off.aep")
        settings = project.render_queue.items[0].output_modules[0].settings

        assert settings["Video Output"] is False
        assert settings["Width"] == 0
        assert settings["Height"] == 0


class TestOutputModule:
    """Tests for OutputModule parsing."""

    def test_post_render_action_none(self) -> None:
        """Test post_render_action is NONE by default."""
        from aep_parser.models.enums import PostRenderAction

        project = parse_project(SAMPLES_DIR / "base.aep")
        om = project.render_queue.items[0].output_modules[0]

        assert om.post_render_action == PostRenderAction.NONE

    def test_post_render_action_import(self) -> None:
        """Test post_render_action is IMPORT."""
        from aep_parser.models.enums import PostRenderAction

        project = parse_project(SAMPLES_DIR / "post_render_import.aep")
        om = project.render_queue.items[0].output_modules[0]

        assert om.post_render_action == PostRenderAction.IMPORT

    def test_post_render_action_import_and_replace(self) -> None:
        """Test post_render_action is IMPORT_AND_REPLACE_USAGE."""
        from aep_parser.models.enums import PostRenderAction

        project = parse_project(
            SAMPLES_DIR / "post_render_import_and_replace_this_comp.aep"
        )
        om = project.render_queue.items[0].output_modules[0]

        assert om.post_render_action == PostRenderAction.IMPORT_AND_REPLACE_USAGE

    def test_post_render_action_set_proxy(self) -> None:
        """Test post_render_action is SET_PROXY."""
        from aep_parser.models.enums import PostRenderAction

        project = parse_project(
            SAMPLES_DIR / "post_render_set_proxy_this_comp.aep"
        )
        om = project.render_queue.items[0].output_modules[0]

        assert om.post_render_action == PostRenderAction.SET_PROXY


class TestRenderQueueItem:
    """Tests for RenderQueueItem parsing."""

    def test_render_enabled(self) -> None:
        """Test render flag is True when item is queued."""
        project = parse_project(SAMPLES_DIR / "base.aep")
        item = project.render_queue.items[0]

        assert item.render is True

    def test_render_disabled(self) -> None:
        """Test render flag is False when unchecked in queue."""
        project = parse_project(SAMPLES_DIR / "render_unchecked.aep")
        item = project.render_queue.items[0]

        assert item.render is False

    def test_item_time_span_start(self) -> None:
        """Test RenderQueueItem.time_span_start property."""
        project = parse_project(
            SAMPLES_DIR / "time_span_custom_start_01s_23f_duration_24s13f.aep"
        )
        item = project.render_queue.items[0]

        # Should delegate to settings.time_span_start (1s 23f at 24fps)
        assert abs(item.time_span_start - (1 + 23 / 24)) < 0.0001

    def test_item_time_span_duration(self) -> None:
        """Test RenderQueueItem.time_span_duration property."""
        project = parse_project(
            SAMPLES_DIR / "time_span_custom_start_00_duration_30s.aep"
        )
        item = project.render_queue.items[0]

        # Should delegate to settings.time_span_duration
        assert item.time_span_duration == 30.0

    def test_comment(self) -> None:
        """Test RenderQueueItem.comment is parsed from RCom chunk."""
        project = parse_project(SAMPLES_DIR / "comment_aaaaa.aep")
        item = project.render_queue.items[0]

        assert item.comment == "aaaaa"

    def test_default_comment(self) -> None:
        """Test RenderQueueItem.comment is None when no comment set."""
        project = parse_project(SAMPLES_DIR / "base.aep")
        item = project.render_queue.items[0]

        assert item.comment == ""
