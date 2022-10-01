class Project(object):
    def __init__(self, depth=None, root_folder=None, items=None, expression_engine=None):
        self.depth = depth
        self.root_folder = root_folder
        self.items = items
        self.expression_engine = expression_engine

    def __repr__(self):
        return str(self.__dict__)
