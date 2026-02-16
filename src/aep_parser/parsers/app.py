"""Main entry point for parsing After Effects project files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
)
from ..models.app import App
from ..models.project import Project
from .views import parse_viewers

if TYPE_CHECKING:
    from ..kaitai import Aep


def parse_app(aep: Aep, project: Project) -> App:
    """Build an [App][] from the parsed RIFX data and project.

    Args:
        aep: The parsed Kaitai RIFX structure.
        project: The already-parsed [Project][].
    """
    root_chunks = aep.data.chunks
    root_folder_chunk = find_by_list_type(chunks=root_chunks, list_type="Fold")
    head_chunk = find_by_type(chunks=root_chunks, chunk_type="head")

    # Parse version from binary header
    # Format: {major}.{minor}x{build}
    version = (
        f"{head_chunk.ae_version_major}."
        f"{head_chunk.ae_version_minor}x"
        f"{head_chunk.ae_build_number}"
    )
    build_number = head_chunk.ae_build_number

    # Parse viewer panels from Fold-level chunks
    viewers = parse_viewers(root_folder_chunk)
    active_viewers = [v for v in viewers if v.active]
    active_viewer = active_viewers[0] if active_viewers else None

    return App(
        version=version,
        build_number=build_number,
        project=project,
        active_viewer=active_viewer,
    )
