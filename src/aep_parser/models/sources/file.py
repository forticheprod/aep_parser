from __future__ import annotations

import os
from dataclasses import dataclass

from aep_parser.utils import fs_timeout

from .footage import FootageSource


@fs_timeout(timeout=2.0, default=False)
def _safe_path_exists(path: str) -> bool:
    """Check if a path exists, guarded against hanging on network paths."""
    return os.path.exists(path)


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

    @property
    def missing_footage_path(self) -> str:
        """The missing footage path if the footage is missing, else empty."""
        return self.file if not _safe_path_exists(self.file) else ""

    @property
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return False
