from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TiffFormatOptions:
    """TIFF format-specific render options.

    These settings correspond to the TIFF Options dialog in After Effects,
    accessible when the output format is set to TIFF Sequence.
    """

    lzw_compression: bool
    """Whether LZW compression is enabled."""

    ibm_pc_byte_order: bool
    """Whether IBM PC byte order (little-endian) is used."""
