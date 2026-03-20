from __future__ import annotations

import typing
from io import BytesIO
from typing import Any

from kaitaistruct import KaitaiStream

from .aep_optimized import Aep

if typing.TYPE_CHECKING:
    from typing import Callable


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
            chunk.chunk_type == "LIST" and chunk.data.list_type == list_type
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
            chunk.chunk_type == "LIST" and chunk.data.list_type == list_type
        ),
    )


def filter_by_type(chunks: list[Aep.Chunk], chunk_type: str) -> list[Aep.Chunk]:
    """Return chunks that have the provided chunk_type."""
    return _filter_chunks(
        chunks=chunks, func=lambda chunk: chunk.chunk_type == chunk_type
    )


def find_chunks_before(
    chunks: list[Aep.Chunk],
    chunk_type: str,
    before_type: str,
) -> list[Aep.Chunk]:
    """Return consecutive chunks of `chunk_type` immediately before `before_type`.

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
    text: str = chunk.data.contents
    return text.rstrip("\x00")


def chunk_tree(
    chunks: list[Aep.Chunk],
    depth: int = -1,
    indent: int = 0,
) -> str:
    """Return a text tree representation of chunks for debugging.

    Args:
        chunks: List of chunks to visualize.
        depth: Max depth to recurse (-1 for unlimited).
        indent: Current indentation level (used internally).

    Example::

        >>> print(chunk_tree(root.chunks, depth=2))
        LIST:Fold (12345 B)
          tdsn (4 B)
          Utf8 (12 B)
          LIST:Layr (8000 B)
            ...
    """
    lines: list[str] = []
    prefix = "  " * indent
    for chunk in chunks:
        if chunk.chunk_type == "LIST":
            label = f"LIST:{chunk.data.list_type}"
            lines.append(f"{prefix}{label} ({chunk.len_data} B)")
            if depth != 0 and hasattr(chunk.data, "chunks"):
                lines.append(chunk_tree(chunk.data.chunks, depth - 1, indent + 1))
        else:
            lines.append(f"{prefix}{chunk.chunk_type} ({chunk.len_data} B)")
    return "\n".join(lines)


def recursive_find(
    chunks: list[Aep.Chunk],
    chunk_type: str | None = None,
    list_type: str | None = None,
) -> list[Aep.Chunk]:
    """Recursively search the chunk tree for matching chunks.

    At least one of *chunk_type* or *list_type* must be given.

    Args:
        chunks: List of chunks to search.
        chunk_type: Match chunks with this chunk_type (e.g. `"cdta"`).
        list_type: Match LIST chunks with this list_type (e.g. `"Layr"`).
            When provided, only LIST chunks are matched.

    Returns:
        All matching chunks across the entire tree, in DFS order.
    """
    if chunk_type is None and list_type is None:
        raise ValueError("At least one of chunk_type or list_type is required")
    results: list[Aep.Chunk] = []
    for chunk in chunks:
        if list_type is not None:
            if chunk.chunk_type == "LIST" and chunk.data.list_type == list_type:
                results.append(chunk)
        elif chunk.chunk_type == chunk_type:
            results.append(chunk)
        # Recurse into LIST children
        if chunk.chunk_type == "LIST" and hasattr(chunk.data, "chunks"):
            results.extend(recursive_find(chunk.data.chunks, chunk_type, list_type))
    return results


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

# Each chunk starts with a 4-byte type identifier and a 4-byte length field.
CHUNK_HEADER_SIZE = 8


def compute_body_size(body: Any) -> int:
    """Return the serialized byte size of a Kaitai Chunk body.

    The body must not be dirty - call `body._check()` first. `KaitaiStream`
    requires a pre-allocated buffer so we size it from the chunk's `len_data`
    with arbitrary headroom for growth, then write the body to it and check
    the final position for size.
    """
    saved_io = body._io
    current = getattr(body._parent, "len_data", 0)
    buf = BytesIO(bytearray(current + 4096))
    body._write__seq(KaitaiStream(buf))
    size = buf.tell()
    body._io = saved_io
    return size


def _update_len_chain(start: Any, delta: int) -> None:
    """Walk up from *start*, adding *delta* to each ``len_data`` and calling ``_check()``."""
    obj: Any = start
    while obj is not None:
        if hasattr(obj, "len_data"):
            obj.len_data += delta
            if hasattr(obj, "_check"):
                obj._check()
        obj = getattr(obj, "_parent", None)


def propagate_check(body: Any) -> None:
    """Call `_check()` bottom-up from `body` to root, updating `len_data`.

    1. `body._check()` clears the body's `_dirty` flag.
    2. We compute the body's new serialized size.
    3. If the size changed, the delta is added to every ancestor `len_data`
       (Chunk and root Aep) and `_check()` is called on every object up to the
       root so no `ConsistencyNotCheckedError` is raised during `save()`.
    """
    body._check()

    chunk = getattr(body, "_parent", None)
    if chunk is None:
        return

    delta = compute_body_size(body) - chunk.len_data
    if not delta:
        return

    _update_len_chain(chunk, delta)


def create_chunk(
    parent: Any,
    root: Any,
    chunk_type: str,
    body: Any,
    raw_data: bytes,
) -> Any:
    """Create a new Kaitai Chunk wired into the parent/root tree.

    Args:
        parent: The Chunks container that will hold this chunk.
        root: The root Aep object.
        chunk_type: 4-character chunk type identifier (e.g. ``"lnrb"``).
        body: A pre-built Kaitai body instance.
        raw_data: The raw bytes that represent the body.
    """
    chunk = Aep.Chunk()
    chunk.chunk_type = chunk_type
    chunk.len_data = len(raw_data)
    chunk._raw_data = raw_data
    chunk.padding = b"\x00" if len(raw_data) % 2 else b""
    chunk.data = body

    body._parent = chunk
    body._root = root
    chunk._parent = parent
    chunk._root = root

    body._check()
    chunk._check()
    return chunk


def create_flag_chunk(aep: Any, chunk_type: str, body_cls_name: str) -> Any:
    """Create a new 1-byte flag chunk ready for insertion into root chunks.

    The body type is expected to have a single anonymous ``contents`` field.
    """
    from .aep import Aep as Aep  # type: ignore[attr-defined]

    raw_data = b"\x01"
    body_cls = getattr(Aep, body_cls_name)
    body = body_cls()
    body._unnamed0 = raw_data
    body._dirty = False

    return create_chunk(
        parent=aep.data,
        root=aep,
        chunk_type=chunk_type,
        body=body,
        raw_data=raw_data,
    )


def toggle_flag_chunk(
    aep: Any, chunk_type: str, body_cls_name: str, enable: bool
) -> None:
    """Add or remove a flag chunk from the root chunk list."""
    chunks = aep.data.chunks
    existing = [i for i, c in enumerate(chunks) if c.chunk_type == chunk_type]

    if enable and not existing:
        chunk = create_flag_chunk(aep, chunk_type, body_cls_name)
        chunks.append(chunk)
        delta = CHUNK_HEADER_SIZE + chunk.len_data + len(chunk.padding)
    elif not enable and existing:
        delta = 0
        for i in reversed(existing):
            c = chunks.pop(i)
            delta -= CHUNK_HEADER_SIZE + c.len_data + len(c.padding)
    _update_len_chain(aep, delta)
