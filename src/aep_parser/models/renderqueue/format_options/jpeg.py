from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aep_parser.enums import JpegFormatType


@dataclass
class JpegFormatOptions:
    """JPEG format-specific render options.

    These settings correspond to the JPEG Options dialog in After Effects,
    accessible when the output format is set to JPEG Sequence.

    Example:
        ```python
        from aep_parser import JpegFormatOptions, parse

        app = parse("project.aep")
        om = app.project.render_queue.items[0].output_modules[0]
        if isinstance(om.format_options, JpegFormatOptions):
            print(om.format_options.quality)
        ```
    """

    quality: int
    """
    JPEG quality level, from 0 (Smaller File) to 10 (Bigger File).
    """

    format_type: JpegFormatType
    """
    JPEG format option type: Baseline (Standard), Baseline Optimized,
    or Progressive.
    """

    scans: int
    """
    Number of progressive scans (3, 4, or 5). Only relevant when
    `format_type` is `JpegFormatType.PROGRESSIVE`.
    """
