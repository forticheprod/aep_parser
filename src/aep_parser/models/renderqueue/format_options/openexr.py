from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aep_parser.enums import OpenExrCompression


@dataclass
class OpenExrFormatOptions:
    """OpenEXR format-specific render options.

    These settings correspond to the OpenEXR Options dialog in After Effects,
    accessible when the output format is set to OpenEXR or OpenEXR Sequence.
    """

    compression: OpenExrCompression
    """
    The compression method. Corresponds to the ``Compression`` dropdown
    in the OpenEXR Options dialog.
    """

    luminance_chroma: bool
    """
    Whether Luminance/Chroma encoding is enabled. Corresponds to the
    ``Luminance/Chroma`` checkbox in the OpenEXR Options dialog.
    Not applicable when compression is DWAA or DWAB.
    """

    thirty_two_bit_float: bool
    """
    Whether 32-bit float output is used instead of the default 16-bit
    half float. Corresponds to the ``32-bit float (not recommended)``
    checkbox in the OpenEXR Options dialog.
    """

    dwa_compression_level: float | None
    """
    The DWA compression level. Only meaningful when ``compression`` is
    ``OpenExrCompression.DWAA`` or ``OpenExrCompression.DWAB``.
    Stored as a little-endian ``f4`` in the Ropt body. Defaults to
    ``45.0`` in After Effects.
    """
