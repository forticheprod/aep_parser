from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TargaFormatOptions:
    """Targa (TGA) format-specific render options.

    These settings correspond to the Targa Options dialog in After Effects,
    accessible when the output format is set to Targa Sequence.

    Example:
        ```python
        import aep_parser
        from aep_parser.models.renderqueue.format_options.targa import (
            TargaFormatOptions,
        )

        app = aep_parser.parse("project.aep")
        om = app.project.render_queue.items[0].output_modules[0]
        if isinstance(om.format_options, TargaFormatOptions):
            print(om.format_options.bits_per_pixel)
        ```
    """

    bits_per_pixel: int
    """Color depth in bits per pixel (24 or 32)."""

    rle_compression: bool
    """Whether RLE compression is enabled."""
