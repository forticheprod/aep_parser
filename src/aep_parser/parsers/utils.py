# coding: utf-8
from __future__ import (
    absolute_import,
    unicode_literals,
    division
)
import collections

from ..kaitai.utils import (
    find_by_type,
    str_contents,
)


def get_name(child_chunks):
    """
    Args:
        child_chunks (list): The child chunks of the item.
    Returns:
        str: The name of the item.
    """
    name_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="Utf8"
    )
    item_name = str_contents(name_chunk)
    return item_name


def get_comment(child_chunks):
    """
    Args:
        child_chunks (list): The child chunks of the item.
    Returns:
        str: The comment of the item.
    """
    cmta_chunk = find_by_type(
        chunks=child_chunks,
        chunk_type="cmta"
    )
    if cmta_chunk:
        return str_contents(cmta_chunk)
    return ""


def get_chunks_by_match_name(root_chunk):
    """
    Args:
        root_chunk (Aep.Chunk): The LIST chunk to parse.
    Returns:
        dict: The chunks, grouped by their match name.
    """
    SKIP_CHUNK_TYPES = (
        "engv",
        "aRbs",
    )
    chunks_by_match_name = collections.OrderedDict()
    if root_chunk:
        skip_to_next_tdmn_flag = True
        for chunk in root_chunk.data.chunks:
            if chunk.chunk_type == "tdmn":
                match_name = str_contents(chunk)
                if match_name in ("ADBE Group End", "ADBE Effect Built In Params"):
                    skip_to_next_tdmn_flag = True
                else:
                    skip_to_next_tdmn_flag = False
            elif (not skip_to_next_tdmn_flag) and chunk.chunk_type not in SKIP_CHUNK_TYPES:
                chunks_by_match_name.setdefault(match_name, []).append(chunk)
    return chunks_by_match_name


def split_in_chunks(iterable, n):
    """
    Yield successive n-sized chunks from lst.
    Args:
        iterable (list): The list to chunk.
        n (int): The size of the chunks.
    Returns:
        list: The chunks.
    """
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]
