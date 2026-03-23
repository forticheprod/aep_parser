from __future__ import annotations

import json
import struct
import typing
from typing import Any, List, TypeVar

from ..kaitai import Aep
from ..kaitai.utils import (
    ChunkNotFoundError,
    find_by_list_type,
    find_by_type,
    str_contents,
)

if typing.TYPE_CHECKING:
    from typing import Iterator

T = TypeVar(
    "T", bytes, List[Any]
)  # Cannot use list here because of py3.7, even with future


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
        for chunk in root_chunk.body.chunks:
            if chunk.chunk_type == "tdmn":
                match_name = str_contents(chunk)
                if match_name == "ADBE Group End":
                    skip_to_next_tdmn_flag = True
                else:
                    skip_to_next_tdmn_flag = False
            elif (
                not skip_to_next_tdmn_flag
            ) and chunk.chunk_type not in SKIP_CHUNK_TYPES:
                chunks_by_match_name.setdefault(match_name, []).append(chunk)
    return chunks_by_match_name


def split_into_batches(iterable: T, n: int) -> Iterator[T]:
    """
    Yield successive n-sized batches from bytes or list.
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
    if property_chunk.body.list_type != "tdbs":
        return False
    for chunk in property_chunk.body.chunks:
        if chunk.chunk_type == "LIST" and chunk.body.list_type == "list":
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
    try:
        als2_chunk = find_by_list_type(chunks=parent_chunks, list_type="Als2")
        alas_chunk = find_by_type(chunks=als2_chunk.body.chunks, chunk_type="alas")
    except ChunkNotFoundError:
        return {}
    alas_text = str_contents(alas_chunk)
    if not alas_text:
        return {}
    result = json.loads(alas_text)
    return result if isinstance(result, dict) else {}


def read_tdum(
    chunks: list[Aep.Chunk],
    chunk_type: str,
    color: bool,
    integer: bool,
    dimensions: int,
) -> Any:
    """Decode a tdum (min) or tduM (max) chunk from a tdbs LIST.

    Returns the decoded scalar/list value, or `None` when the chunk is
    absent.  The binary encoding depends on the property type:

    * Scalar: float64 (8 bytes)
    * Color: float32×4 RGBA (16 bytes)
    * Position: float64×dimensions (16 bytes for 2-D)
    * Vector: float64×dimensions (up to 32 bytes for 4-D)
    * Enum (integer flag): uint32 (4 bytes)
    """
    try:
        chunk = find_by_type(chunks=chunks, chunk_type=chunk_type)
    except ChunkNotFoundError:
        return None
    raw = chunk.body.data
    size = len(raw)
    if color and size == 16:
        return list(struct.unpack(">4f", raw))
    if integer and size == 4:
        return struct.unpack(">I", raw)[0]
    if size == 8:
        return struct.unpack(">d", raw)[0]
    if size == 16:
        return list(struct.unpack(">2d", raw))
    if size == 32:
        return list(struct.unpack(">4d", raw))
    return struct.unpack(">d", raw[:8])[0]
