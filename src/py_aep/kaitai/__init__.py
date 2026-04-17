"""Kaitai Struct parser for AEP file format."""

from . import patches as patches  # noqa: F401  # monkey-patch body classes
from .aep import Aep as Aep  # type: ignore[attr-defined]
from .utils import (
    ChunkNotFoundError,
    filter_by_list_type,
    filter_by_type,
    find_by_list_type,
    find_by_type,
    str_contents,
)

__all__ = [
    "Aep",
    "ChunkNotFoundError",
    "filter_by_list_type",
    "filter_by_type",
    "find_by_list_type",
    "find_by_type",
    "str_contents",
]
