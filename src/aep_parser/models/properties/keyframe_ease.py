"""Keyframe ease model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KeyframeEase:
    """
    The `KeyframeEase` object encapsulates the keyframe ease settings of a
    layer's AE property. Keyframe ease is determined by the `speed` and
    `influence` values.

    See: https://ae-scripting.docsforadobe.dev/other/keyframeease/

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        position = comp.layers[0].transform.property(name="ADBE Position")
        keyframe = position.keyframes[0]
        print(keyframe.out_temporal_ease[0].speed)
        print(keyframe.out_temporal_ease[0].influence)
        ```
    """

    speed: float
    """
    The speed value of the keyframe. The units depend on the type of keyframe,
    and are displayed in the Keyframe Velocity dialog box.
    """

    influence: float
    """
    The influence value of the keyframe, as shown in the Keyframe Velocity
    dialog box. This is a percentage value between 0.1 and 100.
    """
