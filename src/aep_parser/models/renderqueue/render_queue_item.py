from __future__ import annotations

import typing
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from ..enums import LogType, RQItemStatus

if typing.TYPE_CHECKING:
    from typing import Iterator

    from ..items.composition import CompItem
    from .output_module import OutputModule

AEP_EPOCH = datetime(1904, 1, 1)  # Mac HFS+ epoch Jan 1, 1904


@dataclass
class RenderQueueItem:
    """
    The `RenderQueueItem` object represents an individual item in the render
    queue. It provides access to the specific settings for an item to be
    rendered.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/renderqueueitem/
    """

    comment: str
    """A comment that describes the render queue item. This shows in the Render Queue panel."""

    comp: CompItem = field(repr=False)
    """The composition that will be rendered by this render-queue item."""

    output_modules: list[OutputModule]
    """The list of Output Modules for the item."""

    render: bool
    """When `True`, the item will be rendered when the render queue is started."""

    settings: dict[str, Any]
    """
    Dict with ExtendScript-compatible keys matching getSettings() output.
    Contains quality, resolution, motion blur, frame blending, and other
    rendering options.
    """

    skip_frames: int
    """
    The number of frames to skip when rendering this item. Use this to do
    rendering tests that are faster than a full render. A value of 0 skip no
    frames, and results in regular rendering of all frames. A value of 1 skips
    every other frame. This is equivalent to "rendering on twos." Higher
    values skip a larger number of frames. The total length of time remains
    unchanged. For example, if skip has a value of 1, a sequence output would
    have half the number of frames and in movie output, each frame would be
    double the duration.
    """

    status: RQItemStatus
    """The current render status of the item."""

    templates: list[str] = field(default_factory=list)  # TODO
    """
    The names of all render-item templates available in the local installation
    of After Effects.
    """

    @property
    def time_span_start(self) -> float:
        """
        The time in the composition, in seconds, at which rendering will
        begin.
        """
        return float(self.settings["Time Span Start"])

    @property
    def time_span_duration(self) -> float:
        """
        The duration in seconds of the composition to be rendered. The
        duration is determined by subtracting the start time from the end
        time.
        """
        return float(self.settings["Time Span Duration"])

    @property
    def time_span_end(self) -> float:
        """
        The time in the composition, in seconds, at which rendering will end.
        """
        return self.time_span_start + self.time_span_duration

    @property
    def time_span_start_frames(self) -> int:
        """
        The time in the composition, in frames, at which rendering will begin.
        """
        return int(self.settings["Time Span Start Frames"])

    @property
    def time_span_duration_frames(self) -> int:
        """
        The duration in frames of the composition to be rendered. The duration
        is determined by subtracting the start time from the end time.
        """
        return int(self.settings["Time Span Duration Frames"])

    @property
    def time_span_end_frames(self) -> int:
        """
        The time in the composition, in frames, at which rendering will end.
        """
        return self.time_span_start_frames + self.time_span_duration_frames

    @property
    def elapsed_seconds(self) -> int | None:
        """
        The number of seconds that have elapsed in rendering this item, or
        `None` if the item has not started rendering.
        """
        if self.status is None:
            return None
        return int(self.settings["Elapsed Seconds"])

    @property
    def start_time(self) -> datetime | None:
        if self.status is None:
            return None
        return AEP_EPOCH + timedelta(seconds=self.settings["Start Time"])

    @property
    def comp_name(self) -> str:
        """The name of the composition being rendered."""
        return self.comp.name

    @property
    def log_type(self) -> LogType:
        """
        A log type for this item, indicating which events should be logged
        while this item is being rendered.
        """
        return LogType(self.settings["Log Type"])

    @property
    def queue_item_notify(self) -> bool:
        """
        When `True`, a user notification is enabled for this render queue
        item, signaling the user upon render completion.
        """
        return bool(self.settings["Queue Item Notify"])

    def __iter__(self) -> Iterator[OutputModule]:
        """Allow iteration over Output Modules."""
        return iter(self.output_modules)
