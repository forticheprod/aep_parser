from .property_base import PropertyBase


class Property(PropertyBase):
    def __init__(self,
                 expression, max_value, min_value, property_value_type, value,
                 property_control_type, property_parameters,
                 *args, **kwargs):
        """
        Property object of a layer or nested property.
        Args:
            expression (str): The expression string for this property, if there is one.
            max_value (float): The maximum permitted value for this property.
            min_value (float): The minimum permitted value for this property.
            property_value_type (int): The type of value stored in this property.
            value (any): The value of this property.
            property_control_type (PropertyControlType): The type of the property
                                                         (scalar, color, enum).
            property_parameters (list): A list of parameters for this property.
            
        """
        super(Property, self).__init__(*args, **kwargs)
        # TODO dimensionsSeparated
        self.expression = expression
        # TODO expressionEnabled
        # TODO hasMax
        # TODO hasMin
        # TODO isDropdownEffect
        # TODO isSeparationFollower
        # TODO isSeparationLeader
        # TODO isSpatial
        # TODO isTimeVarying
        self.max_value = max_value
        self.min_value = min_value
        self.property_value_type = property_value_type
        # TODO separationDimension
        # TODO separationLeader
        self.value = value

        self.property_control_type = property_control_type
        self.property_parameters = property_parameters  # enum choices
        self.keyframes = []

    def __repr__(self):
        return str(self.__dict__)

    def add_key(self, keyframe):
        """
        Adds a new keyframe or marker to the named property at the specified time
        and returns the index of the new keyframe.
        Args:
            keyframe (models.properties.Keyframe): The keyframe to add.
        Returns:
            int: The index of the new keyframe.
        """
        self.keyframes.append(keyframe)
        return len(self.keyframes)

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
        pass

    def nearest_key_index(time):
        """
        Returns the index of the keyframe nearest to the specified time.
        Args:
            time (float): The time in seconds; a floating-point value. The beginning of the composition is 0.
        Returns:
            int: The index of the keyframe nearest to the specified time.
        """
        return min(self.keyframes, key=lambda k: abs(k.time - time))
