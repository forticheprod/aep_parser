from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from .project import Project
    from .viewer.viewer import Viewer


@dataclass
class App:
    """
    The `App` object represents the After Effects application. Attributes
    provide access to the project and application-level settings parsed from
    the binary file.

    See: https://ae-scripting.docsforadobe.dev/general/application/
    """

    version: str
    """
    The version of After Effects that last saved the project, formatted as
    "{major}.{minor}x{build}" (e.g., "25.6x101").
    """

    build_number: int
    """
    The build number of After Effects that last saved the project.
    """

    project: Project
    """
    The project that is currently loaded.
    """

    active_viewer: Viewer | None = None
    """
    The Viewer object for the currently focused or active-focused viewer (Composition,
    Layer, or Footage) panel. Returns `None` if no viewers are open.
    """
