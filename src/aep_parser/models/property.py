class Property(object):
    def __init__(self, match_name="", name="", index=0, property_type=None,
                 select_options=[], properties=[]):
        """
        Property object of a layer or nested property.
        """
        self.match_name = match_name
        self.name = name
        self.index = index
        self.property_type = property_type
        self.properties = properties
        self.select_options = select_options

    def __repr__(self):
        return str(self.__dict__)
