"""Reusable validator factories for descriptor fields.

Each factory returns a callable `(value) -> None` that raises
`ValueError` or `TypeError` when the value is invalid.  Pass the
returned callable as the `validate` parameter of a descriptor.
"""

from __future__ import annotations

from typing import Callable, Sequence


def validate_number(
    *,
    min: float | None = None,
    max: float | None = None,
    integer: bool = False,
) -> Callable[[object], None]:
    """Return a validator that checks a numeric value.

    Args:
        min: Minimum allowed value (inclusive).
        max: Maximum allowed value (inclusive).
        integer: When `True`, reject non-`int` values.
    """
    type_label = "an integer" if integer else "a number"

    def _validator(value: object) -> None:
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
) -> Callable[[object], None]:
    """Return a validator that checks a fixed-length numeric sequence.

    Args:
        length: Required number of elements.
        min: Minimum allowed value per element (inclusive).
        max: Maximum allowed value per element (inclusive).
    """

    def _validator(value: object) -> None:
        try:
            items: Sequence[object] = list(value)  # type: ignore[arg-type]
        except TypeError:
            raise TypeError(
                f"expected a sequence of {length} elements"
            ) from None
        if len(items) != length:
            raise ValueError(
                f"expected {length} elements, got {len(items)}"
            )
        for i, v in enumerate(items):
            try:
                if min is not None and v < min:  # type: ignore[operator]
                    raise ValueError(
                        f"element [{i}] must be >= {min}, got {v}"
                    )
                if max is not None and v > max:  # type: ignore[operator]
                    raise ValueError(
                        f"element [{i}] must be <= {max}, got {v}"
                    )
            except TypeError:
                raise TypeError(
                    f"element [{i}] must be a number, "
                    f"got {type(v).__name__}"
                ) from None

    return _validator


def validate_one_of(
    allowed: Sequence[object],
) -> Callable[[object], None]:
    """Return a validator that checks value is in the allowed set.

    Args:
        allowed: Sequence of valid values.
    """
    allowed_set = set(allowed)
    formatted = ", ".join(str(v) for v in allowed)

    def _validator(value: object) -> None:
        try:
            if float(value) not in allowed_set:  # type: ignore[arg-type]
                raise ValueError(
                    f"must be one of [{formatted}], got {value}"
                )
        except TypeError:
            raise TypeError(
                f"expected a number, got {type(value).__name__}"
            ) from None

    return _validator
