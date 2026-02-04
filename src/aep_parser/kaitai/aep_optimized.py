"""Optimized Aep class with dict-based chunk type lookup.

This module wraps the auto-generated aep.py and applies performance
optimizations without modifying the generated file. After regenerating
aep.py from aep.ksy, no manual changes are needed.

The optimization replaces the large if/elif chain in Chunk._read()
with a dict lookup for better performance.
"""

from __future__ import annotations

from io import BytesIO

from kaitaistruct import KaitaiStream

# Import the generated Aep class
from .aep import Aep

# Mapping from chunk type to Kaitai struct class for fast lookup
_CHUNK_TYPE_TO_CLASS: dict[str, type] = {
    "alas": Aep.Utf8Body,
    "cdat": Aep.CdatBody,
    "cdta": Aep.CdtaBody,
    "cmta": Aep.Utf8Body,
    "fdta": Aep.FdtaBody,
    "fnam": Aep.ChildUtf8Body,
    "head": Aep.HeadBody,
    "idta": Aep.IdtaBody,
    "ldat": Aep.LdatBody,
    "ldta": Aep.LdtaBody,
    "lhd3": Aep.Lhd3Body,
    "LIST": Aep.ListBody,
    "NmHd": Aep.NmhdBody,
    "nnhd": Aep.NnhdBody,
    "opti": Aep.OptiBody,
    "pard": Aep.PardBody,
    "pdnm": Aep.ChildUtf8Body,
    "pjef": Aep.Utf8Body,
    "sspc": Aep.SspcBody,
    "tdb4": Aep.Tdb4Body,
    "tdmn": Aep.Utf8Body,
    "tdsb": Aep.TdsbBody,
    "tdsn": Aep.ChildUtf8Body,
    "Utf8": Aep.Utf8Body,
}


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
        chunk_class = Aep.AsciiBody

    self.data = chunk_class(_io__raw_data, self, self._root)

    if (self.len_data % 2) != 0:
        self.padding = self._io.read_bytes(1)


def apply_optimizations() -> None:
    """Apply performance optimizations to the Aep class.

    This replaces the Chunk._read method with an optimized version
    that uses dict lookup instead of a large if/elif chain.
    """
    Aep.Chunk._read = _optimized_chunk_read


# Apply optimizations on import
apply_optimizations()

__all__ = ["Aep", "apply_optimizations"]
