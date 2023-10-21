import os

from .footage import FootageSource


class FileSource(FootageSource):
    def __init__(self,
                 ascendcount_base, ascendcount_target, file, platform, server_name,
                 server_volume_name, target_is_folder,
                 *args, **kwargs):
        super(FileSource, self).__init__(*args, **kwargs)
        self.ascendcount_base = ascendcount_base
        self.ascendcount_target = ascendcount_target
        self.file = file
        self.platform = platform
        self.server_name = server_name
        self.server_volume_name = server_volume_name
        self.target_is_folder = target_is_folder
    
    @property
    def missing_footage_path(self):
        return self.file if os.path.exists(self.file) else ""

