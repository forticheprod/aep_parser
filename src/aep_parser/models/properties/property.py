from __future__ import annotations

import typing
from dataclasses import dataclass

from ..enums import PropertyControlType, PropertyValueType
from .property_base import PropertyBase

if typing.TYPE_CHECKING:
    from typing import Any

    from .keyframe import Keyframe


@dataclass
class Property(PropertyBase):
    """
    The `Property` object contains value, keyframe, and expression information
    about a particular AE property of a layer. An AE property is a value,
    often animatable, of an effect, mask, or transform within an individual
    layer.

    Info:
        `Property` is a subclass of [PropertyBase][]. All methods and attributes
        of [PropertyBase][] are available when working with `Property`.

    See: https://ae-scripting.docsforadobe.dev/property/property/
    """

    animated: bool
    """When `True`, the property has keyframes."""

    color: bool
    """When `True`, the property value is a color."""

    dimensions_separated: bool
    """
    When `True`, the property's dimensions are represented as separate
    properties. For example, if the layer's position is represented as X
    Position and Y Position properties in the Timeline panel, the Position
    property has this attribute set to `True`. This attribute applies only
    when the property is a "separation leader" (a multidimensional property
    that can be separated).
    """

    dimensions: int
    """The number of dimensions in the property value (1, 2, or 3)."""

    expression_enabled: bool
    """
    When `True`, the named property uses its associated expression to generate
    a value. When `False`, the keyframe information or static value of the
    property is used.
    """

    expression: str
    """
    The expression for the named property. Writeable only when
    `can_set_expression` for the named property is `True`.
    """

    integer: bool
    """When `True`, the property value is an integer."""

    is_spatial: bool
    """
    When `True`, the named property defines a spatial value. Examples are
    position and effect point controls.
    """

    keyframes: list[Keyframe]
    """The list of keyframes for this property."""

    locked_ratio: bool
    """When `True`, the property's X/Y ratio is locked."""

    no_value: bool
    """When `True`, the property stores no data."""

    property_control_type: PropertyControlType
    """
    The type of effect control (scalar, color, enum, etc.) for this property.
    """

    property_value_type: PropertyValueType
    """
    The type of value stored in the named property. Each type of data is
    stored and retrieved in a different kind of structure. For example, a 3D
    spatial property (such as a layer's position) is stored as an array of
    three floating-point values.
    """

    value: Any
    """
    The value of the named property at the current time. If `expression_enabled`
    is `True`, returns the evaluated expression value. If there are keyframes,
    returns the keyframed value at the current time. Otherwise, returns the
    static value.
    """

    vector: bool
    """When `True`, the property value is a vector."""

    # Set after initialization
    elided: bool = False
    """When `True`, the property is elided (hidden in the UI)."""

    default_value: Any = None
    """The default value of the property."""

    last_value: Any = None
    """The last value of the property (before animation)."""

    max_value: Any = None
    """
    The maximum permitted value of the named property. Only valid if
    `has_max` is `True`.
    """

    min_value: Any = None
    """
    The minimum permitted value of the named property. Only valid if
    `has_min` is `True`.
    """

    nb_options: int | None = None
    """The number of options in a dropdown property."""

    property_parameters: list[str] | None = None  # enum choices
    """
    An array of all item strings in a dropdown menu property. This attribute
    applies to dropdown menu properties of effects and layers, including
    custom strings in the Menu property of the Dropdown Menu Control.
    """

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
        return self.property_control_type == PropertyControlType.ENUM

    @property
    def is_time_varying(self) -> bool:
        """`True` if the named property has keyframes or an enabled expression."""
        return bool((self.expression and self.expression_enabled) or self.animated)

    @property
    def has_max(self) -> bool:
        """`True` if there is a maximum permitted value for the named property."""
        return self.max_value is not None

    @property
    def has_min(self) -> bool:
        """`True` if there is a minimum permitted value for the named property."""
        return self.min_value is not None
