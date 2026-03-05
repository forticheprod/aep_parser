from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TargaFormatOptions:
    """Targa (TGA) format-specific render options.

    These settings correspond to the Targa Options dialog in After Effects,
    accessible when the output format is set to Targa Sequence.
    """

    bits_per_pixel: int
    """Color depth in bits per pixel (24 or 32)."""

    rle_compression: bool
    """Whether RLE compression is enabled."""
