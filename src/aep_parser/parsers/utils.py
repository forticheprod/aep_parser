from __future__ import annotations

import json
import typing

from ..kaitai.utils import (
    find_by_list_type,
    find_by_type,
    str_contents,
)

if typing.TYPE_CHECKING:
    from typing import Iterator

    from ..kaitai import Aep


def get_name(child_chunks: list[Aep.Chunk]) -> str:
    """Get the name of an item from its child chunks."""
    name_chunk = find_by_type(chunks=child_chunks, chunk_type="Utf8")
    item_name = str_contents(name_chunk)
    return item_name


def get_comment(child_chunks: list[Aep.Chunk]) -> str:
    """Get the comment of an item from its child chunks."""
    cmta_chunk = find_by_type(chunks=child_chunks, chunk_type="cmta")
    if cmta_chunk:
        return str_contents(cmta_chunk)
    return ""


def get_chunks_by_match_name(root_chunk: Aep.Chunk) -> dict[str, list[Aep.Chunk]]:
    """Get chunks grouped by their match name."""
    SKIP_CHUNK_TYPES = (
        "engv",
        "aRbs",
    )
    chunks_by_match_name = {}
    if root_chunk:
        skip_to_next_tdmn_flag = True
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


def split_in_chunks(iterable: list, n: int) -> Iterator[list]:
    """
    Yield successive n-sized chunks from a list.
    NOTE use itertools.batched in py 3.12+
    """
    if n < 1:
        raise ValueError('n must be at least one')
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


def parse_alas_data(parent_chunks: list[Aep.Chunk]) -> dict:
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
    if als2_chunk is None:
        return {}

    alas_chunk = find_by_type(chunks=als2_chunk.chunks, chunk_type="alas")
    if alas_chunk is None:
        return {}

    try:
        alas_text = str_contents(alas_chunk)
        if not alas_text:
            return {}
        return json.loads(alas_text)
    except (json.JSONDecodeError, AttributeError):
        return {}
