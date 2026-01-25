from __future__ import annotations

import typing

from .layer import Layer

if typing.TYPE_CHECKING:
    from ...kaitai.aep import Aep


class LightLayer(Layer):
    def __init__(self, light_type: Aep.LightType, *args, **kwargs):
        """
        The LightLayer object represents a light layer within a composition.

        This class is not used at the moment.

        Args:
            light_type: The type of light.
        """
        super().__init__(*args, **kwargs)
        self.light_type = light_type
