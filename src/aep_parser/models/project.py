class Project(object):
    def __init__(self, depth=None, root_folder=None, items_=dict(),
                 expression_engine=None):
        """
        After Effects project file
        """
        self.depth = depth
        self.root_folder = root_folder
        self.items_ = items_
        self.expression_engine = expression_engine

    def __repr__(self):
        return str(self.__dict__)
