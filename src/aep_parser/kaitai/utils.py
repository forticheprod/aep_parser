from __future__ import absolute_import
from __future__ import unicode_literals


def find_chunk(chunks, func):
    """
    Perform a basic find operation over a chunks list.
    """
    for chunk in chunks:
        if func(chunk):
            return chunk


def find_by_type(chunks, chunk_type):
    """
    Perform a find operation over a chunks list predicated upon chunk type.
    """
    return find_chunk(
        chunks=chunks,
        func=lambda chunk: chunk.chunk_type == chunk_type
    )


def find_by_list_type(chunks, list_type):
    """
    Perform a find operation over a chunks list predicated upon chunk type.
    """
    return find_chunk(
        chunks=chunks,
        func=lambda chunk: (
            chunk.chunk_type == "LIST"
            and chunk.data.list_type == list_type
        )
    )

def filter_chunks(chunks, func):
    """
    Perform a basic filter operation over a chunks list.
    """
    return list(filter(func, chunks))


def filter_by_list_type(chunks, list_type):
    """
    Return chunks that have the provided list_type.
    """
    return filter_chunks(
        chunks=chunks,
        func=lambda chunk: (
            chunk.chunk_type == "LIST"
            and chunk.data.list_type == list_type
        )
    )


def filter_by_type(chunks, chunk_type):
    """
    Return chunks that have the provided chunk type.
    """
    return filter_chunks(
        chunks=chunks,
        func=lambda chunk: (
            chunk.chunk_type == chunk_type
        )
    )

def str_contents(chunk):
    text = str(chunk.data.data)
    return text.rstrip("\x00")
