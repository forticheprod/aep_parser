from __future__ import annotations

from ..kaitai import Aep
from ..kaitai.utils import str_contents


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
