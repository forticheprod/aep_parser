from .item import Item


class Folder(Item):
    def __init__(self, folder_contents=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_contents = folder_contents
