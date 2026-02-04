from __future__ import annotations

from dataclasses import dataclass

from .av_layer import AVLayer


@dataclass
class TextLayer(AVLayer):
    """
    The TextLayer object represents a text layer within a composition.

    TextLayer is a subclass of AVLayer, which is a subclass of Layer.
    All methods and attributes of AVLayer and Layer are available when
    working with TextLayer.

    See: https://ae-scripting.docsforadobe.dev/layer/textlayer/
    """

    pass
