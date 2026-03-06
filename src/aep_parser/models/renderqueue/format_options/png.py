from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aep_parser.enums import Hdr10ColorPrimaries, PngCompression


@dataclass
class PngFormatOptions:
    """PNG format-specific render options.

    These settings correspond to the PNG Options dialog in After Effects,
    accessible when the output format is set to PNG Sequence.

    The Ropt body for PNG contains a fixed-size binary block (typically 318
    bytes) with width, height, and bit depth at known offsets. HDR10 metadata
    is stored separately in a JSON ``Utf8`` chunk alongside the Ropt chunk.

    Example:
        ```python
        import aep_parser
        from aep_parser.models.renderqueue.format_options.png import (
            PngFormatOptions,
        )

        app = aep_parser.parse("project.aep")
        om = app.project.render_queue.items[0].output_modules[0]
        if isinstance(om.format_options, PngFormatOptions):
            print(om.format_options.compression)
        ```
    """

    width: int
    """The output width in pixels (big-endian ``u4`` at offset 14)."""

    height: int
    """The output height in pixels (big-endian ``u4`` at offset 18)."""

    bit_depth: int
    """
    The output bit depth per channel (big-endian ``u2`` at offset 24).
    Common values are ``8`` and ``16``.
    """

    compression: PngCompression
    """
    The PNG compression / interlace mode. Corresponds to the
    ``Compression`` dropdown in the PNG Options dialog.
    """

    include_hdr10_metadata: bool
    """
    Whether HDR10 metadata is embedded in the PNG output.
    Corresponds to the ``Include HDR10 Metadata`` checkbox in the PNG
    Options dialog. Only available for 16-bit output.
    """

    color_primaries: Hdr10ColorPrimaries
    """
    The color primaries used for HDR10 metadata. Corresponds to the
    ``Color Primaries`` dropdown in the PNG Options dialog.
    Only meaningful when ``include_hdr10_metadata`` is ``True``.
    """

    luminance_min: float | None
    """
    The minimum display luminance in nits for HDR10 metadata, or
    ``None`` if not explicitly set. Corresponds to the
    ``Luminance Minimum`` field in the PNG Options dialog.
    """

    luminance_max: float | None
    """
    The maximum display luminance in nits for HDR10 metadata, or
    ``None`` if not explicitly set. Corresponds to the
    ``Luminance Maximum`` field in the PNG Options dialog.
    """

    content_light_max: float | None
    """
    The maximum content light level in nits for HDR10 metadata, or
    ``None`` if not explicitly set. Corresponds to the
    ``Content Light Maximum`` field in the PNG Options dialog.
    """

    content_light_average: float | None
    """
    The maximum frame average light level in nits for HDR10 metadata,
    or ``None`` if not explicitly set. Corresponds to the
    ``Content Light Average`` field in the PNG Options dialog.
    """
