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
    Property object of a layer or nested property.

    Attributes:
        property_control_type: The type of the property (scalar, color, enum).
        expression: The expression for the named property.
        expression_enabled: True if the expression is enabled.
        property_value_type: The type of value stored in this property.
        value: The value of this property.
        max_value: The maximum permitted value for this property.
        min_value: The minimum permitted value for this property.
        dimensions_separated: When true, the property's dimensions are
            represented as separate properties. For example, if the layer's
            position is represented as X Position and Y Position properties
            in the Timeline panel, the Position property has this attribute
            set to true.
        is_spatial: When true, the property is a spatial property.
        property_parameters: A list of parameters for this property.
        locked_ratio: When true, the property's X/Y ratio is locked.
    """

    property_control_type: Aep.PropertyControlType = Aep.PropertyControlType.unknown
    expression: list[str] | None = None
    expression_enabled: bool | None = None
    property_value_type: Aep.PropertyValueType = Aep.PropertyValueType.unknown
    value: Any = None
    max_value: Any = None
    min_value: Any = None
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
        """True if the property is the Menu property of a Dropdown Menu Control effect."""
        return self.property_control_type == Aep.PropertyControlType.enum

    @property
    def is_time_varying(self) -> bool:
        """True if the named property has keyframes or an enabled expression."""
        return bool((self.expression and self.expression_enabled) or self.animated)

    @property
    def has_max(self) -> bool:
        """True if there is a maximum permitted value for the named property."""
        return bool(self.max_value)

    @property
    def has_min(self) -> bool:
        """True if there is a minimum permitted value for the named property."""
        return bool(self.min_value)
