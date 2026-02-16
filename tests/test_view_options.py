"""Tests for ViewOptions model parsing using samples from models/view/.

These tests verify that aep_parser correctly reads viewer panel settings
(channels, exposure, zoom, fast preview, toggle flags, etc.) from the
`fips` chunks in the binary AEP format.

The viewer panel data is accessed via `project.active_viewer`, which
represents the focused Composition/Layer/Footage panel. Each panel has
one or more `View` objects containing `ViewOptions`.
"""

from __future__ import annotations

from pathlib import Path

from aep_parser import (
    ChannelType,
    FastPreviewType,
    ViewerType,
    parse_project,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "view"


def _get_active_view_options(aep_path: Path):  # type: ignore[no-untyped-def]
    """Parse a project and return the ViewOptions of the active viewer's active view."""
    project = parse_project(aep_path)
    assert project.active_viewer is not None, "No active viewer found"
    assert project.active_viewer.type == ViewerType.VIEWER_COMPOSITION
    idx = project.active_viewer.active_view_index
    return project.active_viewer.views[idx].options


class TestViewOptionsChannels:
    """Tests for ViewOptions.channels attribute."""

    def test_channels_rgb(self) -> None:
        """Test RGB channel display mode (default)."""
        opts = _get_active_view_options(SAMPLES_DIR / "channels_rgb.aep")
        assert opts.channels == ChannelType.CHANNEL_RGB

    def test_channels_red(self) -> None:
        """Test Red channel display mode."""
        opts = _get_active_view_options(SAMPLES_DIR / "channels_red.aep")
        assert opts.channels == ChannelType.CHANNEL_RED

    def test_channels_green(self) -> None:
        """Test Green channel display mode."""
        opts = _get_active_view_options(SAMPLES_DIR / "channels_green.aep")
        assert opts.channels == ChannelType.CHANNEL_GREEN

    def test_channels_blue(self) -> None:
        """Test Blue channel display mode."""
        opts = _get_active_view_options(SAMPLES_DIR / "channels_blue.aep")
        assert opts.channels == ChannelType.CHANNEL_BLUE

    def test_channels_alpha(self) -> None:
        """Test Alpha channel display mode."""
        opts = _get_active_view_options(SAMPLES_DIR / "channels_alpha.aep")
        assert opts.channels == ChannelType.CHANNEL_ALPHA

    def test_channels_rgb_straight(self) -> None:
        """Test RGB Straight channel display mode."""
        opts = _get_active_view_options(SAMPLES_DIR / "channels_rgb_straight.aep")
        assert opts.channels == ChannelType.CHANNEL_RGB_STRAIGHT


class TestViewOptionsCheckerboards:
    """Tests for ViewOptions.checkerboards (transparency grid) attribute."""

    def test_transparency_grid_on(self) -> None:
        """Test transparency grid enabled."""
        opts = _get_active_view_options(SAMPLES_DIR / "transparency_grid_on.aep")
        assert opts.checkerboards is True

    def test_transparency_grid_off(self) -> None:
        """Test transparency grid disabled."""
        opts = _get_active_view_options(SAMPLES_DIR / "transparency_grid_off.aep")
        assert opts.checkerboards is False


class TestViewOptionsExposure:
    """Tests for ViewOptions.exposure attribute."""

    def test_exposure_zero(self) -> None:
        """Test exposure of 0.0 (no adjustment)."""
        opts = _get_active_view_options(SAMPLES_DIR / "exposure_0.0.aep")
        assert opts.exposure == 0.0

    def test_exposure_positive(self) -> None:
        """Test positive exposure of 1.0."""
        opts = _get_active_view_options(SAMPLES_DIR / "exposure_1.0.aep")
        assert opts.exposure == 1.0

    def test_exposure_max(self) -> None:
        """Test maximum exposure of 40.0."""
        opts = _get_active_view_options(SAMPLES_DIR / "exposure_40.0.aep")
        assert opts.exposure == 40.0

    def test_exposure_min(self) -> None:
        """Test minimum exposure of -40.0."""
        opts = _get_active_view_options(SAMPLES_DIR / "exposure_-40.0.aep")
        assert opts.exposure == -40.0


class TestViewOptionsFastPreview:
    """Tests for ViewOptions.fast_preview attribute."""

    def test_fast_preview_off(self) -> None:
        """Test fast preview off."""
        opts = _get_active_view_options(SAMPLES_DIR / "fast_preview_off.aep")
        assert opts.fast_preview == FastPreviewType.FP_OFF

    def test_fast_preview_adaptive_resolution(self) -> None:
        """Test adaptive resolution fast preview mode."""
        opts = _get_active_view_options(
            SAMPLES_DIR / "fast_preview_adaptive_resolution.aep"
        )
        assert opts.fast_preview == FastPreviewType.FP_ADAPTIVE_RESOLUTION

    def test_fast_preview_wireframe(self) -> None:
        """Test wireframe fast preview mode."""
        opts = _get_active_view_options(
            SAMPLES_DIR / "fast_preview_wireframe.aep"
        )
        assert opts.fast_preview == FastPreviewType.FP_WIREFRAME


class TestViewOptionsGrid:
    """Tests for ViewOptions.grid attribute."""

    def test_grid_on(self) -> None:
        """Test grid overlay enabled."""
        opts = _get_active_view_options(SAMPLES_DIR / "grid_on.aep")
        assert opts.grid is True

    def test_grid_off(self) -> None:
        """Test grid overlay disabled."""
        opts = _get_active_view_options(SAMPLES_DIR / "grid_off.aep")
        assert opts.grid is False


class TestViewOptionsGuidesVisibility:
    """Tests for ViewOptions.guides_visibility attribute."""

    def test_guides_on(self) -> None:
        """Test guides visible."""
        opts = _get_active_view_options(SAMPLES_DIR / "guides_on.aep")
        assert opts.guides_visibility is True

    def test_guides_off(self) -> None:
        """Test guides hidden."""
        opts = _get_active_view_options(SAMPLES_DIR / "guides_off.aep")
        assert opts.guides_visibility is False


class TestViewOptionsMaskAndShapePath:
    """Tests for ViewOptions.mask_and_shape_path attribute."""

    def test_mask_and_shape_path_on(self) -> None:
        """Test mask and shape path visibility enabled."""
        opts = _get_active_view_options(
            SAMPLES_DIR / "mask_and_shape_path_on.aep"
        )
        assert opts.mask_and_shape_path is True

    def test_mask_and_shape_path_off(self) -> None:
        """Test mask and shape path visibility disabled."""
        opts = _get_active_view_options(
            SAMPLES_DIR / "mask_and_shape_path_off.aep"
        )
        assert opts.mask_and_shape_path is False


class TestViewOptionsProportionalGrid:
    """Tests for ViewOptions.proportional_grid attribute."""

    def test_proportional_grid_on(self) -> None:
        """Test proportional grid enabled."""
        opts = _get_active_view_options(
            SAMPLES_DIR / "proportional_grid_on.aep"
        )
        assert opts.proportional_grid is True

    def test_proportional_grid_off(self) -> None:
        """Test proportional grid disabled."""
        opts = _get_active_view_options(
            SAMPLES_DIR / "proportional_grid_off.aep"
        )
        assert opts.proportional_grid is False


class TestViewOptionsRegionOfInterest:
    """Tests for ViewOptions.region_of_interest attribute."""

    def test_roi_on(self) -> None:
        """Test region of interest enabled."""
        opts = _get_active_view_options(SAMPLES_DIR / "roi_on.aep")
        assert opts.region_of_interest is True

    def test_roi_off(self) -> None:
        """Test region of interest disabled."""
        opts = _get_active_view_options(SAMPLES_DIR / "roi_off.aep")
        assert opts.region_of_interest is False


class TestViewOptionsRulers:
    """Tests for ViewOptions.rulers attribute."""

    def test_rulers_on(self) -> None:
        """Test rulers displayed."""
        opts = _get_active_view_options(SAMPLES_DIR / "rulers_on.aep")
        assert opts.rulers is True

    def test_rulers_off(self) -> None:
        """Test rulers hidden."""
        opts = _get_active_view_options(SAMPLES_DIR / "rulers_off.aep")
        assert opts.rulers is False


class TestViewOptionsTitleActionSafe:
    """Tests for ViewOptions.title_action_safe attribute."""

    def test_title_action_safe_on(self) -> None:
        """Test title/action safe guides displayed."""
        opts = _get_active_view_options(
            SAMPLES_DIR / "title_action_safe_on.aep"
        )
        assert opts.title_action_safe is True

    def test_title_action_safe_off(self) -> None:
        """Test title/action safe guides hidden."""
        opts = _get_active_view_options(
            SAMPLES_DIR / "title_action_safe_off.aep"
        )
        assert opts.title_action_safe is False


class TestViewOptionsUseDisplayColorManagement:
    """Tests for ViewOptions.use_display_color_management attribute."""

    def test_display_color_management_on(self) -> None:
        """Test display color management enabled (default)."""
        opts = _get_active_view_options(SAMPLES_DIR / "channels_rgb.aep")
        assert opts.use_display_color_management is True

    def test_display_color_management_off(self) -> None:
        """Test display color management disabled."""
        opts = _get_active_view_options(
            SAMPLES_DIR / "channels_use_display_color_management_off.aep"
        )
        assert opts.use_display_color_management is False


class TestViewOptionsZoom:
    """Tests for ViewOptions.zoom attribute."""

    def test_zoom_25(self) -> None:
        """Test 25% zoom level."""
        opts = _get_active_view_options(SAMPLES_DIR / "zoom_25.aep")
        assert opts.zoom == 0.25

    def test_zoom_100(self) -> None:
        """Test 100% zoom level."""
        opts = _get_active_view_options(SAMPLES_DIR / "zoom_100.aep")
        assert opts.zoom == 1.0

    def test_zoom_1600(self) -> None:
        """Test 1600% zoom level."""
        opts = _get_active_view_options(SAMPLES_DIR / "zoom_1600.aep")
        assert opts.zoom == 16.0
