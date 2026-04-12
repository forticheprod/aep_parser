from __future__ import annotations

from .av_layer import AVLayer


class ThreeDModelLayer(AVLayer):
    """
    The `ThreeDModelLayer` object represents a 3D Model layer within a
    composition.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        model_layer = comp.three_d_model_layers[0]
        print(model_layer.source)
        ```

    Info:
        `ThreeDModelLayer` is a subclass of [AVLayer][] object. All methods and
        attributes of [AVLayer][] are available when working with
        `ThreeDModelLayer`.

    Note:
        This functionality was added in After Effects 24.4

    See: https://ae-scripting.docsforadobe.dev/layer/threedmodellayer/
    """

    @property
    def can_set_collapse_transformation(self) -> bool:
        """`True` for 3D Model layers. Read-only."""
        return True

    @property
    def can_set_time_remap_enabled(self) -> bool:
        """`False` for 3D Model layers (time remapping is not supported). Read-only."""
        return False
