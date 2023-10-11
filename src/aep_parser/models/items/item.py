import abc
import copy
import sys


if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(
        'ABC', (object,),
        {'__slots__': ()}
    )


class Item(ABC):
    def __init__(self, item_id, label, name, type_name, parent_folder):
        """
        Generalized object storing information about folders, compositions, or footages
        """
        # TODO Comment
        self.item_id = item_id
        self.label = label
        self.name = name  # TODO make it an abstract property ?
        self.parent_folder = parent_folder
        self.type_name = type_name

    def __repr__(self):
        attrs = copy.deepcopy(self.__dict__)
        if self.parent_folder is None:
            parent_folder = "<project>"
        else:
            parent_folder = "<'{parent_name}' folder>".format(
                parent_name=self.parent_folder.name
            )
        attrs["parent_folder"] = parent_folder
        return str(attrs)

    # @abc.abstractmethod
    # @property
    # def name(self):
    #     pass
