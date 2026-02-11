from __future__ import annotations

import typing
from dataclasses import dataclass

from .layer import Layer

if typing.TYPE_CHECKING:
    from ..enums import LightType


@dataclass
class LightLayer(Layer):
    """
    The `LightLayer` object represents a light layer within a composition.

    Info:
        `LightLayer` is a subclass of `Layer` object. All methods and
        attributes of `Layer` are available when working with `LightLayer`.

    See: https://ae-scripting.docsforadobe.dev/layer/lightlayer/
    """

    light_type: LightType
    """The type of light."""
