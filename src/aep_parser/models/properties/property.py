from __future__ import annotations

import math
import typing
from dataclasses import dataclass
from typing import cast

from aep_parser.enums import PropertyControlType, PropertyType, PropertyValueType

from .property_base import PropertyBase

if typing.TYPE_CHECKING:
    from typing import Any

    from aep_parser.enums import KeyframeInterpolationType, Label
    from aep_parser.models.properties.keyframe_ease import KeyframeEase
    from aep_parser.models.properties.marker import MarkerValue
    from aep_parser.models.properties.shape import Shape
    from aep_parser.models.text.text_document import TextDocument

    from .keyframe import Keyframe

_SEPARATION_LEADER = "ADBE Position"
_SEPARATION_FOLLOWERS: list[str] = [
    "ADBE Position_0",
    "ADBE Position_1",
    "ADBE Position_2",
]


def _values_equal(a: Any, b: Any) -> bool:
    """Compare two property values with float tolerance.

    Handles scalars, lists/tuples, booleans, and None.
    Uses [math.isclose][] for numeric comparisons.
    """
    if a is None or b is None:
        return a is b
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a == b)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        return all(_values_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, abs_tol=1e-6)
    return bool(a == b)


@dataclass
class Property(PropertyBase):
    """
    The `Property` object contains value, keyframe, and expression information
    about a particular AE property of a layer. An AE property is a value,
    often animatable, of an effect, mask, or transform within an individual
    layer.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        prop = comp.layers[0].transform.property(name="ADBE Position")
        print(prop.value)
        ```

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

    units_text: str
    """
    The text description of the units in which the value is expressed.

    Common values include `"pixels"`, `"degrees"`, `"percent"`,
    `"seconds"`, and `"dB"`. An empty string indicates the property
    has no specific unit.
    """

    vector: bool
    """When `True`, the property value is a vector."""

    # Set after initialization
    default_value: Any = None
    """The default value of the property."""

    expression_error: str = ""
    """
    Contains the error, if any, generated by evaluation of the string most
    recently set in [expression][]. If no expression string has been
    specified, or if the last expression string evaluated without error,
    contains the empty string (`""`).

    Note:
        The parser cannot evaluate expressions, so this attribute is always
        an empty string. After Effects computes expression errors at runtime
        when it evaluates the expression engine; this information is not
        stored in the binary `.aep` file.
    """

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

    def __post_init__(self) -> None:
        """Set the property type to PROPERTY."""
        self.property_type = PropertyType.PROPERTY

    @property
    def is_separation_leader(self) -> bool:
        """`True` if the property is a multidimensional property that
        can be separated.
        """
        return self.match_name == _SEPARATION_LEADER

    @property
    def is_separation_follower(self) -> bool:
        """`True` if the property is a component of a separated
        multidimensional property (e.g. X Position, Y Position,
        Z Position).
        """
        return self.match_name in _SEPARATION_FOLLOWERS

    @property
    def separation_dimension(self) -> int | None:
        """For a separated follower, the dimension it represents.

        Returns 0, 1, or 2 for X, Y, or Z. Returns `None` for
        properties that are not separation followers.
        """
        if not self.is_separation_follower:
            return None
        return _SEPARATION_FOLLOWERS.index(self.match_name)

    @property
    def separation_leader(self) -> Property | None:
        """For a separation follower, the leader property.

        Returns the [Property][] that acts as the separation leader
        (e.g. Position) for this follower (e.g. X Position).
        Returns `None` when this property is not a follower or the
        leader cannot be found.
        """
        if self.match_name not in _SEPARATION_FOLLOWERS:
            return None
        parent = self.parent_property
        if parent is None or not hasattr(parent, "properties"):
            return None
        return cast("Property | None", parent.property(name=_SEPARATION_LEADER))

    def get_separation_follower(self, dim: int) -> Property | None:
        """
        Retrieve a specific follower property for a separated,
        multidimensional property.

        For example, you can use this method on the Position property
        to access the separated X Position and Y Position properties.

        Args:
            dim: The dimension number (starting at 0).
        """
        if not self.is_separation_leader:
            return None
        parent = self.parent_property
        if parent is None or not hasattr(parent, "properties"):
            return None
        if dim < 0 or dim >= len(_SEPARATION_FOLLOWERS):
            raise ValueError(f"{dim} must be ")
        match_name = _SEPARATION_FOLLOWERS[dim]
        return cast("Property | None", parent.property(name=match_name))

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

    def key_in_interpolation_type(self, key_index: int) -> KeyframeInterpolationType:
        """Returns the "in" interpolation type for the specified
        keyframe.

        Note:
            Equivalent to `self.keyframes[key_index].in_interpolation_type`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].in_interpolation_type

    def key_in_spatial_tangent(self, key_index: int) -> list[float] | None:
        """Returns the incoming spatial tangent for the specified
        keyframe, if the named property is spatial (that is, the
        value type is `TwoD_SPATIAL` or `ThreeD_SPATIAL`).

        Note:
            Equivalent to `self.keyframes[key_index].in_spatial_tangent`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].in_spatial_tangent

    def key_in_temporal_ease(self, key_index: int) -> list[KeyframeEase]:
        """Returns the incoming temporal ease for the specified
        keyframe.

        Note:
            Equivalent to `self.keyframes[key_index].in_temporal_ease`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].in_temporal_ease

    def key_label(self, key_index: int) -> Label:
        """Returns the label color for the specified keyframe.
        Colors are represented by their number (0 for None, or 1
        to 16 for one of the preset colors in the Labels
        preferences).

        Note:
            Equivalent to `self.keyframes[key_index].label`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].label

    def key_out_interpolation_type(self, key_index: int) -> KeyframeInterpolationType:
        """Returns the outgoing interpolation type for the specified
        keyframe.

        Note:
            Equivalent to
            `self.keyframes[key_index].out_interpolation_type`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].out_interpolation_type

    def key_out_spatial_tangent(self, key_index: int) -> list[float] | None:
        """Returns the outgoing spatial tangent for the specified
        keyframe.

        Note:
            Equivalent to
            `self.keyframes[key_index].out_spatial_tangent`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].out_spatial_tangent

    def key_out_temporal_ease(self, key_index: int) -> list[KeyframeEase]:
        """Returns the outgoing temporal ease for the specified
        keyframe.

        Note:
            Equivalent to
            `self.keyframes[key_index].out_temporal_ease`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].out_temporal_ease

    def key_roving(self, key_index: int) -> bool:
        """Returns `True` if the specified keyframe is roving.
        The first and last keyframe in a property cannot rove.

        Note:
            Equivalent to `self.keyframes[key_index].roving`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].roving

    def key_spatial_auto_bezier(self, key_index: int) -> bool:
        """Returns `True` if the specified keyframe has spatial
        auto-Bezier interpolation. This type of interpolation
        affects this keyframe only if `key_spatial_continuous` is
        also `True`.

        Note:
            Equivalent to
            `self.keyframes[key_index].spatial_auto_bezier`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].spatial_auto_bezier

    def key_spatial_continuous(self, key_index: int) -> bool:
        """Returns `True` if the specified keyframe has spatial
        continuity.

        Note:
            Equivalent to
            `self.keyframes[key_index].spatial_continuous`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].spatial_continuous

    def key_temporal_auto_bezier(self, key_index: int) -> bool:
        """Returns `True` if the specified keyframe has temporal
        auto-Bezier interpolation. Temporal auto-Bezier
        interpolation affects this keyframe only if the keyframe
        interpolation type is `KeyframeInterpolationType.BEZIER`
        for both `key_in_interpolation_type` and
        `key_out_interpolation_type`.

        Note:
            Equivalent to
            `self.keyframes[key_index].temporal_auto_bezier`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].temporal_auto_bezier

    def key_temporal_continuous(self, key_index: int) -> bool:
        """Returns `True` if the specified keyframe has temporal
        continuity. Temporal continuity affects this keyframe only
        if the keyframe interpolation type is
        `KeyframeInterpolationType.BEZIER` for both
        `key_in_interpolation_type` and
        `key_out_interpolation_type`.

        Note:
            Equivalent to
            `self.keyframes[key_index].temporal_continuous`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].temporal_continuous

    def key_time(self, key_index: int) -> float:
        """Returns the time at which the specified keyframe occurs.

        Note:
            Equivalent to `self.keyframes[key_index].time`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].time

    def key_value(
        self, key_index: int
    ) -> list[float] | float | MarkerValue | Shape | TextDocument | None:
        """Returns the current value of the specified keyframe.

        Note:
            Equivalent to `self.keyframes[key_index].value`.

        Args:
            key_index: The index for the keyframe.
        """
        return self.keyframes[key_index].value

    @property
    def num_keys(self) -> int:
        """The number of keyframes in the named property.
        If the value is 0, the property is not being keyframed.

        Note:
            Equivalent to `len(self.keyframes)`.
        """
        return len(self.keyframes)

    @property
    def is_modified(self) -> bool:
        """`True` if the property value differs from its default.

        A property is considered modified when it has keyframes, has an
        enabled expression, or when its current value differs from
        `default_value`.
        """
        if self.animated:
            return True
        if self.expression and self.expression_enabled:
            return True
        if self.default_value is not None:
            return not _values_equal(self.value, self.default_value)
        return False

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
