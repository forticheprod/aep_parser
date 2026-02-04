from __future__ import annotations

from dataclasses import dataclass

from .footage import FootageSource


@dataclass
class PlaceholderSource(FootageSource):
    """
    Placeholder source.

    Corresponds to After Effects PlaceholderSource object.
    See: https://ae-scripting.docsforadobe.dev/sources/placeholdersource/
    """

    @property
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return False
