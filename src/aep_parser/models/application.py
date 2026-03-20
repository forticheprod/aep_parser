from __future__ import annotations

import re
import typing
from typing import Any

from ..descriptors import ChunkField, ChunkInstanceField

if typing.TYPE_CHECKING:
    from ..kaitai.aep import Aep  # type: ignore[attr-defined]
    from .project import Project
    from .viewer.viewer import Viewer

_VERSION_RE = re.compile(r"^(\d+)\.(\d+)x(\d+)$")


def _reverse_version(value: str, body: Any) -> dict[str, Any]:
    """Parse ``"major.minorxbuild"`` back into seq fields."""
    m = _VERSION_RE.match(value)
    if not m:
        msg = (
            f"version must match '{{major}}.{{minor}}x{{build}}' "
            f"(e.g. '25.6x101'), got {value!r}"
        )
        raise ValueError(msg)
    major, minor, build = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return {
        "ae_version_major_a": major // 8,
        "ae_version_major_b": major % 8,
        "ae_version_minor": minor,
        "ae_build_number": build,
    }


class Application:
    """
    The `Application` object represents the After Effects application. Attributes
    provide access to the project and application-level settings parsed from
    the binary file.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        print(app.version)
        ```

    See: https://ae-scripting.docsforadobe.dev/general/application/
    """

    # ---- Chunk-backed descriptors (head) ----

    build_number = ChunkField[str](
        "_head",
        "ae_build_number",
        reverse=int,
        invalidates=["version"],
    )
    """The build number of After Effects that last saved the project.
    Read / Write.

    Warning:
        This attribute is read-only in ExtendScript. Modifying it could
        cause issues when opening the file in After Effects.
    """

    version = ChunkInstanceField[str](
        "_head",
        "version",
        reverse=_reverse_version,
        invalidates=["ae_version_major", "version"],
    )
    """The version of After Effects that last saved the project, formatted as
    "{major}.{minor}x{build}" (e.g., "25.6x101"). Read / Write.

    Warning:
        This attribute is read-only in ExtendScript. Modifying it could
        cause issues when opening the file in After Effects.
    """

    # ---- Regular attributes set in __init__ ----

    project: Project
    """The project that is currently loaded."""

    active_viewer: Viewer | None
    """
    The Viewer object for the currently focused or active-focused viewer (Composition,
    Layer, or Footage) panel. Returns `None` if no viewers are open.
    """

    def __init__(
        self,
        *,
        _head: Aep.HeadBody,
        project: Project,
        active_viewer: Viewer | None = None,
    ) -> None:
        self._head = _head
        self.project = project
        self.active_viewer = active_viewer

    def __repr__(self) -> str:
        return (
            f"Application(version={self.version!r}, build_number={self.build_number!r})"
        )
