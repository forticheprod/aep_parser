from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from ..enums import ChannelType, FastPreviewType


@dataclass
class ViewOptions:
    """
    The `ViewOptions` object represents the options for a given [View][] object.

    See: https://ae-scripting.docsforadobe.dev/other/viewoptions/
    """

    channels: ChannelType
    """
    The state of the Channels menu.
    """

    checkerboards: bool
    """
    When `True`, checkerboards (transparency grid) is enabled in the current view.
    """

    draft3d: bool
    """
    When `True`, Draft 3D mode is enabled for the Composition panel. This
    corresponds to the value of the Draft 3D button in the Composition panel.
    """

    exposure: float
    """
    The exposure value for the current view.
    """

    fast_preview: FastPreviewType
    """
    The state of the Fast Previews menu.
    """

    grid: bool
    """When `True`, the grid overlay is visible in the view."""

    guides_visibility: bool
    """
    When `True`, indicates guides are visible in the view.
    """

    mask_and_shape_path: bool
    """When `True`, indicates mask and shape paths are visible in the view."""

    proportional_grid: bool
    """When `True`, indicatesthe proportional grid overlay is visible in the view."""

    region_of_interest: bool
    """
    When `True`, the region of interest (ROI) selection is active in the view.
    """

    rulers: bool
    """When `True`, indicates rulers are shown in the view."""

    title_action_safe: bool
    """
    When `True`, indicates title/action safe margin guides are visible in the view.
    """

    use_display_color_management: bool
    """
    When `True`, indicates display color management is enabled for the view.
    """

    zoom: float
    """
    The current zoom value for the view, as a normalized percentage between 1%
    (0.01) and 1600% (16).
    """
