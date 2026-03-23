"""Reusable validator factories for descriptor fields.

Each factory returns a callable `(value, instance) -> None` that raises
`ValueError` or `TypeError` when the value is invalid.  Pass the
returned callable as the `validate` parameter of a descriptor.

The `instance` argument is the model object being modified, allowing
cross-field validation (e.g. checking that one field is >= another).
"""

from __future__ import annotations

from typing import Any, Callable, Sequence


def validate_number(
    *,
    min: float | None = None,
    max: float | None = None,
    integer: bool = False,
) -> Callable[[object, Any], None]:
    """Return a validator that checks a numeric value.

    Args:
        min: Minimum allowed value (inclusive).
        max: Maximum allowed value (inclusive).
        integer: When `True`, reject non-`int` values.
    """
    type_label = "an integer" if integer else "a number"

    def _validator(value: object, instance: Any = None) -> None:
        if integer and not isinstance(value, int):
            raise TypeError(f"expected {type_label}, got {type(value).__name__}")
        try:
            if min is not None and value < min:  # type: ignore[operator]
                raise ValueError(f"must be >= {min}, got {value}")
            if max is not None and value > max:  # type: ignore[operator]
                raise ValueError(f"must be <= {max}, got {value}")
        except TypeError:
            raise TypeError(
                f"expected {type_label}, got {type(value).__name__}"
            ) from None

    return _validator


def validate_sequence(
    *,
    length: int,
    min: float | None = None,
    max: float | None = None,
    integer: bool = False,
) -> Callable[[object, Any], None]:
    """Return a validator that checks a fixed-length numeric sequence.

    Args:
        length: Required number of elements.
        min: Minimum allowed value per element (inclusive).
        max: Maximum allowed value per element (inclusive).
        integer: When `True`, reject non-`int` elements.
    """
    _element_validator = validate_number(min=min, max=max, integer=integer)

    def _validator(value: object, instance: Any = None) -> None:
        try:
            items: Sequence[object] = list(value)  # type: ignore[call-overload]
        except TypeError:
            raise TypeError(f"expected a sequence of {length} elements") from None
        if len(items) != length:
            raise ValueError(f"expected {length} elements, got {len(items)}")
        for i, v in enumerate(items):
            try:
                _element_validator(v, None)
            except (TypeError, ValueError) as exc:
                raise type(exc)(f"element [{i}] {exc}") from None

    return _validator


def validate_one_of(
    allowed: Sequence[object],
) -> Callable[[object, Any], None]:
    """Return a validator that checks value is in the allowed set.

    Args:
        allowed: Sequence of valid values.
    """
    allowed_set = set(allowed)
    formatted = ", ".join(str(v) for v in allowed)

    def _validator(value: object, instance: Any = None) -> None:
        try:
            if float(value) not in allowed_set:  # type: ignore[arg-type]
                raise ValueError(f"must be one of [{formatted}], got {value}")
        except TypeError:
            raise TypeError(f"expected a number, got {type(value).__name__}") from None

    return _validator


def validate_gte_field(
    field_name: str,
) -> Callable[[object, Any], None]:
    """Return a validator ensuring value >= another field on the instance.

    Args:
        field_name: Name of the attribute on the model instance whose
            current value is the dynamic minimum.
    """

    def _validator(value: object, instance: Any = None) -> None:
        if instance is None:
            return
        bound = getattr(instance, field_name, None)
        if bound is not None and value < bound:  # type: ignore[operator]
            raise ValueError(f"must be >= {field_name} ({bound}), got {value}")

    return _validator


def validate_all(
    *validators: Callable[[object, Any], None],
) -> Callable[[object, Any], None]:
    """Chain multiple validators into a single callable.

    Each validator is called in order; the first failure stops execution.

    Args:
        validators: Two or more validator callables.
    """

    def _validator(value: object, instance: Any = None) -> None:
        for v in validators:
            v(value, instance)

    return _validator
