from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing import Callable

    from .aep_optimized import Aep


class ChunkNotFoundError(Exception):
    """Raised when a required chunk is not found in the AEP file structure."""

    pass


def _find_chunk(
    chunks: list[Aep.Chunk], func: Callable[[Aep.Chunk], bool], description: str
) -> Aep.Chunk:
    """Perform a basic find operation over a chunks list.

    Args:
        chunks: List of chunks to search.
        func: Predicate function to match chunks.
        description: Human-readable description for error message.

    Raises:
        ChunkNotFoundError: If no matching chunk is found.
    """
    for chunk in chunks:
        if func(chunk):
            return chunk
    raise ChunkNotFoundError(f"Missing {description}")


def find_by_type(chunks: list[Aep.Chunk], chunk_type: str) -> Aep.Chunk:
    """Return first chunk that has the provided chunk_type.

    Raises:
        ChunkNotFoundError: If no chunk with the given type is found.
    """
    return _find_chunk(
        chunks=chunks,
        func=lambda chunk: chunk.chunk_type == chunk_type,
        description=f"{chunk_type} chunk",
    )


def find_by_list_type(chunks: list[Aep.Chunk], list_type: str) -> Aep.Chunk:
    """Return first LIST chunk that has the provided list_type.

    Raises:
        ChunkNotFoundError: If no LIST chunk with the given list_type is found.
    """
    return _find_chunk(
        chunks=chunks,
        func=lambda chunk: (
            chunk.chunk_type == "LIST" and chunk.list_type == list_type
        ),
        description=f"LIST/{list_type} chunk",
    )


def _filter_chunks(
    chunks: list[Aep.Chunk], func: Callable[[Aep.Chunk], bool]
) -> list[Aep.Chunk]:
    """Perform a basic filter operation over a chunks list."""
    return list(filter(func, chunks))


def filter_by_list_type(chunks: list[Aep.Chunk], list_type: str) -> list[Aep.Chunk]:
    """Return LIST chunks that have the provided list_type."""
    return _filter_chunks(
        chunks=chunks,
        func=lambda chunk: (
            chunk.chunk_type == "LIST" and chunk.list_type == list_type
        ),
    )


def filter_by_type(chunks: list[Aep.Chunk], chunk_type: str) -> list[Aep.Chunk]:
    """Return chunks that have the provided chunk_type."""
    return _filter_chunks(
        chunks=chunks, func=lambda chunk: (chunk.chunk_type == chunk_type)
    )


def str_contents(chunk: Aep.Chunk) -> str:
    """Return the string contents of a chunk whose chunk_type is Utf8."""
    text = str(chunk.contents)
    return text.rstrip("\x00")
