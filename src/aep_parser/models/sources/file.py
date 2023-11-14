import os

from .footage import FootageSource


class FileSource(FootageSource):
    def __init__(self, file, file_names, target_is_folder, *args, **kwargs):
        """
        Args:
            file (str): The full file path.
            file_names (list[str]): The filenames if the footage is an image sequence.
            target_is_folder (bool): True if the file is a folder, else False.
        """
        super(FileSource, self).__init__(*args, **kwargs)
        self.file = file
        self.file_names = file_names
        self.target_is_folder = target_is_folder
    
    @property
    def missing_footage_path(self):
        """
        Returns:
            str: The missing footage path if the footage is missing, else an empty string.
        """
        return self.file if os.path.exists(self.file) else ""
