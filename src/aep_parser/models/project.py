class Project(object):
    def __init__(self,
                 depth, effect_names, expression_engine, framerate, project_items,
                 ae_version=None, metadata=None, root_folder=None):
        """
        After Effects project file
        """
        self.depth = depth
        self.effect_names = effect_names
        self.expression_engine = expression_engine
        self.framerate = framerate
        self.project_items = project_items
        self.ae_version = ae_version
        self.metadata = metadata
        self.root_folder = root_folder

    def __repr__(self):
        return str(self.__dict__)
