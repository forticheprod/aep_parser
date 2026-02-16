from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from ..enums import ViewerType
    from .view import View


@dataclass
class Viewer:
    """
    The `Viewer` object represents a Composition, Layer, or Footage panel.

    See: https://ae-scripting.docsforadobe.dev/other/viewer/
    """

    active: bool
    """
    When `True`, indicates if the viewer panel is focused, and thereby
    frontmost.
    """

    active_view_index: int
    """
    The index of the current active [View][] object, in the `Viewer.views` array.
    """

    type: ViewerType
    """
    The content in the viewer panel.
    """

    views: list[View]
    """All of the [View][] objects associated with this viewer."""
