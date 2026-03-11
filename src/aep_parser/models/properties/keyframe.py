from __future__ import annotations

import typing
from dataclasses import dataclass

from aep_parser.enums import Label

if typing.TYPE_CHECKING:
    from aep_parser.enums import KeyframeInterpolationType
    from aep_parser.models.properties.keyframe_ease import KeyframeEase
    from aep_parser.models.properties.shape_value import ShapeValue


@dataclass
class Keyframe:
    """
    The `Keyframe` object represents a keyframe of a property.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        position = comp.layers[0].transform.property(name="ADBE Position")
        keyframe = position.keyframes[0]
        print(keyframe.time)
        ```

    Warning:
        `Keyframe` object does not exist in ExtendScript API. It has been added
        for convenience.
    """

    auto_bezier: bool
    """`True` if the keyframe has temporal auto-Bezier."""

    continuous_bezier: bool
    """`True` if the keyframe has temporal continuity."""

    frame_time: int
    """Time of the keyframe, in frames."""

    in_interpolation_type: KeyframeInterpolationType
    """The "in" interpolation type for the keyframe."""

    label: Label
    """
    The label color. Colors are represented by their number (0 for None, or 1
    to 16 for one of the preset colors in the Labels preferences).
    """

    out_interpolation_type: KeyframeInterpolationType
    """The "out" interpolation type for the keyframe."""

    roving_across_time: bool
    """
    `True` if the keyframe is roving. The first and last keyframe in
    a property cannot rove.
    """

    value: list[float] | float | ShapeValue | None
    """
    The value of the keyframe. For a 1D property (e.g. Opacity, Rotation),
    this is a single `float`. For a multi-dimensional property (e.g.
    Position, Scale), this is a `list[float]`. For shape/mask path
    properties, this is a [ShapeValue][]. For properties that carry no
    value (e.g. markers), this is `None`.
    """

    in_spatial_tangent: list[float] | None
    """
    The incoming spatial tangent for the keyframe, if the named
    property is spatial (that is, the value type is `TwoD_SPATIAL` or
    `ThreeD_SPATIAL`).

    - If the property value type is `PropertyValueType.TwoD_SPATIAL`, the list
    contains 2 floating-point values.
    - If the property value type is `PropertyValueType.ThreeD_SPATIAL`, the list
    contains 3 floating-point values.
    - If the property value type is neither of these types, returns `None`.
    """

    in_temporal_ease: list[KeyframeEase]
    """
    The incoming temporal ease for the keyframe.

    Array of [KeyframeEase][] objects:
    - If the property value type is `PropertyValueType.TwoD`, the array contains 2 objects.
    - If the property value type is `PropertyValueType.ThreeD`, the array contains 3 objects.
    - For any other value type, the array contains 1 object.

    """

    out_temporal_ease: list[KeyframeEase]
    """
    The outgoing temporal ease for the keyframe.

    Each element is a [KeyframeEase][] object — one per property dimension.
    For spatial properties, this list always has a single element.

    See:
        https://ae-scripting.docsforadobe.dev/property/property/#propertykeyouttemporalease
    """

    out_spatial_tangent: list[float] | None
    """
    The outgoing spatial tangent vector for the keyframe.

    Only set for spatial properties (e.g. Position). Each element corresponds
    to a dimension (X, Y, and optionally Z). ``None`` for non-spatial
    properties.

    See:
        https://ae-scripting.docsforadobe.dev/property/property/#propertykeyoutspatialtangent
    """
