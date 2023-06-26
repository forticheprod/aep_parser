class Project(object):
    def __init__(self, depth=None, root_folder=None, project_items=dict(),
                 expression_engine=None):
        """
        After Effects project file
        """
        self.depth = depth
        self.root_folder = root_folder
        self.project_items = project_items
        self.expression_engine = expression_engine

    def __repr__(self):
        return str(self.__dict__)
