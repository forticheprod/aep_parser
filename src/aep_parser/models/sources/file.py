from __future__ import annotations

import os
from dataclasses import dataclass

from .footage import FootageSource


@dataclass
class FileSource(FootageSource):
    """
    File source.

    Attributes:
        file: The full file path.
        file_names: The filenames if the footage is an image sequence.
        target_is_folder: True if the file is a folder, else False.
    """

    file: str
    file_names: list[str]
    target_is_folder: bool

    @property
    def missing_footage_path(self) -> str:
        """The missing footage path if the footage is missing, else empty."""
        return self.file if not os.path.exists(self.file) else ""

    @property
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return False
