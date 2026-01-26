from __future__ import annotations

from dataclasses import dataclass

from .footage import FootageSource


@dataclass
class PlaceholderSource(FootageSource):
    """Placeholder source."""

    pass
