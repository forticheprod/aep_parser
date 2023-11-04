from six import string_types

from .property_base import PropertyBase


class PropertyGroup(PropertyBase):
    def __init__(self, is_effect, *args, **kwargs):
        """
        Group of properties.
        Args:
            is_effect (bool): When true, this property is an effect PropertyGroup.
        """
        super(PropertyGroup, self).__init__(*args, **kwargs)
        self.is_effect = is_effect

        self.properties = []
        self.enabled = True
        self.elided = not is_effect  # there might be more than that

    def __iter__(self):
        return iter(self.properties)

    def get_property(self, index=None, name=None):
        """
        Finds and returns a child property of this group, as specified by either its
        index or name (match name, parenthesis style or intercap style).
        Args:
            index (int): The index of the property to return.
            name (str): The name of the property to return.
        Returns:
            models.properties.Property: The property.
        """
        defined_arg = index or name
        if defined_arg:
            if isinstance(defined_arg, (int, float)):
                return self.properties[defined_arg]
            elif isinstance(defined_arg, string_types):
                for prop in self.properties:
                    if prop.name == defined_arg:
                        return prop

