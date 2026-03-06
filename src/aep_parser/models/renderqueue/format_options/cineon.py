from __future__ import annotations

from dataclasses import dataclass

from aep_parser.enums import CineonFileFormat


@dataclass
class CineonFormatOptions:
    """Cineon/DPX format-specific render options.

    These settings correspond to the Cineon Settings dialog in After Effects,
    accessible when the output format is set to Cineon Sequence or DPX
    Sequence.

    Example:
        ```python
        import aep_parser
        from aep_parser.models.renderqueue.format_options.cineon import (
            CineonFormatOptions,
        )

        app = aep_parser.parse("project.aep")
        om = app.project.render_queue.items[0].output_modules[0]
        if isinstance(om.format_options, CineonFormatOptions):
            print(om.format_options.file_format)
        ```
    """

    ten_bit_black_point: int
    """
    The 10-bit black point value (0–1023). Defines the code value that
    maps to the black point on a logarithmic scale.
    """

    ten_bit_white_point: int
    """
    The 10-bit white point value (0–1023). Defines the code value that
    maps to the white point on a logarithmic scale.
    """

    converted_black_point: float
    """
    The converted black point value, normalized to the 0.0–1.0 range.
    This is the linear-light equivalent of the 10-bit black point.
    """

    converted_white_point: float
    """
    The converted white point value, normalized to the 0.0–1.0 range.
    This is the linear-light equivalent of the 10-bit white point.
    """

    current_gamma: float
    """The gamma value applied during the Cineon/DPX conversion."""

    highlight_expansion: int
    """The highlight expansion value."""

    logarithmic_conversion: bool
    """Whether logarithmic conversion is enabled."""

    file_format: CineonFileFormat
    """
    The file format for the Cineon output. See [CineonFileFormat][] for
    possible values.
    """

    bit_depth: int
    """The bit depth per channel (8, 10, 12, or 16)."""
