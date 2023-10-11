class Property(object):
    def __init__(self, match_name="", name="", index=0, property_type=None,
                 select_options=[], keyframes=dict()):
        """
        Property object of a layer or nested property.
        """
        self.match_name = match_name
        self.name = name
        self.index = index
        self.property_type = property_type
        self.select_options = select_options  # enum choices
        self.keyframes = keyframes

    def __repr__(self):
        return str(self.__dict__)
