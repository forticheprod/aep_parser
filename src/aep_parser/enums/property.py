"""Property-related After Effects enumerations."""

from __future__ import annotations

from enum import IntEnum


class PropertyControlType(IntEnum):
    """The type of effect control for a property.

    Describes the UI control type exposed in the After Effects effect panel
    (scalar slider, color picker, angle dial, checkbox, dropdown, etc.).
    """

    LAYER = 0
    INTEGER = 1
    SCALAR = 2
    ANGLE = 3
    BOOLEAN = 4
    COLOR = 5
    TWO_D = 6
    ENUM = 7
    PAINT_GROUP = 9
    SLIDER = 10
    CURVE = 11
    MASK = 12
    GROUP = 13
    UNKNOWN_14 = 14
    UNKNOWN = 15
    THREE_D = 18


class PropertyValueType(IntEnum):
    """The type of value stored in a property.

    Each type of data is stored and retrieved in a different kind of
    structure.  For example, a 3-D spatial property (such as a layer's
    position) is stored as an array of three floating-point values.

    See: https://ae-scripting.docsforadobe.dev/property/property/#propertypropertyvaluetype
    """

    UNKNOWN = 0
    NO_VALUE = 1
    THREE_D_SPATIAL = 2
    THREE_D = 3
    TWO_D_SPATIAL = 4
    TWO_D = 5
    ONE_D = 6
    COLOR = 7
    CUSTOM_VALUE = 8
    MARKER = 9
    LAYER_INDEX = 10
    MASK_INDEX = 11
    SHAPE = 12
    TEXT_DOCUMENT = 13
    LRDR = 14
    LITM = 15
    GIDE = 16
    ORIENTATION = 17


class KeyframeInterpolationType(IntEnum):
    """Interpolation type for keyframes.

    See: https://ae-scripting.docsforadobe.dev/property/property/#propertysetinterpolationtypeatkey
    """

    LINEAR = 6612
    BEZIER = 6613
    HOLD = 6614

    @classmethod
    def from_binary(cls, value: int) -> KeyframeInterpolationType:
        """Convert binary value to KeyframeInterpolationType."""
        try:
            return cls(value + 6611)
        except ValueError:
            return cls.LINEAR
