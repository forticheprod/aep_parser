from __future__ import annotations

import typing
from dataclasses import dataclass

from .layer import Layer

if typing.TYPE_CHECKING:
    from ...kaitai.aep import Aep


@dataclass
class LightLayer(Layer):
    """
    The LightLayer object represents a light layer within a composition.

    This class is not used at the moment.

    Attributes:
        light_type: The type of light.
    """

    light_type: Aep.LightType | None = None
