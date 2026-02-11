from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..enums import AlphaMode, FieldSeparationType


@dataclass
class FootageSource(ABC):
    """
    The `FootageSource` object holds information describing the source of some
    footage. It is used as the `main_source` of a `FootageItem` object, or the
    `proxy_source` of a `CompItem` object or `FootageItem`.

    See: https://ae-scripting.docsforadobe.dev/sources/footagesource/
    """

    alpha_mode: AlphaMode
    """
    Defines how the alpha information in the footage is interpreted. If
    `has_alpha` is `False`, this attribute has no relevant meaning.
    """

    conform_frame_rate: int
    """
    A frame rate to use instead of the `native_frame_rate` value. If set to 0,
    the `native_frame_rate` is used instead.
    """

    field_separation_type: FieldSeparationType
    """
    How the fields are to be separated in non-still footage. It is an error
    to set this attribute if `is_still` is `True`. It is an error to set this
    value to `FieldSeparationType.OFF` if `remove_pulldown` is not
    `PulldownPhase.OFF`.
    """

    has_alpha: bool
    """
    When `True`, the footage has an alpha component. In this case, the
    attributes `alpha_mode`, `invert_alpha`, and `premultiplied` have valid
    values. When `False`, those attributes have no relevant meaning for the
    footage.
    """

    high_quality_field_separation: bool
    """
    When `True`, After Effects uses special algorithms to determine how to
    perform high-quality field separation.
    """

    invert_alpha: bool
    """
    When `True`, an alpha channel in a footage clip or proxy should be
    inverted. This attribute is valid only if an alpha is present. If
    `has_alpha` is `False`, or if `alpha_mode` is `AlphaMode.IGNORE`, this
    attribute is ignored.
    """

    is_still: bool
    """
    When `True` the footage is still; When `False`, it has a time-based
    component. Examples of still footage are JPEG files, solids, and
    placeholders with a duration of 0. Examples of non-still footage are
    movie files, sound files, sequences, and placeholders of non-zero
    duration.
    """

    loop: int
    """
    The number of times that the footage is to be played consecutively when
    used in a composition.
    """

    premul_color: list[float]
    """
    The color to be premultiplied. This attribute is valid only if the
    `alpha_mode` is `AlphaMode.PREMULTIPLIED`.
    """

    @property
    @abstractmethod
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return False
