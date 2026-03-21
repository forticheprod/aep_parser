"""Descriptors for chunk-backed model fields.

Each descriptor reads from / writes to a Kaitai chunk body attribute,
so that modifying a model field directly mutates the underlying binary
data and `Project.save()` persists the change.

After every `__set__`, `propagate_check` walks the Kaitai
parent chain bottom-up: it calls `_check()` on each object (clearing
the `_dirty` flag) and updates every ancestor `Chunk.len_data` when
the body's serialized size has changed.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar, overload

from .utils import propagate_check

T = TypeVar("T")

_SENTINEL = object()


def _invalidate(body: Any, names: list[str]) -> None:
    """Clear cached Kaitai instances so they recompute on next access."""
    for name in names:
        invalidator = getattr(body, f"_invalidate_{name}", None)
        if invalidator is not None:
            try:
                invalidator()
            except AttributeError:
                pass


class ChunkField(Generic[T]):
    """Descriptor that proxies a single field on a chunk body.

    Args:
        chunk_attr: Name of the model attribute holding the chunk body
            reference (e.g. `"_cdta"`).
        field: Name of the field on the chunk body (e.g. `"width"`).
        transform: Optional callable applied when *getting* (binary ->
            user-facing value).
        reverse: Callable applied when *setting* (user-facing -> binary
            value). Defaults to ``None`` (read-only). Pass a callable
            (e.g. ``int``) to make the field writable.
        validate: Optional callable called with the user-facing value
            before any `reverse` transform. Must raise `ValueError`
            or `TypeError` if the value is invalid.
        invalidates: Kaitai instance names to clear after a set so they
            are recomputed on next access.
        default: Optional default value returned when the chunk body is
            `None`. If not given, accessing the field when the body is `None`
            raises `AttributeError`.
    """

    def __init__(
        self,
        chunk_attr: str,
        field: str,
        *,
        transform: Callable[..., Any] | None = None,
        reverse: Callable[..., Any] | None = None,
        validate: Callable[..., None] | None = None,
        invalidates: list[str] | None = None,
        default: Any = _SENTINEL,
    ) -> None:
        self.chunk_attr = chunk_attr
        self.field = field
        self.transform = transform
        self.reverse = reverse
        self.validate = validate
        self.invalidates = invalidates or []
        self.default = default

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name

    @overload
    def __get__(self, obj: None, objtype: type) -> ChunkField[T]: ...

    @overload
    def __get__(self, obj: Any, objtype: type | None = None) -> T: ...

    def __get__(self, obj: Any, objtype: type | None = None) -> T | ChunkField[T]:
        if obj is None:
            return self
        body = getattr(obj, self.chunk_attr)
        if body is None:
            if self.default is not _SENTINEL:
                return self.default  # type: ignore[no-any-return,return-value]
            raise AttributeError(f"chunk body {self.chunk_attr!r} is None")
        value = getattr(body, self.field)
        return self.transform(value) if self.transform else value  # type: ignore[no-any-return,return-value]

    def __set__(self, obj: Any, value: T) -> None:
        if self.reverse is None:
            raise AttributeError(f"{self.public_name!r} is read-only.")
        body = getattr(obj, self.chunk_attr)
        if self.validate:
            self.validate(value, obj)
        value = self.reverse(value)
        setattr(body, self.field, value)
        _invalidate(body, self.invalidates)
        propagate_check(body)


class ChunkInstanceField(Generic[T]):
    """Descriptor for a Kaitai computed instance backed by multiple fields.

    The *getter* reads the instance value directly (Kaitai computes it
    lazily from the underlying source fields).

    The *setter* calls `reverse(value)` which must return a dict mapping
    source field names to their new binary values. After writing them all,
    every name in `invalidates` has its cached instance cleared.

    Args:
        chunk_attr: Name of the model attribute holding the chunk body.
        instance: Name of the Kaitai instance property (e.g. `"frame_rate"`).
        reverse: Callable that decomposes a user value into a dict of
            `{field_name: binary_value}` pairs.
        validate: Optional callable called with the user-facing value
            before any `reverse` transform. Must raise `ValueError`
            or `TypeError` if the value is invalid.
        invalidates: Kaitai instance names to clear after a set.
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
    ) -> None:
        self.chunk_attr = chunk_attr
        self.instance = instance
        self.transform = transform
        self.reverse = reverse
        self.validate = validate
        self.invalidates = invalidates or []

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name

    @overload
    def __get__(self, obj: None, objtype: type) -> ChunkInstanceField[T]: ...

    @overload
    def __get__(self, obj: Any, objtype: type | None = None) -> T: ...

    def __get__(
        self, obj: Any, objtype: type | None = None
    ) -> T | ChunkInstanceField[T]:
        if obj is None:
            return self
        body = getattr(obj, self.chunk_attr)
        value = getattr(body, self.instance)
        return self.transform(value) if self.transform else value  # type: ignore[no-any-return,return-value]

    def __set__(self, obj: Any, value: T) -> None:
        if self.reverse is None:
            raise AttributeError(f"{self.public_name!r} is read-only.")
        body = getattr(obj, self.chunk_attr)
        if self.validate:
            self.validate(value, obj)
        for field_name, field_value in self.reverse(value, body).items():
            setattr(body, field_name, field_value)
        _invalidate(body, self.invalidates)
        propagate_check(body)
