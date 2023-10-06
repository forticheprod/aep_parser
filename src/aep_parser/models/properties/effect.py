class Effect(object):
    def __init__(self, match_name="", name="", index=0, parameters=[]):
        """
        Effect object of a layer.
        """
        self.match_name = match_name
        self.name = name
        self.index = index
        self.parameters = parameters

    def __repr__(self):
        return str(self.__dict__)
