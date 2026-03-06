from __future__ import annotations

from dataclasses import dataclass

from .layer import Layer


@dataclass
class CameraLayer(Layer):
    """
    The CameraLayer object represents a camera layer within a composition.

    Example:
        ```python
        import aep_parser

        app = aep_parser.parse("project.aep")
        comp = app.project.compositions[0]
        camera = comp.camera_layers[0]
        print(camera.name)
        ```

    Info:
        `CameraLayer` is a subclass of [Layer][] object. All methods and
        attributes of [Layer][] are available when working with `CameraLayer`.

    See: https://ae-scripting.docsforadobe.dev/layer/cameralayer/
    """

    pass
