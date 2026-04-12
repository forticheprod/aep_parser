"""Lightweight stand-in for Kaitai body objects on synthesized properties.

A `ProxyBody` stores the same named attributes as a real Kaitai body
(e.g. `TdsbBody`, `Tdb4Body`) but does not participate in the binary
chunk tree.  `ChunkField` descriptors read from and write to it
transparently.  On first end-user write the owning model calls
`_materialize()` which replaces the proxy with real Kaitai chunks.
"""

from __future__ import annotations


class ProxyBody:
    """Attribute bag that mimics a Kaitai body without binary backing.

    `propagate_check` walks `_parent` upward; setting it to `None`
    makes the walk stop immediately so no serialization happens.
    """

    def __init__(self, **attrs: object) -> None:
        for name, value in attrs.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "_parent", None)

    def _check(self) -> None:  # noqa: PLR6301
        """No-op - satisfies the `propagate_check` contract."""
