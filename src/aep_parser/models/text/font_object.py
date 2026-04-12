"""Font object model for After Effects text layers."""

from __future__ import annotations

import typing

from ...cos.descriptors import CosField

if typing.TYPE_CHECKING:
    from typing import Any


class FontObject:
    """Provides information about a specific font.

    The Font object provides information about a specific font, along with
    the font technology used, helping disambiguate when multiple fonts
    sharing the same PostScript name are installed on the system.

    Example:
        ```python
        from aep_parser import parse

        app = parse("project.aep")
        comp = app.project.compositions[0]
        font = comp.text_layers[0].text.source_text.value.font_object
        print(font.post_script_name)
        ```

    Note:
        This functionality was added in After Effects 24.0.

    See: https://ae-scripting.docsforadobe.dev/text/fontobject/
    """

    post_script_name: str = CosField("_font_data", "0", transform=str, default="")  # type: ignore[assignment]
    """The PostScript name of the font. Read-only."""

    version: str | None = CosField("_font_data", "5", transform=str)  # type: ignore[assignment]
    """The version number of the font. Read-only."""

    def __init__(
        self,
        *,
        _font_data: dict[str, Any] | None = None,
        _font_entry: dict[str, Any] | None = None,
        post_script_name: str | None = None,
        version: str | None = None,
    ) -> None:
        self._font_data = _font_data
        self._font_entry = _font_entry
        if post_script_name is not None:
            self.__dict__["post_script_name"] = post_script_name
        if version is not None:
            self.__dict__["version"] = version
