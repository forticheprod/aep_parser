from .item import Item


class Folder(Item):
    def __init__(self, folder_items, *args, **kwargs):
        """
        Args:
            folder_items (list[Item]): The folder items.
        """
        super(Folder, self).__init__(*args, **kwargs)
        self.folder_items = folder_items

    def __iter__(self):
        """
        Returns:
            iter: An iterator over the folder items.
        """
        return iter(self.folder_items)

    def item(self, index):
        """
        Args:
            index (int): The index of the item to return.
        """
        return self.folder_items[index]
