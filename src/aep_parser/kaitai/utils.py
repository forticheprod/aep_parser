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


def find_chunks_before(
    chunks: list[Aep.Chunk],
    chunk_type: str,
    before_type: str,
) -> list[Aep.Chunk]:
    """Return consecutive chunks of ``chunk_type`` immediately before ``before_type``.

    Scans *chunks* for the first occurrence of *before_type*, then collects the
    uninterrupted run of *chunk_type* chunks that directly precede it.

    Args:
        chunks: List of chunks to search.
        chunk_type: The type of chunks to collect.
        before_type: The anchor chunk type that follows the desired run.

    Raises:
        ChunkNotFoundError: If no chunk with *before_type* is found.
    """
    anchor_index = None
    for i, chunk in enumerate(chunks):
        if chunk.chunk_type == before_type:
            anchor_index = i
            break
    if anchor_index is None:
        raise ChunkNotFoundError(f"Missing {before_type} chunk")

    result: list[Aep.Chunk] = []
    for i in range(anchor_index - 1, -1, -1):
        if chunks[i].chunk_type == chunk_type:
            result.insert(0, chunks[i])
        else:
            break
    return result


def group_chunks(
    chunks: list[Aep.Chunk],
    start_type: str,
    end_type: str,
) -> list[list[Aep.Chunk]]:
    """Split *chunks* into groups bounded by *start_type* … *end_type* (inclusive).

    Chunks that fall outside any group are ignored.

    Args:
        chunks: Flat list of chunks to scan.
        start_type: Chunk type that begins a new group.
        end_type: Chunk type that closes the current group.
    """
    groups: list[list[Aep.Chunk]] = []
    current: list[Aep.Chunk] | None = None
    for chunk in chunks:
        if chunk.chunk_type == start_type and current is None:
            current = [chunk]
        elif current is not None:
            current.append(chunk)
            if chunk.chunk_type == end_type:
                groups.append(current)
                current = None
    return groups


def split_on_type(
    chunks: list[Aep.Chunk],
    chunk_type: str,
) -> list[list[Aep.Chunk]]:
    """Split *chunks* into groups starting at each occurrence of *chunk_type*.

    Every time a chunk with *chunk_type* is encountered a new group begins.
    Chunks that appear before the first occurrence are discarded.

    Args:
        chunks: Flat list of chunks to scan.
        chunk_type: Chunk type that starts a new group.
    """
    groups: list[list[Aep.Chunk]] = []
    current: list[Aep.Chunk] | None = None
    for chunk in chunks:
        if chunk.chunk_type == chunk_type:
            if current is not None:
                groups.append(current)
            current = [chunk]
        elif current is not None:
            current.append(chunk)
    if current is not None:
        groups.append(current)
    return groups


def str_contents(chunk: Aep.Chunk) -> str:
    """Return the string contents of a chunk whose chunk_type is Utf8."""
    text: str = chunk.contents
    return text.rstrip("\x00")
