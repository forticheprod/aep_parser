import os

from .footage import FootageSource


class FileSource(FootageSource):
    def __init__(self,
                 file, file_names, target_is_folder,
                 *args, **kwargs):
        super(FileSource, self).__init__(*args, **kwargs)
        self.file = file
        self.file_names = file_names
        self.target_is_folder = target_is_folder
    
    @property
    def missing_footage_path(self):
        return self.file if os.path.exists(self.file) else ""

