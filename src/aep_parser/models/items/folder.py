from .item import Item


class Folder(Item):
    def __init__(self,
                 items=[],
                 *args, **kwargs):
        super(Folder, self).__init__(*args, **kwargs)
        self.items = items

    def item(self, index):
        return self.items[index]
