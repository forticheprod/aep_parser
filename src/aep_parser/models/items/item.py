class Item(object):
    def __init__(self, item_type="", item_id=0, name="", label_color=None):
        """
        Generalized object storing information about folders, compositions, or asset
        """
        self.item_type = item_type
        self.item_id = item_id
        self.name = name
        self.label_color = label_color

    def __repr__(self):
        return str(self.__dict__)
