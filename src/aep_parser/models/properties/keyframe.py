from __future__ import annotations

import typing
from dataclasses import dataclass

from aep_parser.enums import Label

if typing.TYPE_CHECKING:
    from aep_parser.enums import KeyframeInterpolationType
    from aep_parser.models.properties.keyframe_ease import KeyframeEase
    from aep_parser.models.properties.shape_value import ShapeValue
    from aep_parser.models.text.text_document import TextDocument


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

    frame_time: int
    """Time of the keyframe, in frames."""

    in_interpolation_type: KeyframeInterpolationType
    """The "in" interpolation type for the keyframe."""

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
    - If the property value type is `PropertyValueType.TwoD`, the list contains
      2 objects.
    - If the property value type is `PropertyValueType.ThreeD`, the list contains
      3 objects.
    - For any other value type, the list contains 1 object.
    """

    label: Label
    """
    The label color. Colors are represented by their number (0 for None, or 1
    to 16 for one of the preset colors in the Labels preferences).
    """

    out_interpolation_type: KeyframeInterpolationType
    """The "out" interpolation type for the keyframe."""

    out_spatial_tangent: list[float] | None
    """
    The outgoing spatial tangent for the keyframe, if the named
    property is spatial (that is, the value type is `TwoD_SPATIAL` or
    `ThreeD_SPATIAL`).

    - If the property value type is `PropertyValueType.TwoD_SPATIAL`, the list
      contains 2 floating-point values.
    - If the property value type is `PropertyValueType.ThreeD_SPATIAL`, the list
      contains 3 floating-point values.
    - If the property value type is neither of these types, returns `None`.
    """

    out_temporal_ease: list[KeyframeEase]
    """
    The outgoing temporal ease for the keyframe.

    Array of [KeyframeEase][] objects:
    - If the property value type is `PropertyValueType.TwoD`, the list contains
      2 objects.
    - If the property value type is `PropertyValueType.ThreeD`, the list contains
      3 objects.
    - For any other value type, the list contains 1 object.
    """

    roving: bool
    """
    `True` if the keyframe is roving. The first and last keyframe in
    a property cannot rove.
    """

    spatial_auto_bezier: bool
    """
    `True` if the keyframe has spatial auto-Bezier interpolation. This type of
    interpolation affects this keyframe only if [spatial_continuous][] is also
    `True`. If the property value type is neither `TwoD_SPATIAL` nor
    `ThreeD_SPATIAL`, the value is `False`.
    """

    spatial_continuous: bool
    """
    `True` if the keyframe has spatial continuity. If the property value type
    is neither `TwoD_SPATIAL` nor `ThreeD_SPATIAL`, the value is `False`.
    """

    temporal_auto_bezier: bool
    """
    `True` if the keyframe has temporal auto-Bezier interpolation. Temporal
    auto-Bezier interpolation affects this keyframe only if the keyframe
    interpolation type is `KeyframeInterpolationType.BEZIER` for both
    `in_interpolation_type` and `out_interpolation_type`.
    """

    temporal_continuous: bool
    """
    `True` if the keyframe has temporal continuity. Temporal continuity affects
    this keyframe only if the keyframe interpolation type is
    `KeyframeInterpolationType.BEZIER` for both `in_interpolation_type` and
    `out_interpolation_type`.
    """

    time: float
    """Time of the keyframe, in seconds."""

    value: list[float] | float | ShapeValue | TextDocument | None
    """
    The value of the keyframe. For a 1D property (e.g. Opacity, Rotation), this
    is a single `float`. For a multi-dimensional property (e.g. Position,
    Scale), this is a `list[float]`. For shape/mask path properties, this is a
    [ShapeValue][]. For text properties, this is a [TextDocument][]. For
    properties that carry no value (e.g. markers), this is `None`.
    """
