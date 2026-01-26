"""aep_parser - A .aep (After Effects Project) parser."""

from __future__ import annotations

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # type: ignore[import,no-redef]  # Python 3.7

from .models.project import Project
from .parsers.project import parse_project

try:
    __version__ = version("aep_parser")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "parse_project",
    "Project",
]
