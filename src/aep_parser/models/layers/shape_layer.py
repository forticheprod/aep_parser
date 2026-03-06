from __future__ import annotations

from dataclasses import dataclass

from .av_layer import AVLayer


@dataclass
class ShapeLayer(AVLayer):
    """
    The `ShapeLayer` object represents a shape layer within a composition.

    Example:
        ```python
        import aep_parser

        app = aep_parser.parse("project.aep")
        comp = app.project.compositions[0]
        shape_layer = comp.shape_layers[0]
        print(shape_layer.content)
        ```

    Info:
        `ShapeLayer` is a subclass of [AVLayer][] object. All methods and
        attributes of [AVLayer][] are available when working with `ShapeLayer`.

    See: https://ae-scripting.docsforadobe.dev/layer/shapelayer/
    """

    pass
