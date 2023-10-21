from .item import Item


class Folder(Item):
    def __init__(self,
                 folder_items,
                 *args, **kwargs):
        super(Folder, self).__init__(*args, **kwargs)
        self.folder_items = folder_items

    def item(self, index):
        return self.folder_items[index]
