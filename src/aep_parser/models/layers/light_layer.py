from __future__ import annotations

import typing
from dataclasses import dataclass

from .layer import Layer

if typing.TYPE_CHECKING:
    from ..enums import LightType


@dataclass
class LightLayer(Layer):
    """
    The LightLayer object represents a light layer within a composition.

    See: https://ae-scripting.docsforadobe.dev/layer/lightlayer/

    Attributes:
        light_type: The type of light.
    """

    light_type: LightType
