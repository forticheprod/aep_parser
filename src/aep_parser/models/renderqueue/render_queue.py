from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from .render_queue_item import RenderQueueItem
    from .render_settings import RenderSettings


@dataclass
class RenderQueue:
    """
    The RenderQueue object represents the render automation process, the data
    and functionality that is available through the Render Queue panel of a
    particular After Effects project. Attributes provide access to items in
    the render queue and their render status.

    See: https://ae-scripting.docsforadobe.dev/renderqueue/renderqueue/

    Attributes:
        items: A collection of all items in the render queue.
        render_settings: Global render settings for the render queue.
            These are the default settings applied to new render queue items.
    """

    items: list[RenderQueueItem]
    render_settings: RenderSettings | None = None
