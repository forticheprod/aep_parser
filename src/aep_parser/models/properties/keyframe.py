from __future__ import annotations

import typing
from dataclasses import dataclass

from aep_parser.enums import Label

if typing.TYPE_CHECKING:
    from aep_parser.enums import KeyframeInterpolationType


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
    """`True` if the specified keyframe has spatial auto-Bezier interpolation."""

    continuous_bezier: bool
    """`True` if the specified keyframe has temporal continuity."""

    frame_time: int
    """Time of the keyframe, in frames."""

    keyframe_interpolation_type: KeyframeInterpolationType
    """Interpolation type for the specified keyframe."""

    label: Label
    """
    The label color. Colors are represented by their number (0 for None, or 1
    to 16 for one of the preset colors in the Labels preferences).
    """

    roving_across_time: bool
    """
    `True` if the specified keyframe is roving. The first and last keyframe in
    a property cannot rove.
    """

    value: list[float] | float | None
    """
    The value of the keyframe. For a 1D property (e.g. Opacity, Rotation),
    this is a single `float`. For a multi-dimensional property (e.g.
    Position, Scale), this is a `list[float]`. For properties that carry no
    value (e.g. markers), this is `None`.
    """
