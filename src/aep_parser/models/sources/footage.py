from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..enums import AlphaMode, FieldSeparationType


@dataclass
class FootageSource(ABC):
    """
    Base class for footage sources.

    Corresponds to After Effects FootageSource object.
    See: https://ae-scripting.docsforadobe.dev/sources/footagesource/

    Attributes:
        alpha_mode: Defines how the alpha information in the footage is
            interpreted. If `has_alpha` is `False`, this attribute has no relevant
            meaning.
        conform_frame_rate: A frame rate to use instead of the `native_frame_rate`
            value. If set to 0, the `native_frame_rate` is used instead.
        field_separation_type: How the fields are to be separated in non-still
            footage. It is an error to set this attribute if `is_still` is `True`.
            It is an error to set this value to `FieldSeparationType.OFF` if
            `remove_pulldown` is not `PulldownPhase.OFF`.
        has_alpha: When `True`, the footage has an alpha component. In this
            case, the attributes `alpha_mode`, `invert_alpha`, and `premultiplied`
            have valid values. When `False`, those attributes have no relevant
            meaning for the footage.
        high_quality_field_separation: When `True`, After Effects uses special
            algorithms to determine how to perform high-quality field
            separation.
        invert_alpha: When `True`, an alpha channel in a footage clip or proxy
            should be inverted. This attribute is valid only if an alpha is
            present. If `has_alpha` is `False`, or if `alpha_mode` is
            `AlphaMode.IGNORE`, this attribute is ignored.
        is_still: When `True` the footage is still; When `False`, it has a
            time-based component. Examples of still footage are JPEG files,
            solids, and placeholders with a duration of 0. Examples of
            non-still footage are movie files, sound files, sequences, and
            placeholders of non-zero duration.
        loop: The number of times that the footage is to be played
            consecutively when used in a composition.
        premul_color: The color to be premultiplied. This attribute is valid
            only if the `alpha_mode` is `AlphaMode.PREMULTIPLIED`.
    """

    alpha_mode: AlphaMode
    conform_frame_rate: int
    field_separation_type: FieldSeparationType
    has_alpha: bool
    high_quality_field_separation: bool
    invert_alpha: bool
    is_still: bool
    loop: int
    premul_color: list[float]

    @property
    @abstractmethod
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return False
