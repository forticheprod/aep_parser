from __future__ import annotations

from dataclasses import dataclass

from .footage import FootageSource


@dataclass
class SolidSource(FootageSource):
    """
    Solid source.

    Corresponds to After Effects SolidSource object.
    See: https://ae-scripting.docsforadobe.dev/sources/solidsource/

    Attributes:
        color: The solid color (RGBA).
    """

    color: list[float]

    @property
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return True
