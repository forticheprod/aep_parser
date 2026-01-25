from __future__ import annotations

import os

from .footage import FootageSource


class FileSource(FootageSource):
    def __init__(
        self,
        file: str,
        file_names: list[str],
        target_is_folder: bool,
        *args,
        **kwargs,
    ):
        """
        File source.

        Args:
            file: The full file path.
            file_names: The filenames if the footage is an image sequence.
            target_is_folder: True if the file is a folder, else False.
        """
        super().__init__(*args, **kwargs)
        self.file = file
        self.file_names = file_names
        self.target_is_folder = target_is_folder

    @property
    def missing_footage_path(self) -> str:
        """The missing footage path if the footage is missing, else empty."""
        return self.file if not os.path.exists(self.file) else ""
