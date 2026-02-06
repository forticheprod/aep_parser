from __future__ import annotations

import typing
from dataclasses import dataclass, field

from ...kaitai import Aep
from .property_base import PropertyBase

if typing.TYPE_CHECKING:
    from typing import Any

    from .keyframe import Keyframe


@dataclass
class Property(PropertyBase):
    """
    Property object containing value, keyframe, and expression information.

    The Property object contains value, keyframe, and expression information
    about a particular AE property of a layer. An AE property is a value,
    often animatable, of an effect, mask, or transform within an individual
    layer.

    See: https://ae-scripting.docsforadobe.dev/property/property/

    Attributes:
        animated: When `True`, the property has keyframes.
        color: When `True`, the property value is a color.
        default_value: The default value of the property.
        dimensions: The number of dimensions in the property value (1, 2, or 3).
        dimensions_separated: When `True`, the property's dimensions are
            represented as separate properties. For example, if the layer's
            position is represented as X Position and Y Position properties
            in the Timeline panel, the Position property has this attribute
            set to `True`. This attribute applies only when the property is
            a "separation leader" (a multidimensional property that can be
            separated).
        elided: When `True`, the property is elided (hidden in the UI).
        expression: The expression for the named property. Writeable only
            when `can_set_expression` for the named property is `True`.
        expression_enabled: When `True`, the named property uses its associated
            expression to generate a value. When `False`, the keyframe
            information or static value of the property is used.
        integer: When `True`, the property value is an integer.
        is_spatial: When `True`, the named property defines a spatial value.
            Examples are position and effect point controls.
        keyframes: The list of keyframes for this property.
        last_value: The last value of the property (before animation).
        locked_ratio: When `True`, the property's X/Y ratio is locked.
        max_value: The maximum permitted value of the named property. Only
            valid if `has_max` is `True`.
        min_value: The minimum permitted value of the named property. Only
            valid if `has_min` is `True`.
        nb_options: The number of options in a dropdown property.
        no_value: When `True`, the property stores no data.
        property_control_type: The type of effect control (scalar, color,
            enum, etc.) for this property.
        property_parameters: An array of all item strings in a dropdown menu
            property. This attribute applies to dropdown menu properties of
            effects and layers, including custom strings in the Menu property
            of the Dropdown Menu Control.
        property_value_type: The type of value stored in the named property.
            Each type of data is stored and retrieved in a different kind of
            structure. For example, a 3D spatial property (such as a layer's
            position) is stored as an array of three floating-point values.
        value: The value of the named property at the current time. If
            `expression_enabled` is `True`, returns the evaluated expression
            value. If there are keyframes, returns the keyframed value at the
            current time. Otherwise, returns the static value.
        vector: When `True`, the property value is a vector.
    """

    property_control_type: Aep.PropertyControlType = Aep.PropertyControlType.unknown
    expression: list[str] | None = None
    expression_enabled: bool | None = None
    property_value_type: Aep.PropertyValueType = Aep.PropertyValueType.unknown
    value: Any = None
    last_value: Any = None
    default_value: Any = None
    max_value: Any = None
    min_value: Any = None
    nb_options: int | None = None
    dimensions_separated: bool | None = None
    is_spatial: bool | None = None
    property_parameters: list[str] | None = None  # enum choices
    locked_ratio: bool | None = None
    keyframes: list[Keyframe] = field(default_factory=list)
    elided: bool = False
    animated: bool = False
    dimensions: int = 0
    integer: bool = False
    vector: bool = False
    no_value: bool = False
    color: bool = False

    def get_separation_follower(self, dim: int) -> Property | None:
        """
        Retrieve a specific follower property for a separated, multidimensional property.

        For example, you can use this method on the Position property to access the
        separated X Position and Y Position properties.

        Args:
            dim: The dimension number (starting at 0).
        """
        return None  # TODO

    def nearest_key_index(self, time: float) -> int:
        """
        Returns the index of the keyframe nearest to the specified time.

        Args:
            time: The time in seconds; a floating-point value. The beginning
                of the composition is 0.
        """
        return min(
            range(len(self.keyframes)),
            key=lambda i: abs(self.keyframes[i].frame_time - time),
        )

    def nearest_key(self, time: float) -> Keyframe:
        """
        Returns the keyframe nearest to the specified time.

        Args:
            time: The time in seconds; a floating-point value. The beginning
                of the composition is 0.
        """
        index = self.nearest_key_index(time)
        return self.keyframes[index]

    @property
    def is_dropdown_effect(self) -> bool:
        """`True` if the property is the Menu property of a Dropdown Menu Control effect."""
        return self.property_control_type == Aep.PropertyControlType.enum

    @property
    def is_time_varying(self) -> bool:
        """`True` if the named property has keyframes or an enabled expression."""
        return bool((self.expression and self.expression_enabled) or self.animated)

    @property
    def has_max(self) -> bool:
        """`True` if there is a maximum permitted value for the named property."""
        return bool(self.max_value)

    @property
    def has_min(self) -> bool:
        """`True` if there is a minimum permitted value for the named property."""
        return bool(self.min_value)
