from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class FootageSource(ABC):
    """Base class for footage sources."""

    @property
    @abstractmethod
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return False
