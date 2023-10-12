import abc
import copy
import sys


if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(
        'ABC', (object,),
        {'__slots__': ()}
    )


class PropertyBase(ABC):
    def __init__(self,
                 enabled, is_effect, match_name, name, parent_property, property_type):
        """
        Base class for both Property and PropertyGroup.
        Args:
            enabled (bool): Corresponds to the setting of the eyeball icon.
            is_effect (bool): When true, this property is an effect PropertyGroup.
            match_name (str): A special name for the property used to build unique
                              naming paths. The match name is not displayed, but you
                              can refer to it in scripts. Every property has a unique
                              match-name identifier..
            name (str): Display name of the property.
            parent_property (PropertyGroup): The property group that is the immediate
                                             parent of this property.
            property_type (PropertyType): The type of this property
        """
        self.enabled = enabled
        self.is_effect = is_effect
        # TODO isMask
        self.match_name = match_name
        self.name = name
        self.parent_property = parent_property
        self.property_index = len(parent_property.properties) + 1
        self.property_type = property_type

    def __repr__(self):
        attrs = copy.deepcopy(self.__dict__)
        # Collapse parent_property to avoid infinite recursion
        if not isinstance(self.parent_property, PropertyBase):
            parent_property = "<layer>"
        else:
            parent_property = "<'{parent_name}' PropertyGroup>".format(
                parent_name=self.parent_property.name
            )
        attrs["parent_property"] = parent_property
        return str(attrs)

    @property
    def active(self):
        """
        For an effect and all properties, it is the same as the enabled attribute,
        except that it’s read-only
        """
        return self.enabled

    @abc.abstractmethod
    @property
    def elided(self):
        """
        When true, this property is a group used to organize other properties.
        The property is not displayed in the user interface and its child properties
        are not indented in the Timeline panel.
        """
        pass

    @property
    def is_modified(self):
        """
        When true, this property has been changed since its creation.
        """
        pass

    def property_group(self, count_up=1):
        """
        Returns the property group that contains this property.
        """
        if count_up == 0:
            return self
        else:
            return self.parent_property.property_group(count_up - 1)

    @property
    def property_depth(self):
        """
        Returns the number of levels of parent groups between this property and the
        containing layer. The value 0 for a layer.
        """
        depth = 1
        while self.parent_property:
            depth += 1
            self = self.parent_property
        return depth