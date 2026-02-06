from __future__ import annotations

import typing
from dataclasses import dataclass, field
from typing import Any

if typing.TYPE_CHECKING:
    from ..items.composition import CompItem
    from .output_module import OutputModule
    from .render_settings import RenderSettings


@dataclass
class RenderQueueItem:
    """
    The RenderQueueItem object represents an individual item in the render
    queue. It provides access to the specific settings for an item to be
    rendered.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/renderqueueitem/

    Attributes:
        comp: The composition that will be rendered by this render-queue item.
        comp_id: The ID of the composition being rendered by this item.
            Used internally to link to the `CompItem`.
        output_modules: The list of Output Modules for the item.
        render: When `True`, the item will be rendered when the render queue is
            started.
        render_settings: The render settings for this item, defining quality,
            resolution, motion blur, frame blending, and other rendering options.
        settings: all settings for a given Render Queue Item.
            Retrieved via ExtendScript `RenderQueueItem.getSettings(GetSettingsFormat.STRING)`.
        status: The current render status of the item.
        skip_frames: The number of frames to skip when rendering this item.
            Use this to do rendering tests that are faster than a full render.
            A value of 0 skip no frames, and results in regular rendering of
            all frames. A value of 1 skips every other frame. This is
            equivalent to "rendering on twos." Higher values skip a larger
            number of frames. The total length of time remains unchanged. For
            example, if skip has a value of 1, a sequence output would have
            half the number of frames and in movie output, each frame would be
            double the duration.
        templates: The names of all render-item templates available in the
            local installation of After Effects.
        time_span_duration: The duration in seconds of the composition to be
            rendered. The duration is determined by subtracting the start
            time from the end time.
        time_span_start: The time in the composition, in seconds, at which
            rendering will begin.
    """

    output_modules: list[OutputModule]
    comp: CompItem | None = None
    comp_id: int | None = None
    render: bool | None = None
    render_settings: RenderSettings | None = None
    status: int | None = None
    templates: list[str] = field(default_factory=list)
    time_span_start: float | None = None
    time_span_duration: float | None = None
    settings: dict[str, Any] = field(default_factory=dict)
    skip_frames: float | None = None

    def __iter__(self):
        """Allow iteration over Output Modules."""
        return iter(self.output_modules)
