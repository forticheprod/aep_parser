from .item import Item


class Folder(Item):
    def __init__(self, folder_items,  *args, **kwargs):
        super(Folder, self).__init__(*args, **kwargs)
        self.folder_items = folder_items
        self.is_composition = False
        self.is_folder = True
        self.is_footage = False

    def __iter__(self):
        return iter(self.folder_items)

    def item(self, index):
        return self.folder_items[index]
