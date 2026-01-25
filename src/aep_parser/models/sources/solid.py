from __future__ import annotations

from .footage import FootageSource


class SolidSource(FootageSource):
    def __init__(self, color: list[float], *args, **kwargs):
        """
        Solid source.

        Args:
            color: The solid color (RGBA).
        """
        super().__init__(*args, **kwargs)
        self.color = color

    @property
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return True
