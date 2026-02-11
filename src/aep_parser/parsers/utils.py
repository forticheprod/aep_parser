from __future__ import annotations

import json
import typing
from io import BytesIO
from typing import Any, List, TypeVar

from kaitaistruct import KaitaiStream

from ..kaitai import Aep
from ..kaitai.utils import (
    ChunkNotFoundError,
    find_by_list_type,
    find_by_type,
    str_contents,
)

if typing.TYPE_CHECKING:
    from typing import Iterator

T = TypeVar("T", bytes, List[Any])


def get_name(child_chunks: list[Aep.Chunk]) -> str:
    """Get the name of an item from its child chunks."""
    name_chunk = find_by_type(chunks=child_chunks, chunk_type="Utf8")
    item_name = str_contents(name_chunk)
    return item_name


def get_comment(child_chunks: list[Aep.Chunk]) -> str:
    """Get the comment of an item from its child chunks."""
    try:
        cmta_chunk = find_by_type(chunks=child_chunks, chunk_type="cmta")
        return str_contents(cmta_chunk)
    except ChunkNotFoundError:
        return ""


def get_chunks_by_match_name(
    root_chunk: Aep.Chunk,
) -> dict[str, list[Aep.Chunk]]:
    """Get chunks grouped by their match name."""
    SKIP_CHUNK_TYPES = (
        "engv",
        "aRbs",
    )
    chunks_by_match_name: dict[str, list[Aep.Chunk]] = {}
    if root_chunk:
        skip_to_next_tdmn_flag = True
        match_name = ""
        for chunk in root_chunk.chunks:
            if chunk.chunk_type == "tdmn":
                match_name = str_contents(chunk)
                if match_name in ("ADBE Group End", "ADBE Effect Built In Params"):
                    skip_to_next_tdmn_flag = True
                else:
                    skip_to_next_tdmn_flag = False
            elif (
                not skip_to_next_tdmn_flag
            ) and chunk.chunk_type not in SKIP_CHUNK_TYPES:
                chunks_by_match_name.setdefault(match_name, []).append(chunk)
    return chunks_by_match_name


def split_in_chunks(iterable: T, n: int) -> Iterator[T]:
    """
    Yield successive n-sized chunks from bytes or list.
    NOTE use itertools.batched in py 3.12+
    """
    if n < 1:
        raise ValueError("n must be at least one")
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]


def property_has_keyframes(property_chunk: Aep.Chunk) -> bool:
    """
    Check if a property has keyframes.

    A property with keyframes contains a LIST/list chunk with lhd3/ldat.
    A property without keyframes contains a cdat chunk (constant data).

    Args:
        property_chunk: The property's tdbs LIST chunk.
    """
    if property_chunk.chunk_type != "LIST":
        return False
    if property_chunk.list_type != "tdbs":
        return False
    for chunk in property_chunk.chunks:
        if chunk.chunk_type == "LIST" and chunk.list_type == "list":
            return True  # Has keyframes
    return False  # Has cdat (constant) or other structure


def parse_alas_data(parent_chunks: list[Aep.Chunk]) -> dict[str, Any]:
    """Parse path information from an Als2/alas chunk structure.

    The Als2 LIST chunk contains an alas chunk with JSON data including:
    - fullpath: The folder or file path
    - target_is_folder: Whether fullpath is a folder (`True`) or file (`False`)

    Args:
        parent_chunks: List of chunks that may contain an Als2 LIST chunk.

    Returns:
        Dictionary with alas data (fullpath, target_is_folder, etc.),
        or empty dict if not found or invalid.
    """
    als2_chunk = find_by_list_type(chunks=parent_chunks, list_type="Als2")
    alas_chunk = find_by_type(chunks=als2_chunk.chunks, chunk_type="alas")
    alas_text = str_contents(alas_chunk)
    if not alas_text:
        return {}
    result = json.loads(alas_text)
    return result if isinstance(result, dict) else {}


def parse_ldat_items(
    list_chunk: Aep.Chunk,
    is_spatial: bool = False,
) -> list:
    """Parse items from a LIST chunk containing lhd3 and ldat.

    Uses lhd3.item_type to determine the correct parser class:
    - lrdr: RenderSettingsLdatBody (2246 bytes per item)
    - litm: OutputModuleSettingsLdatBody (128 bytes per item)
    - keyframe types: LdatItem (variable size per item)

    Args:
        list_chunk: A LIST chunk containing lhd3 and ldat child chunks.
        is_spatial: Whether the property is spatial (affects 3D type interpretation
            for keyframe items).

    Returns:
        List of parsed items (type depends on item_type).
    """
    lhd3 = find_by_type(chunks=list_chunk.chunks, chunk_type="lhd3")
    ldat = find_by_type(chunks=list_chunk.chunks, chunk_type="ldat")

    count = lhd3.count
    if not count:
        return []

    item_size = lhd3.item_size
    item_type = lhd3.item_type

    # Adjust type for spatial 3D properties
    if item_type == Aep.LdatItemType.three_d and is_spatial:
        item_type = Aep.LdatItemType.three_d_spatial

    items = []
    for item_bytes in split_in_chunks(ldat.items, item_size):
        stream = KaitaiStream(BytesIO(item_bytes))
        if item_type == Aep.LdatItemType.lrdr:
            item = Aep.RenderSettingsLdatBody(stream)
        elif item_type == Aep.LdatItemType.litm:
            item = Aep.OutputModuleSettingsLdatBody(stream)
        else:
            item = Aep.LdatItem(item_type=item_type, _io=stream)
        items.append(item)

    return items
