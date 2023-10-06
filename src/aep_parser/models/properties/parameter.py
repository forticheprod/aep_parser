from .property import Property


class Parameter(Property):
    def __init__(self, match_name="", name="", index=0, property_type=None,
                 select_options=[]):
        """
        Parameter of an effect.
        """
        self.match_name = match_name
        self.name = name
        self.index = index
        self.property_type = property_type
        self.select_options = select_options  # enum choices

    def __repr__(self):
        return str(self.__dict__)
