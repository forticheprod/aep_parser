from ...kaitai.aep import Aep
from .property_base import PropertyBase


class Property(PropertyBase):
    def __init__(self,
                 property_control_type=Aep.PropertyControlType.unknown, expression=None,
                 expression_enabled=None,
                 property_value_type=Aep.PropertyValueType.unknown, value=None,
                 max_value=None, min_value=None, dimensions_separated=None,
                 is_spatial=None, property_parameters=None, locked_ratio=None,
                 *args, **kwargs):
        """
        Property object of a layer or nested property.
        Args:
            property_control_type (Aep.PropertyControlType): The type of the property
                                                             (scalar, color, enum).
            expression (str): The expression for the named property
            excpression_enabled (bool): True if the expression is enabled.
            property_value_type (Aep.PropertyValueType): The type of value stored in
                                                         this property.
            value (any): The value of this property.
            max_value (any): The maximum permitted value for this property.
            min_value (any): The minimum permitted value for this property.
            dimensions_separated (bool): When true, the property's dimensions are
                                         represented as separate properties. For
                                         example, if the layer's position is represented
                                         as X Position and Y Position properties in the
                                         Timeline panel, the Position property has this
                                         attribute set to true.
            is_spatial (bool): When true, the property is a spatial property.
            property_parameters (list[str]): A list of parameters for this property.
            locked_ratio (bool): When true, the property's X/Y ratio locked.
            
        """
        super(Property, self).__init__(*args, **kwargs)
        self.property_control_type = property_control_type
        self.expression = expression
        self.expression_enabled = expression_enabled
        self.property_value_type = property_value_type
        self.value = value
        self.max_value = max_value
        self.min_value = min_value
        self.dimensions_separated = dimensions_separated
        self.is_spatial = is_spatial
        self.property_parameters = property_parameters  # enum choices
        self.locked_ratio = locked_ratio  # TODO figure out what this does
        # TODO isSeparationFollower
        # TODO isSeparationLeader
        # TODO separationDimension
        # TODO separationLeader

        self.keyframes = []
        self.elided = False

    def get_separation_follower(self, dim):
        """
        For a separated, multidimensional property, retrieves a specific follower
        property. For example, you can use this method on the Position property to
        access the separated X Position and Y Position properties.
        Args:
            dim (int): The dimension number (starting at 0).
        Returns:
            Property: The follower property.
        """
        pass  # TODO

    def nearest_key_index(self, time):
        """
        Returns the index of the keyframe nearest to the specified time.
        Args:
            time (float): The time in seconds; a floating-point value.
                          The beginning of the composition is 0.
        Returns:
            int: The index of the keyframe nearest to the specified time.
        """
        return min(self.keyframes, key=lambda k: abs(k.time - time))  # FIXME does not return index

    @property
    def is_dropdown_effect(self):
        """
        Returns:
            bool: True if the property is the Menu property of a Dropdown Menu Control
                  effect.
        """
        return self.property_control_type == Aep.PropertyControlType.enum

    @property
    def is_time_varying(self):
        """
        Returns:
            bool: True if the named property has keyframes or an enabled expression.
        """
        return bool((self.expression and self.expression_enabled) or self.animated)

    @property
    def has_max(self):
        """
        Returns:
            bool: True if there is a maximum permitted value for the named property.
        """
        return bool(self.max_value)

    @property
    def has_min(self):
        """
        Returns:
            bool: True if there is a minimum permitted value for the named property.
        """
        return bool(self.min_value)
