from __future__ import annotations

from dataclasses import dataclass

from ...enums import MaskFeatherFalloff, MaskMode, MaskMotionBlur
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

    color: list[float]
    """
    The color used to draw the mask outline as it appears in the user
    interface (Composition panel, Layer panel, and Timeline panel).
    The three array values specify the red, green, and blue components
    of the color.
    """

    inverted: bool
    """
    When `True`, the mask is inverted.
    """

    locked: bool
    """
    When `True`, the mask is locked and cannot be edited in the user interface.
    """

    mask_feather_falloff: MaskFeatherFalloff
    """
    The feather falloff mode for the mask. Applies to all feather
    values for the mask.
    """

    mask_mode: MaskMode
    """
    The blending mode for the mask. Controls how the mask interacts with
    other masks and with the layer below.
    """

    mask_motion_blur: MaskMotionBlur
    """
    How motion blur is applied to this mask.
    """

    roto_bezier: bool
    """
    When `True`, the mask uses RotoBezier, enabling curved mask segments
    without direction handles.
    """
