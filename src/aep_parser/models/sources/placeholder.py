from __future__ import annotations

from dataclasses import dataclass

from .footage import FootageSource


@dataclass
class PlaceholderSource(FootageSource):
    """
    The `PlaceholderSource` object describes the footage source of a
    placeholder.

    Info:
        `PlaceholderSource` is a subclass of `FootageSource` object. All
        methods and attributes of `FootageSource` are available when working
        with `PlaceholderSource`. `PlaceholderSource` does not define any
        additional methods or attributes.

    See: https://ae-scripting.docsforadobe.dev/sources/placeholdersource/
    """

    @property
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return False
