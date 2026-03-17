from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from aep_parser.enums import ViewerType

    from .view import View


@dataclass
class Viewer:
    """
    The `Viewer` object represents a Composition, Layer, or Footage panel.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        viewer = app.active_viewer
        print(viewer.type)
        ```

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
