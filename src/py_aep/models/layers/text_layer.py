from __future__ import annotations

from .av_layer import AVLayer


class TextLayer(AVLayer):
    """
    The `TextLayer` object represents a text layer within a composition.

    Example:
        ```python
        from py_aep import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        text_layer = comp.text_layers[0]
        print(text_layer.text)
        ```

    Info:
        `TextLayer` is a subclass of [AVLayer][] object. All methods and
        attributes of [AVLayer][] are available when working with `TextLayer`.

    See: https://ae-scripting.docsforadobe.dev/layer/textlayer/
    """

    pass
