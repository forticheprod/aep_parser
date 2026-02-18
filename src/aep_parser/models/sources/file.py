from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aep_parser.utils import safe_path_exists

from .footage import FootageSource


@dataclass
class FileSource(FootageSource):
    """
    The `FileSource` object describes footage that comes from a file.

    Info:
        `FileSource` is a subclass of [FootageSource][] object. All methods and
        attributes of [FootageSource][] are available when working with `FileSource`.

    See: https://ae-scripting.docsforadobe.dev/sources/filesource/
    """

    file: str
    """The full file path."""

    file_names: list[str]
    """The filenames if the footage is an image sequence."""

    target_is_folder: bool
    """`True` if the file is a folder, else `False`."""

    file_attributes: dict[str, Any] = field(default_factory=dict)
    """
    Format-specific metadata extracted from the source file header stored
    in the project.

    For PSD (Photoshop) sources, the following keys are available:

    - ``psd_layer_index`` (`int`): Zero-based index of this layer within the
      PSD file. ``0xFFFF`` means merged/flattened.
    - ``psd_group_name`` (`str`): PSD group/folder that contains this layer
      (e.g. ``"PAINT 02"``).
    - ``psd_layer_count`` (`int`): Total number of layers in the source PSD.
    - ``psd_canvas_width`` (`int`): Full PSD canvas width in pixels.
    - ``psd_canvas_height`` (`int`): Full PSD canvas height in pixels.
    - ``psd_bit_depth`` (`int`): Bit depth per channel (8, 16, 32).
    - ``psd_channels`` (`int`): Number of color channels (3 for RGB,
      4 for RGBA/CMYK).
    - ``psd_layer_top`` (`int`): Layer bounding-box top (pixels, can be
      negative if the layer extends above the canvas).
    - ``psd_layer_left`` (`int`): Layer bounding-box left.
    - ``psd_layer_bottom`` (`int`): Layer bounding-box bottom.
    - ``psd_layer_right`` (`int`): Layer bounding-box right.
    """

    @property
    def missing_footage_path(self) -> str:
        """The missing footage path if the footage is missing, else empty."""
        return self.file if not safe_path_exists(self.file) else ""

    @property
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return False
