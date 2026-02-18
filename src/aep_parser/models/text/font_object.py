"""Font object model for After Effects text layers."""

from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from typing import Any

    from ..enums import CTFontTechnology, CTFontType, CTScript


@dataclass
class FontObject:
    """Provides information about a specific font.

    The Font object provides information about a specific font, along with
    the font technology used, helping disambiguate when multiple fonts
    sharing the same PostScript name are installed on the system.

    Most of these attributes simply return information which is contained in
    the font data file itself.

    Note:
        This functionality was added in After Effects 24.0.

    See: https://ae-scripting.docsforadobe.dev/text/fontobject/
    """

    post_script_name: str
    """The PostScript name of the font."""

    family_name: str | None = None
    """The family name of the font, in the ASCII character set."""

    full_name: str | None = None
    """
    The full name of the font, in the ASCII character set. Usually composed
    of the family name and the style name.
    """

    style_name: str | None = None
    """The style name of the font, in the ASCII character set."""

    version: str | None = None
    """The version number of the font."""

    location: str | None = None
    """
    The location of the font file on your system.

    Warning:
        Not guaranteed to be returned for all font types; return value may
        be empty string for some kinds of fonts.
    """

    font_id: int | None = None
    """
    A unique number assigned to the font instance when it is created, value
    is greater than or equal to 1. It never changes during the application
    session but may be different in subsequent launches of the application.

    Can be used to compare two [FontObject][] instances to see if they refer
    to the same underlying native font instance.

    Note:
        This functionality was added in After Effects 24.2.
    """

    has_design_axes: bool | None = None
    """Returns `True` if the font is a variable font."""

    is_from_adobe_fonts: bool | None = None
    """Returns `True` if the font is from Adobe Fonts."""

    is_substitute: bool | None = None
    """
    Returns `True` when this font instance represents a font reference
    which was missing on project open.
    """

    native_family_name: str | None = None
    """
    The native family name of the font in full 16-bit Unicode. Often
    different than what is returned by [family_name][] for non-Latin fonts.
    """

    native_full_name: str | None = None
    """
    The native full name of the font in full 16-bit Unicode. Often different
    than what is returned by [full_name][] for non-Latin fonts.
    """

    native_style_name: str | None = None
    """
    The native style name of the font in full 16-bit Unicode. Often
    different than what is returned by [style_name][] for non-Latin fonts.
    """

    family_prefix: str | None = None
    """
    The family prefix of the variable font. For example, the family of the
    PostScript name ``SFPro-Bold`` is ``SFPro``.

    Note:
        Will return `None` for non-variable fonts.
    """

    technology: CTFontTechnology | None = None
    """The technology used by the font."""

    type: CTFontType | None = None
    """The internal type of the font."""

    design_axes_data: list[dict[str, Any]] | None = None
    """
    The design axes data from the font. Each dict contains the axis
    ``name``, ``tag``, ``min`` value, ``max`` value, and ``default`` value.

    Note:
        Will return `None` for non-variable fonts.
    """

    design_vector: list[float] | None = None
    """
    For variable fonts, an ordered list with a length matching the number of
    design axes defined by the font.

    Note:
        Will return `None` for non-variable fonts.
    """

    writing_scripts: list[CTScript] | None = None
    """The supported character sets of the font."""
