from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from .view_options import ViewOptions


@dataclass
class View:
    """
    The `View` object represents a specific view.

    See: https://ae-scripting.docsforadobe.dev/other/view/
    """

    options: ViewOptions
    """Options object for this View."""
