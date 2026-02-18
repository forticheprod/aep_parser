"""Resolvers module - business logic for computing derived values.

This module contains functions that compute derived values from parsed
model data. Models remain pure data containers; resolvers perform the
computation.
"""

from __future__ import annotations

from .output import resolve_output_filename

__all__ = [
    "resolve_output_filename",
]
