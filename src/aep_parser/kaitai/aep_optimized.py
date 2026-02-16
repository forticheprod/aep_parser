"""Optimized Aep class with dict-based chunk type lookup.

This module wraps the auto-generated aep.py and applies performance
optimizations without modifying the generated file. After regenerating
aep.py from aep.ksy, no manual changes are needed.

The optimization replaces the large if/elif chain in Chunk._read()
with a dict lookup for better performance.
"""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from kaitaistruct import KaitaiStream

# Import the generated Aep class
from .aep import Aep


def _build_chunk_type_mapping() -> tuple[dict[str, type], type]:
    """Build chunk type to class mapping by parsing aep.py.

    This function reads the generated aep.py file and extracts the
    chunk_type -> class mapping from the if/elif chain in Chunk._read(),
    as well as the fallback class from the else clause.

    Returns:
        Tuple of (mapping dict, fallback class).
    """
    # Read the aep.py source file
    aep_py_path = Path(__file__).parent / "aep.py"
    source = aep_py_path.read_text(encoding="utf-8")

    # Pattern to match: if/elif _on == u"chunk_type": pass; self._raw_data = ...; _io__raw_data = ...; self.data = Aep.ClassName(
    # This pattern is specific to Chunk._read() method structure to avoid matching other switch-on blocks
    pattern = re.compile(
        r'(?:if|elif) _on == u?"([^"]+)":\s*\n\s*pass\n\s*self\._raw_data = [^\n]+\n\s*_io__raw_data = [^\n]+\n\s*self\.data = Aep\.(\w+)\(',
        re.MULTILINE,
    )

    mapping: dict[str, type] = {}
    for match in pattern.finditer(source):
        chunk_type = match.group(1)
        class_name = match.group(2)
        # Get the class from Aep
        if hasattr(Aep, class_name):
            mapping[chunk_type] = getattr(Aep, class_name)

    # Extract fallback class from else clause
    # Pattern: else:\n                pass\n                self._raw_data = ...\n                ...self.data = Aep.ClassName(
    else_pattern = re.compile(
        r"else:\s*\n\s*pass\n\s*self\._raw_data = [^\n]+\n\s*_io__raw_data = [^\n]+\n\s*self\.data = Aep\.(\w+)\(",
        re.MULTILINE,
    )
    else_match = else_pattern.search(source)
    assert else_match, "Fallback class not found in aep.py"
    fallback_name = else_match.group(1)
    assert hasattr(Aep, fallback_name), (
        f"Fallback class {fallback_name} not found in Aep"
    )
    fallback_class = getattr(Aep, fallback_name)

    return mapping, fallback_class


# Build the mapping and fallback dynamically from aep.py
_CHUNK_TYPE_TO_CLASS, _FALLBACK_CLASS = _build_chunk_type_mapping()


def _optimized_chunk_read(self: Aep.Chunk) -> None:
    """Optimized _read method for Chunk using dict lookup instead of if/elif."""
    self.chunk_type = (self._io.read_bytes(4)).decode("ascii")
    self.len_data = self._io.read_u4be()
    self._raw_data = self._io.read_bytes(
        (self._io.size() - self._io.pos())
        if self.len_data > (self._io.size() - self._io.pos())
        else self.len_data
    )
    _io__raw_data = KaitaiStream(BytesIO(self._raw_data))

    # Use dict lookup instead of if/elif chain
    try:
        chunk_class = _CHUNK_TYPE_TO_CLASS[self.chunk_type]
    except KeyError:
        chunk_class = _FALLBACK_CLASS
    self.data = chunk_class(_io__raw_data, self, self._root)

    if (self.len_data % 2) != 0:
        self.padding = self._io.read_bytes(1)


def _chunk_getattr(self: Aep.Chunk, name: str) -> object:
    """Delegate attribute access to chunk.data if not found on chunk itself.

    This allows writing `chunk.list_type` instead of `chunk.data.list_type`,
    and works for any attribute on any chunk data type.
    """
    # Avoid infinite recursion - only delegate if we have data
    try:
        data = object.__getattribute__(self, "data")
    except AttributeError:
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        ) from None

    if data is not None and hasattr(data, name):
        return getattr(data, name)

    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


def apply_optimizations() -> None:
    """Apply performance optimizations to the Aep class.

    This replaces the Chunk._read method with an optimized version
    that uses dict lookup instead of a large if/elif chain.

    It also adds __getattr__ to Chunk for transparent attribute delegation
    to chunk.data, allowing `chunk.list_type` instead of `chunk.data.list_type`.
    """
    Aep.Chunk._read = _optimized_chunk_read
    Aep.Chunk.__getattr__ = _chunk_getattr


# Apply optimizations on import
apply_optimizations()

__all__ = ["Aep", "apply_optimizations"]
