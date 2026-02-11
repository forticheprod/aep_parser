from __future__ import annotations

from dataclasses import dataclass

from .footage import FootageSource


@dataclass
class SolidSource(FootageSource):
    """
    The `SolidSource` object represents a solid-color footage source.

    Info:
        `SolidSource` is a subclass of `FootageSource` object. All methods and
        attributes of `FootageSource` are
        available when working with `SolidSource`.

    See: https://ae-scripting.docsforadobe.dev/sources/solidsource/
    """

    color: list[float]
    """The solid color (RGBA)."""

    @property
    def is_solid(self) -> bool:
        """Whether this is a solid source."""
        return True
