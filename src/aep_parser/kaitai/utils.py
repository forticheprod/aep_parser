from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from enum import Enum
    from typing import Callable

    from .aep import Aep


def get_enum_value(value: Enum | int) -> int:
    """Extract integer value from either an enum or raw int.

    Kaitai's resolve_enum returns the enum member if the value exists,
    or the raw integer if the value is not in the enum. This helper
    handles both cases safely.

    Args:
        value: Either a Kaitai enum member or a raw integer.

    Returns:
        The integer value.
    """
    if hasattr(value, "value"):
        return value.value
    return value


def _find_chunk(
    chunks: list[Aep.Chunk], func: Callable[[Aep.Chunk], bool]
) -> Aep.Chunk | None:
    """Perform a basic find operation over a chunks list."""
    for chunk in chunks:
        if func(chunk):
            return chunk


def find_by_type(chunks: list[Aep.Chunk], chunk_type: str) -> Aep.Chunk | None:
    """Return first chunk that has the provided chunk_type."""
    return _find_chunk(chunks=chunks, func=lambda chunk: chunk.chunk_type == chunk_type)


def find_by_list_type(chunks: list[Aep.Chunk], list_type: str) -> Aep.Chunk | None:
    """Return first LIST chunk that has the provided list_type."""
    return _find_chunk(
        chunks=chunks,
        func=lambda chunk: (
            chunk.chunk_type == "LIST" and chunk.data.list_type == list_type
        ),
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
            chunk.chunk_type == "LIST" and chunk.data.list_type == list_type
        ),
    )


def filter_by_type(chunks: list[Aep.Chunk], chunk_type: str) -> list[Aep.Chunk]:
    """Return chunks that have the provided chunk_type."""
    return _filter_chunks(
        chunks=chunks, func=lambda chunk: (chunk.chunk_type == chunk_type)
    )


def str_contents(chunk: Aep.Chunk) -> str:
    """Return the string contents of a chunk whose chunk_type is Utf8."""
    text = str(chunk.data.data)
    return text.rstrip("\x00")
