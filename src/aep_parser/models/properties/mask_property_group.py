from __future__ import annotations

from dataclasses import dataclass

from ...enums import MaskMode
from .property_group import PropertyGroup


@dataclass
class MaskPropertyGroup(PropertyGroup):
    """An individual mask applied to a layer.

    The `MaskPropertyGroup` represents a single mask on a layer. It is a
    child of the `Masks` [PropertyGroup][] (match name `ADBE Mask Parade`).

    Mask atoms have all the standard [PropertyGroup][] attributes plus the
    mask-specific fields below.

    See: https://ae-scripting.docsforadobe.dev/property/maskpropertygroup/
    """

    inverted: bool
    """
    If `True`, the mask is inverted.
    """

    locked: bool
    """
    If `True`, the mask path is locked and cannot be modified in the UI.
    """

    mask_mode: MaskMode
    """
    The blending mode for the mask. Controls how the mask interacts with
    other masks and with the layer below.
    """
