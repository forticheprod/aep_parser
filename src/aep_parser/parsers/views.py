from __future__ import annotations

from typing import TYPE_CHECKING

from ..kaitai.utils import (
    ChunkNotFoundError,
    filter_by_type,
    find_by_type,
    group_chunks,
)
from ..models.enums import ChannelType
from ..models.viewer.view import View
from ..models.viewer.view_options import ViewOptions
from ..models.viewer.viewer import Viewer
from .mappings import map_fast_preview_type, map_viewer_type_from_string

if TYPE_CHECKING:
    from ..kaitai import Aep


def _parse_view_options(fips_chunk: Aep.Chunk) -> ViewOptions:
    """Build a ViewOptions instance from a ``fips`` chunk.

    Args:
        fips_chunk: A chunk whose type is ``fips``.
    """
    return ViewOptions(
        channels=ChannelType.from_binary(fips_chunk.channels),
        checkerboards=fips_chunk.transparency_grid,
        draft3d=fips_chunk.draft3d,
        exposure=fips_chunk.exposure,
        fast_preview=map_fast_preview_type(
            adaptive=fips_chunk.fast_preview_adaptive,
            wireframe=fips_chunk.fast_preview_wireframe,
        ),
        grid=fips_chunk.grid,
        guides_visibility=fips_chunk.guides_visibility,
        mask_and_shape_path=fips_chunk.mask_and_shape_path,
        proportional_grid=fips_chunk.proportional_grid,
        region_of_interest=fips_chunk.region_of_interest,
        rulers=fips_chunk.rulers,
        title_action_safe=fips_chunk.title_action_safe,
        use_display_color_management=fips_chunk.use_display_color_management,
        zoom=fips_chunk.zoom,
    )


def parse_viewers(
    root_folder_chunk: Aep.Chunk,
) -> list[Viewer]:
    """Parse viewer panels from the Fold-level chunks.

    The Fold chunk contains a repeating pattern of small metadata chunks
    that describe each viewer panel (Timeline, Composition, Layer, Footage).
    Each panel block is bounded by ``fvdv``  (start) and ``fifl`` (end), and
    may contain ``fips`` chunks that hold the per-view options.

    The ``fitt`` chunk contains the inner tab type label (e.g.
    ``"AE Composition"``) which maps to [ViewerType][aep_parser.models.enums.ViewerType].
    The ``foac`` chunk indicates whether the outer panel is active.

    Args:
        root_folder_chunk: The ``LIST:Fold`` chunk.

    Returns:
        A list of parsed [Viewer][aep_parser.models.viewer.viewer.Viewer] objects.
    """
    blocks = group_chunks(root_folder_chunk.chunks, "fvdv", "fifl")
    viewers = [_build_viewer(block) for block in blocks]
    return [v for v in viewers if v is not None]


def _build_viewer(block: list[Aep.Chunk]) -> Viewer | None:
    """Build a Viewer from a block of Fold-level chunks.

    Args:
        block: The sequence of chunks from ``fvdv`` to ``fifl``.

    Returns:
        A [Viewer][aep_parser.models.viewer.viewer.Viewer] instance, or ``None`` if the
        block does not contain a recognised viewer type.
    """
    try:
        fitt = find_by_type(block, "fitt")
    except ChunkNotFoundError:
        return None

    viewer_type = map_viewer_type_from_string(fitt.label)
    if viewer_type is None:
        return None

    try:
        foac = find_by_type(block, "foac")
    except ChunkNotFoundError:
        foac = None
    try:
        fiac = find_by_type(block, "fiac")
    except ChunkNotFoundError:
        fiac = None
    try:
        fivi = find_by_type(block, "fivi")
    except ChunkNotFoundError:
        fivi = None
    try:
        fivc = find_by_type(block, "fivc")
    except ChunkNotFoundError:
        fivc = None
    fips_chunks = filter_by_type(block, "fips")

    if fivc is not None:
        fips_chunks = fips_chunks[: fivc.view_count]

    views = [View(options=_parse_view_options(fips)) for fips in fips_chunks]

    return Viewer(
        active=bool(foac and foac.active and fiac and fiac.active),
        active_view_index=fivi.active_view_index if fivi else 0,
        type=viewer_type,
        views=views,
    )
