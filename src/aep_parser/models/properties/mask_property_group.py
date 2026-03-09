from __future__ import annotations

from dataclasses import dataclass

from ...enums import MaskMode
from .property_group import PropertyGroup


@dataclass
class MaskPropertyGroup(PropertyGroup):
    """An individual mask applied to a layer.

    The `MaskPropertyGroup` object encapsulates mask attributes in a layer.

    Info:
        `MaskPropertyGroup` is a subclass of PropertyGroup object. All methods and
        attributes of [PropertyBase][aep_parser.models.properties.property_base.PropertyBase]
        object and [PropertyGroup][], in addition to those listed below, are available
        when working with `MaskPropertyGroup`.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        layer = comp.layers[0]
        mask = layer.masks[0]
        print(mask.inverted)
        ```

    See: https://ae-scripting.docsforadobe.dev/property/maskpropertygroup/
    """

    inverted: bool
    """
    When `True`, the mask is inverted.
    """

    locked: bool
    """
    When `True`, the mask is locked and cannot be edited in the user interface.
    """

    mask_mode: MaskMode
    """
    The blending mode for the mask. Controls how the mask interacts with
    other masks and with the layer below.
    """
