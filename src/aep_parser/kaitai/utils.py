from __future__ import absolute_import, unicode_literals, division
from builtins import str


def _find_chunk(chunks, func):
    """
    Perform a basic find operation over a chunks list.
    """
    for chunk in chunks:
        if func(chunk):
            return chunk


def find_by_type(chunks, chunk_type):
    """
    Return first chunk that has the provided chunk_type.
    """
    return _find_chunk(chunks=chunks, func=lambda chunk: chunk.chunk_type == chunk_type)


def find_by_list_type(chunks, list_type):
    """
    Return first LIST chunk that has the provided list_type.
    """
    return _find_chunk(
        chunks=chunks,
        func=lambda chunk: (
            chunk.chunk_type == "LIST" and chunk.data.list_type == list_type
        ),
    )


def _filter_chunks(chunks, func):
    """
    Perform a basic filter operation over a chunks list.
    """
    return list(filter(func, chunks))


def filter_by_list_type(chunks, list_type):
    """
    Return LIST chunks that have the provided list_type.
    """
    return _filter_chunks(
        chunks=chunks,
        func=lambda chunk: (
            chunk.chunk_type == "LIST" and chunk.data.list_type == list_type
        ),
    )


def filter_by_type(chunks, chunk_type):
    """
    Return chunks that have the provided chunk_type.
    """
    return _filter_chunks(
        chunks=chunks, func=lambda chunk: (chunk.chunk_type == chunk_type)
    )


def str_contents(chunk):
    """
    Return the string contents of a chunk whose chunk_type is Utf8.
    """
    text = str(chunk.data.data)
    return text.rstrip("\x00")
