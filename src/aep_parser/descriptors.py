"""Descriptors for chunk-backed model fields.

Each descriptor reads from / writes to a Kaitai chunk body attribute,
so that modifying a model field directly mutates the underlying binary
data and `Project.save()` persists the change.

After every `__set__`, :func:`_propagate_check` walks the Kaitai
parent chain bottom-up: it calls `_check()` on each object (clearing
the `_dirty` flag) and updates every ancestor `Chunk.len_data` when
the body's serialized size has changed.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any, Callable

from kaitaistruct import KaitaiStream

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_body_size(body: Any) -> int:
    """Return the serialized byte size of a Kaitai body (trial write).

    The body must not be dirty — call `body._check()` first.
    `KaitaiStream` requires a pre-allocated buffer; we size it from
    the parent chunk's `len_data` with headroom for growth.
    """
    saved_io = body._io
    current = getattr(body._parent, "len_data", 0)
    buf = BytesIO(bytearray(current + 4096))
    body._write__seq(KaitaiStream(buf))
    size = buf.tell()
    body._io = saved_io
    return size


def _propagate_check(body: Any) -> None:
    """Call `_check()` bottom-up from *body* to root, updating `len_data`.

    1. `body._check()` clears the body's `_dirty` flag.
    2. A trial write computes the body's new serialized size.
    3. If the size changed, the delta is added to every ancestor
       `len_data` (Chunk and root Aep).
    4. `_check()` is called on every object up to the root so no
       `ConsistencyNotCheckedError` is raised during `save()`.
    """
    body._check()

    chunk = getattr(body, "_parent", None)
    if chunk is None:
        return

    new_size = _compute_body_size(body)
    delta = new_size - chunk.len_data

    obj: Any = chunk
    while obj is not None:
        if delta != 0 and hasattr(obj, "len_data"):
            obj.len_data += delta
        if hasattr(obj, "_check"):
            obj._check()
        obj = getattr(obj, "_parent", None)


class ChunkField:
    """Descriptor that proxies a single field on a chunk body.

    Args:
        chunk_attr: Name of the model attribute holding the chunk body
            reference (e.g. `"_cdta"`).
        field: Name of the field on the chunk body (e.g. `"width"`).
        transform: Optional callable applied when *getting* (binary →
            user-facing value).
        reverse: Optional callable applied when *setting* (user-facing →
            binary value).
        validate: Optional callable called with the user-facing value
            before any `reverse` transform.  Must raise `ValueError`
            or `TypeError` if the value is invalid.
        invalidates: Kaitai instance names to clear after a set so they
            are recomputed on next access.
        doc: Docstring shown on the descriptor (used by Sphinx / mkdocstrings).
    """

    _sentinel = object()

    def __init__(
        self,
        chunk_attr: str,
        field: str,
        *,
        transform: Callable[..., Any] | None = None,
        reverse: Callable[..., Any] | None = None,
        validate: Callable[..., None] | None = None,
        invalidates: list[str] | None = None,
        default: Any = _sentinel,
        doc: str | None = None,
    ) -> None:
        self.chunk_attr = chunk_attr
        self.field = field
        self.transform = transform
        self.reverse = reverse
        self.validate = validate
        self.invalidates = invalidates or []
        self.default = default
        if doc is not None:
            self.__doc__ = doc

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name

    def _get_body(self, obj: Any) -> Any:
        return getattr(obj, self.chunk_attr)

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        body = self._get_body(obj)
        if body is None:
            if self.default is not self._sentinel:
                return self.default
            raise AttributeError(
                f"chunk body {self.chunk_attr!r} is None"
            )
        value = getattr(body, self.field)
        if self.transform is not None:
            return self.transform(value)
        return value

    def __set__(self, obj: Any, value: Any) -> None:
        body = self._get_body(obj)
        if body is None:
            raise AttributeError(
                f"cannot set {self.field!r}: chunk body {self.chunk_attr!r} is None"
            )
        if self.validate is not None:
            self.validate(value)
        if self.reverse is not None:
            value = self.reverse(value)
        setattr(body, self.field, value)
        for inst in self.invalidates:
            invalidator = getattr(body, f"_invalidate_{inst}", None)
            if invalidator is not None:
                try:
                    invalidator()
                except AttributeError:
                    pass
        _propagate_check(body)


class ChunkFlagField(ChunkField):
    """Descriptor for a boolean bit-flag field on a chunk body.

    Always returns `bool` on get and writes `bool` on set.
    """

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        body = self._get_body(obj)
        if body is None:
            if self.default is not self._sentinel:
                return self.default
            raise AttributeError(
                f"chunk body {self.chunk_attr!r} is None"
            )
        return bool(getattr(body, self.field))

    def __set__(self, obj: Any, value: Any) -> None:
        body = self._get_body(obj)
        if body is None:
            raise AttributeError(
                f"cannot set {self.field!r}: chunk body {self.chunk_attr!r} is None"
            )
        setattr(body, self.field, bool(value))
        for inst in self.invalidates:
            invalidator = getattr(body, f"_invalidate_{inst}", None)
            if invalidator is not None:
                try:
                    invalidator()
                except AttributeError:
                    pass
        _propagate_check(body)


class ChunkInstanceField:
    """Descriptor for a Kaitai computed instance backed by multiple fields.

    The *getter* reads the instance value directly (Kaitai computes it
    lazily from the underlying source fields).

    The *setter* calls `reverse(value)` which must return a dict mapping
    source field names to their new binary values.  After writing them
    all, every name in `invalidates` has its cached instance cleared.

    Args:
        chunk_attr: Name of the model attribute holding the chunk body.
        instance: Name of the Kaitai instance property (e.g. `"frame_rate"`).
        reverse: Callable that decomposes a user value into a dict of
            `{field_name: binary_value}` pairs.
        validate: Optional callable called with the user-facing value
            before any `reverse` transform.  Must raise `ValueError`
            or `TypeError` if the value is invalid.
        invalidates: Kaitai instance names to clear after a set.
        doc: Docstring shown on the descriptor.
    """

    def __init__(
        self,
        chunk_attr: str,
        instance: str,
        *,
        transform: Callable[..., Any] | None = None,
        reverse: Callable[..., dict[str, Any]] | None = None,
        validate: Callable[..., None] | None = None,
        invalidates: list[str] | None = None,
        doc: str | None = None,
    ) -> None:
        self.chunk_attr = chunk_attr
        self.instance = instance
        self.transform = transform
        self.reverse = reverse
        self.validate = validate
        self.invalidates = invalidates or []
        if doc is not None:
            self.__doc__ = doc

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name

    def _get_body(self, obj: Any) -> Any:
        return getattr(obj, self.chunk_attr)

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        body = self._get_body(obj)
        value = getattr(body, self.instance)
        if self.transform is not None:
            return self.transform(value)
        return value

    def __set__(self, obj: Any, value: Any) -> None:
        if self.reverse is None:
            raise AttributeError(
                f"{self.public_name!r} is read-only (no reverse transform)"
            )
        body = self._get_body(obj)
        if self.validate is not None:
            self.validate(value)
        fields = self.reverse(value)
        for field_name, field_value in fields.items():
            setattr(body, field_name, field_value)
        for inst in self.invalidates:
            invalidator = getattr(body, f"_invalidate_{inst}", None)
            if invalidator is not None:
                try:
                    invalidator()
                except AttributeError:
                    pass
        _propagate_check(body)


class ChunkEnumField:
    """Descriptor for an enum field using `from_binary` / `to_binary`.

    Args:
        chunk_attr: Name of the model attribute holding the chunk body.
        field: Name of the field on the chunk body.
        enum_class: The enum class with `from_binary()` classmethod.
        doc: Docstring shown on the descriptor.
    """

    def __init__(
        self,
        chunk_attr: str,
        field: str,
        enum_class: type,
        *,
        doc: str | None = None,
    ) -> None:
        self.chunk_attr = chunk_attr
        self.field = field
        self.enum_class = enum_class
        if doc is not None:
            self.__doc__ = doc

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name

    def _get_body(self, obj: Any) -> Any:
        return getattr(obj, self.chunk_attr)

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        body = self._get_body(obj)
        raw = getattr(body, self.field)
        return self.enum_class.from_binary(raw)

    def __set__(self, obj: Any, value: Any) -> None:
        body = self._get_body(obj)
        setattr(body, self.field, value.to_binary())
        _propagate_check(body)
