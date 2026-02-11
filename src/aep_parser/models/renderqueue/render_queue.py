from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from .render_queue_item import RenderQueueItem


@dataclass
class RenderQueue:
    """
    The `RenderQueue` object represents the render automation process, the data
    and functionality that is available through the Render Queue panel of a
    particular After Effects project. Attributes provide access to items in
    the render queue and their render status.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/renderqueue/
    """

    items: list[RenderQueueItem]
    """A collection of all items in the render queue."""
