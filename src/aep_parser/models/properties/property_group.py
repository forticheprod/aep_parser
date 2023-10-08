class PropertyGroup(object):
    def __init__(self, match_name="", name="", index=0, property_type=None,
                 properties=[]):
        """
        Group of properties.
        """
        self.match_name = match_name
        self.name = name
        self.index = index
        self.property_type = property_type
        self.properties = properties

    def __repr__(self):
        return str(self.__dict__)
