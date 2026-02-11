from __future__ import annotations

from dataclasses import dataclass

from .layer import Layer


@dataclass
class CameraLayer(Layer):
    """
    The CameraLayer object represents a camera layer within a composition.

    Info:
        `CameraLayer` is a subclass of `Layer` object. All methods and
        attributes of `Layer` are available when working with `CameraLayer`.

    See: https://ae-scripting.docsforadobe.dev/layer/cameralayer/
    """

    pass
