"""Parse COS (Carousel Object Structure) text data into text models.

Transforms the dict returned by :class:`~aep_parser.cos.CosParser` for a
``btdk`` chunk into :class:`~aep_parser.models.text.TextDocument` and
:class:`~aep_parser.models.text.FontObject` instances.

The COS data layout follows the structure documented in the
`lottie-docs AEP reference
<https://github.com/nickt/lottie-docs/blob/main/docs/aep.md#list-btdk>`_.

Fonts
-----
``data["0"]["1"]["0"]`` contains an array of available fonts.  Each entry
carries a ``CoolTypeFont`` marker and exposes PostScript name, version, and
a flag at well-known sub-keys.

Text documents
--------------
``data["1"]["1"]`` is an array of text documents (one per keyframe).  Inside
each document:

* ``doc["0"]["0"]`` — the text string
* ``doc["0"]["5"]["0"]`` — array of paragraph style runs
* ``doc["0"]["6"]["0"]`` — array of character style runs

Default styles live at ``data["1"]["2"]`` (character) and
``data["1"]["3"]`` (paragraph).
"""

from __future__ import annotations

import logging
from typing import Any

from ..models.enums import (
    AutoKernType,
    FontBaselineOption,
    FontCapsOption,
    LeadingType,
    ParagraphJustification,
)
from ..models.text.font_object import FontObject
from ..models.text.text_document import TextDocument

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper — safe nested dict/list access
# ---------------------------------------------------------------------------


def _g(data: Any, *keys: str | int) -> Any:
    """Safely traverse a nested dict/list by successive keys.

    Each key is tried as a dict string key first and then as a list index.
    Returns ``None`` when any step along the path is missing.

    Example::

        _g(data, "1", "1", 0, "0", "0")  # -> text string
    """
    cur: Any = data
    for key in keys:
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(str(key))
        elif isinstance(cur, list):
            try:
                cur = cur[int(key)]
            except (IndexError, ValueError, TypeError):
                return None
        else:
            return None
    return cur


# ---------------------------------------------------------------------------
# Font parsing
# ---------------------------------------------------------------------------

def parse_fonts(cos_data: dict[str, Any]) -> list[FontObject]:
    """Parse font entries from COS data.

    Reads the font array at ``cos_data["0"]["1"]["0"]``.  Each font entry
    is a dict with structure::

        entry["0"]["0"]["0"]  -> PostScript name (str)
        entry["0"]["0"]["2"]  -> flag (int, 0 or 1)
        entry["0"]["0"]["5"]  -> version string (optional)
        entry["0"]["99"]      -> "CoolTypeFont" marker

    Args:
        cos_data: The parsed COS dict from a ``btdk`` chunk.

    Returns:
        List of [FontObject][] instances in the same order as the COS
        array (the index is referenced by character styles).
    """
    font_array = _g(cos_data, "0", "1", "0")
    if not font_array or not isinstance(font_array, list):
        return []

    fonts: list[FontObject] = []
    for entry in font_array:
        ps_name = _g(entry, "0", "0", "0")
        if ps_name is None:
            continue
        version = _g(entry, "0", "0", "5")
        font = FontObject(
            post_script_name=str(ps_name),
            version=str(version) if version is not None else None,
        )
        fonts.append(font)

    return fonts


# ---------------------------------------------------------------------------
# Paragraph style mapping (keys inside the paragraph style dict)
# ---------------------------------------------------------------------------

_JUSTIFICATION_MAP: dict[int, ParagraphJustification] = {
    0: ParagraphJustification.LEFT_JUSTIFY,
    1: ParagraphJustification.RIGHT_JUSTIFY,
    2: ParagraphJustification.CENTER_JUSTIFY,
    3: ParagraphJustification.FULL_JUSTIFY_LASTLINE_LEFT,
    4: ParagraphJustification.FULL_JUSTIFY_LASTLINE_RIGHT,
    5: ParagraphJustification.FULL_JUSTIFY_LASTLINE_CENTER,
    6: ParagraphJustification.FULL_JUSTIFY_LASTLINE_FULL,
}


def _parse_paragraph_style(
    style: dict[str, Any] | None,
) -> dict[str, Any]:
    """Extract paragraph-level attributes from a COS paragraph style dict.

    The style dict uses numeric string keys.  Documented keys:

    ====  ==============================
    Key   Meaning
    ====  ==============================
    0     Justification (alignment)
    1     First line indent
    2     Start indent
    3     End indent
    4     Space before
    5     Space after
    6     Auto leading (bool-ish int)
    7     Leading amount / ratio
    9     Auto hyphenate (bool)
    15    Every-line composer (bool)
    21    Hanging roman (bool)
    ====  ==============================

    Returns:
        Dict of keyword arguments suitable for :class:`TextDocument`.
    """
    if not style or not isinstance(style, dict):
        return {}

    result: dict[str, Any] = {}

    # Justification (key 0)
    align_val = style.get("0")
    if isinstance(align_val, int) and align_val in _JUSTIFICATION_MAP:
        result["justification"] = _JUSTIFICATION_MAP[align_val]

    # Paragraph spacing / indents (keys 1–5)
    first_indent = style.get("1")
    if isinstance(first_indent, (int, float)):
        result["first_line_indent"] = float(first_indent)

    start_indent = style.get("2")
    if isinstance(start_indent, (int, float)):
        result["start_indent"] = float(start_indent)

    end_indent = style.get("3")
    if isinstance(end_indent, (int, float)):
        result["end_indent"] = float(end_indent)

    space_before = style.get("4")
    if isinstance(space_before, (int, float)):
        result["space_before"] = float(space_before)

    space_after = style.get("5")
    if isinstance(space_after, (int, float)):
        result["space_after"] = float(space_after)

    # Auto leading (key 6 — int acting as bool)
    auto_leading = style.get("6")
    if isinstance(auto_leading, (int, bool)):
        result["auto_leading"] = bool(auto_leading)

    # Leading type (key 8 — maps to LeadingType enum)
    leading_type_val = style.get("8")
    if isinstance(leading_type_val, int):
        try:
            result["leading_type"] = LeadingType(leading_type_val)
        except ValueError:
            pass

    # Auto hyphenate (key 9)
    auto_hyph = style.get("9")
    if isinstance(auto_hyph, (bool, int)):
        result["auto_hyphenate"] = bool(auto_hyph)

    # Every-line composer (key 15)
    every_line = style.get("15")
    if isinstance(every_line, (bool, int)):
        result["every_line_composer"] = bool(every_line)

    # Hanging roman punctuation (key 21)
    hanging = style.get("21")
    if isinstance(hanging, (bool, int)):
        result["hanging_roman"] = bool(hanging)

    return result


# ---------------------------------------------------------------------------
# Character style mapping (keys inside the character style dict)
# ---------------------------------------------------------------------------


def _parse_color(paint: Any) -> list[float] | None:
    """Extract an RGB colour from a COS ``SimplePaint`` structure.

    The paint structure contains ``{"0": {"0": flag, "1": [A, R, G, B]},
    "99": "SimplePaint"}``.  Returns ``[R, G, B]`` or ``None``.
    """
    argb = _g(paint, "0", "1")
    if isinstance(argb, list) and len(argb) >= 4:
        return [float(argb[1]), float(argb[2]), float(argb[3])]
    return None


def _parse_char_style(
    style: dict[str, Any] | None,
    fonts: list[FontObject],
) -> dict[str, Any]:
    """Extract character-level attributes from a COS character style dict.

    The style dict uses numeric string keys.  The mapping below is derived
    from the `lottie-docs AEP reference`_ (documented keys) and from
    empirical analysis of real AEP files (inferred keys).

    Documented keys (lottie-docs)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ======  ===================================
    Key     Field
    ======  ===================================
    0       Font index (into font array)
    1       ``font_size``
    2       ``faux_bold``
    3       ``faux_italic``
    12      ``font_caps_option``
    13      ``font_baseline_option``
    53.0.1  ``fill_color`` (ARGB [0, 1])
    54.0.1  ``stroke_color`` (ARGB [0, 1])
    57      ``apply_stroke`` (stroke enabled)
    58      ``stroke_over_fill``
    63      ``stroke_width``
    ======  ===================================

    Inferred keys (from empirical analysis)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ======  ===================================
    Key     Field
    ======  ===================================
    4       ``apply_fill``
    5       ``tracking``
    6       ``horizontal_scale``
    7       ``vertical_scale``
    8       ``auto_kern_type``
    9       ``baseline_shift``
    10      ``leading`` (line spacing)
    11      ``leading_type``
    17      ``tsume``
    35      ``baseline_direction``
    56      ``apply_fill`` (near stroke keys)
    ======  ===================================

    Args:
        style: The character style dict (numeric string keys).
        fonts: The parsed font list (used to resolve font index).

    Returns:
        Dict of keyword arguments suitable for :class:`TextDocument`.
    """
    if not style or not isinstance(style, dict):
        return {}

    result: dict[str, Any] = {}

    # Font (key 0 — index into the font array)
    font_idx = style.get("0")
    if isinstance(font_idx, int) and 0 <= font_idx < len(fonts):
        font_obj = fonts[font_idx]
        result["font"] = font_obj.post_script_name
        result["font_object"] = font_obj

    # Font size (key 1)
    font_size = style.get("1")
    if isinstance(font_size, (int, float)):
        result["font_size"] = float(font_size)

    # Faux bold / italic (keys 2, 3)
    faux_bold = style.get("2")
    if isinstance(faux_bold, (bool, int)):
        result["faux_bold"] = bool(faux_bold)

    faux_italic = style.get("3")
    if isinstance(faux_italic, (bool, int)):
        result["faux_italic"] = bool(faux_italic)

    # Apply fill (key 56 — near stroke keys 53/54/57/58)
    apply_fill = style.get("56")
    if isinstance(apply_fill, (bool, int)):
        result["apply_fill"] = bool(apply_fill)

    # Tracking (key 5)
    tracking = style.get("5")
    if isinstance(tracking, (int, float)):
        result["tracking"] = float(tracking)

    # Horizontal / vertical scale (keys 6, 7)
    hscale = style.get("6")
    if isinstance(hscale, (int, float)):
        result["horizontal_scale"] = float(hscale)

    vscale = style.get("7")
    if isinstance(vscale, (int, float)):
        result["vertical_scale"] = float(vscale)

    # Auto kern type (key 8)
    kern_val = style.get("8")
    if isinstance(kern_val, int):
        try:
            result["auto_kern_type"] = AutoKernType(kern_val)
        except ValueError:
            pass

    # Baseline shift (key 9)
    bshift = style.get("9")
    if isinstance(bshift, (int, float)):
        result["baseline_shift"] = float(bshift)

    # Leading (key 10)
    leading = style.get("10")
    if isinstance(leading, (int, float)):
        result["leading"] = float(leading)

    # Leading type (key 11)
    leading_type_val = style.get("11")
    if isinstance(leading_type_val, int):
        try:
            result["leading_type"] = LeadingType(leading_type_val)
        except ValueError:
            pass

    # Font caps option (key 12: 0=Normal, 1=SmallCaps, 2=AllCaps)
    caps_val = style.get("12")
    if isinstance(caps_val, int):
        try:
            result["font_caps_option"] = FontCapsOption(caps_val)
            result["all_caps"] = caps_val == FontCapsOption.FONT_ALL_CAPS
            result["small_caps"] = caps_val == FontCapsOption.FONT_SMALL_CAPS
        except ValueError:
            pass

    # Font baseline option (key 13: 0=Normal, 1=Super, 2=Sub)
    baseline_val = style.get("13")
    if isinstance(baseline_val, int):
        try:
            result["font_baseline_option"] = FontBaselineOption(baseline_val)
            result["superscript"] = (
                baseline_val == FontBaselineOption.FONT_FAUXED_SUPERSCRIPT
            )
            result["subscript"] = (
                baseline_val == FontBaselineOption.FONT_FAUXED_SUBSCRIPT
            )
        except ValueError:
            pass

    # Tsume (key 17)
    tsume = style.get("17")
    if isinstance(tsume, (int, float)):
        result["tsume"] = float(tsume)

    # Fill color (key 53 → SimplePaint with ARGB)
    fill_paint = style.get("53")
    fill_color = _parse_color(fill_paint)
    if fill_color is not None:
        result["fill_color"] = fill_color

    # Stroke color (key 54 → SimplePaint with ARGB)
    stroke_paint = style.get("54")
    stroke_color = _parse_color(stroke_paint)
    if stroke_color is not None:
        result["stroke_color"] = stroke_color

    # Apply stroke (key 57 — "Stroke enabled")
    apply_stroke_val = style.get("57")
    if isinstance(apply_stroke_val, (bool, int)):
        result["apply_stroke"] = bool(apply_stroke_val)

    # Stroke over fill (key 58)
    stroke_over_fill = style.get("58")
    if isinstance(stroke_over_fill, (bool, int)):
        result["stroke_over_fill"] = bool(stroke_over_fill)

    # Stroke width (key 63)
    stroke_width = style.get("63")
    if isinstance(stroke_width, (int, float)):
        result["stroke_width"] = float(stroke_width)

    return result


# ---------------------------------------------------------------------------
# Text document parsing
# ---------------------------------------------------------------------------


def _get_first_char_style(doc: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first character style dict from a text document entry.

    Path: ``doc["0"]["6"]["0"][0]["0"]["0"]["6"]``
    """
    return _g(doc, "0", "6", "0", 0, "0", "0", "6")


def _get_first_para_style(doc: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first paragraph style dict from a text document entry.

    Path: ``doc["0"]["5"]["0"][0]["0"]["0"]["5"]``
    """
    return _g(doc, "0", "5", "0", 0, "0", "0", "5")


def parse_text_documents(
    cos_data: dict[str, Any],
    fonts: list[FontObject],
) -> list[TextDocument]:
    """Parse text documents from COS data.

    Reads the document array at ``cos_data["1"]["1"]``.  Each entry is
    a dict with structure::

        entry["0"]["0"]              -> text string
        entry["0"]["5"]["0"]         -> paragraph style runs
        entry["0"]["6"]["0"]         -> character style runs

    For each document the *first* character style and *first* paragraph
    style are extracted and mapped onto :class:`TextDocument` attributes,
    matching the ExtendScript API semantics where most properties "only
    reflect the first character".

    Args:
        cos_data: The parsed COS dict from a ``btdk`` chunk.
        fonts: The list of :class:`FontObject` parsed by
            :func:`parse_fonts` (font indices reference this list).

    Returns:
        List of :class:`TextDocument` instances (one per keyframe).
    """
    doc_array = _g(cos_data, "1", "1")
    if not doc_array or not isinstance(doc_array, list):
        return []

    documents: list[TextDocument] = []

    for doc_entry in doc_array:
        # Text content
        text = _g(doc_entry, "0", "0")
        if text is None:
            text = ""
        text = str(text)

        # Start with text
        kwargs: dict[str, Any] = {"text": text}

        # First character style → most TextDocument char-level attributes
        char_style = _get_first_char_style(doc_entry)
        kwargs.update(_parse_char_style(char_style, fonts))

        # First paragraph style → paragraph-level attributes
        para_style = _get_first_para_style(doc_entry)
        kwargs.update(_parse_paragraph_style(para_style))

        # Compute paragraph count from paragraph style runs
        para_runs = _g(doc_entry, "0", "5", "0")
        if isinstance(para_runs, list):
            kwargs["paragraph_count"] = len(para_runs)

        documents.append(TextDocument(**kwargs))

    return documents


# ---------------------------------------------------------------------------
# High-level entry point
# ---------------------------------------------------------------------------


def parse_btdk_cos(
    cos_data: dict[str, Any],
) -> tuple[list[TextDocument], list[FontObject]]:
    """Parse a btdk COS dict into text documents and fonts.

    This is the main entry point called by
    :func:`~aep_parser.parsers.property.parse_text_document`.

    Args:
        cos_data: The parsed COS dict from a ``btdk`` chunk (the return
            value of :meth:`~aep_parser.cos.CosParser.parse`).

    Returns:
        A tuple ``(text_documents, fonts)`` where *text_documents* is a
        list of :class:`TextDocument` (one per keyframe) and *fonts* is
        the list of :class:`FontObject` referenced by the documents.
    """
    fonts = parse_fonts(cos_data)
    documents = parse_text_documents(cos_data, fonts)
    return documents, fonts
