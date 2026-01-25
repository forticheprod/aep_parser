from __future__ import annotations

import typing

from ..kaitai.utils import (
    find_by_type,
    str_contents,
)

if typing.TYPE_CHECKING:
    from typing import Iterator

    from ..kaitai.aep import Aep


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
        for chunk in root_chunk.data.chunks:
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
