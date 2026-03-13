from __future__ import annotations

import typing
from dataclasses import dataclass

from .layer import Layer

if typing.TYPE_CHECKING:
    from aep_parser.enums import LightType


@dataclass(eq=False)
class LightLayer(Layer):
    """
    The `LightLayer` object represents a light layer within a composition.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        light = comp.light_layers[0]
        print(light.light_type)
        ```

    Info:
        `LightLayer` is a subclass of [Layer][] object. All methods and
        attributes of [Layer][] are available when working with `LightLayer`.

    See: https://ae-scripting.docsforadobe.dev/layer/lightlayer/
    """

    light_type: LightType
    """The type of light."""
