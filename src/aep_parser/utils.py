"""General-purpose utilities for aep_parser."""

from __future__ import annotations

import functools
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any, Callable, TypeVar

R = TypeVar("R")


def fs_timeout(
    timeout: float = 2.0,
    default: Any = None,
) -> Callable[..., Any]:
    """Decorator that guards a function against hanging on filesystem I/O.

    Runs the decorated function in a thread with a timeout. Returns
    ``default`` if the call exceeds ``timeout`` seconds or raises an
    `OSError`.

    Args:
        timeout: Maximum seconds to wait before returning the default.
        default: Value returned on timeout or `OSError`.
    """

    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            with ThreadPoolExecutor(max_workers=1) as pool:
                try:
                    return pool.submit(func, *args, **kwargs).result(
                        timeout=timeout
                    )
                except (TimeoutError, OSError):
                    return default  # type: ignore[return-value, no-any-return]

        return wrapper

    return decorator
