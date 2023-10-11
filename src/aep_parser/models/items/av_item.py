from .item import Item


class AVItem(Item):
    def __init__(self,
                 item_id=0, label_color=None, name="", type_name="",
                 *args, **kwargs):
        """
        Generalized object storing information about folders, compositions, or footages
        """
        super(AVItem, self).__init__(*args, **kwargs)
        self.type_name = type_name
        self.item_id = item_id
        self.name = name
        self.label_color = label_color

    def __repr__(self):
        return str(self.__dict__)
