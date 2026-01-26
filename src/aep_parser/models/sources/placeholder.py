from __future__ import annotations

from dataclasses import dataclass

from .footage import FootageSource


@dataclass
class PlaceholderSource(FootageSource):
    """Placeholder source."""

    @property
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return False
