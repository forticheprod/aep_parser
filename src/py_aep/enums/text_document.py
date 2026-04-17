"""Text document enumerations for After Effects.

These enums match the values used in After Effects ExtendScript.
"""

from __future__ import annotations

from enum import IntEnum


class AutoKernType(IntEnum):
    """Auto kerning type option for text characters.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentautokerntype
    """

    NO_AUTO_KERN = 11413
    METRIC_KERN = 11414
    OPTICAL_KERN = 11415


class BaselineDirection(IntEnum):
    """Baseline direction option for text characters.

    This is significant for Japanese language in vertical texts.
    `BASELINE_VERTICAL_CROSS_STREAM` is also known as Tate-Chu-Yoko.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentbaselinedirection
    """

    BASELINE_WITH_STREAM = 11612
    BASELINE_VERTICAL_ROTATED = 11613
    BASELINE_VERTICAL_CROSS_STREAM = 11614


class BoxAutoFitPolicy(IntEnum):
    """Box auto fit policy for paragraph text boxes.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentboxautofitpolicy
    """

    NONE = 0
    HEIGHT_CURSOR = 1
    HEIGHT_PRECISE_BOUNDS = 2
    HEIGHT_BASELINE = 3


class BoxFirstBaselineAlignment(IntEnum):
    """First baseline alignment for paragraph text boxes.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentboxfirstbaselinealignment
    """

    ASCENT = 0
    CAP_HEIGHT = 1
    EM_BOX = 2
    LEADING = 3
    LEGACY_METRIC = 4
    MINIMUM_VALUE_ASIAN = 5
    MINIMUM_VALUE_ROMAN = 6
    TYPO_ASCENT = 7
    X_HEIGHT = 8


class BoxVerticalAlignment(IntEnum):
    """Vertical alignment for paragraph text boxes.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentboxverticalalignment
    """

    TOP = 0
    CENTER = 1
    BOTTOM = 2
    JUSTIFY = 3


class ComposerEngine(IntEnum):
    """Text composer engine type.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentcomposerengine
    """

    LATIN_CJK_ENGINE = 10413
    UNIVERSAL_TYPE_ENGINE = 10414


class DigitSet(IntEnum):
    """Digit set option for text characters.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentdigitset
    """

    DEFAULT_DIGITS = 12012
    ARABIC_DIGITS = 12013
    HINDI_DIGITS = 12014
    FARSI_DIGITS = 12015
    ARABIC_DIGITS_RTL = 12016


class FontBaselineOption(IntEnum):
    """Font baseline option for superscript and subscript.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentfontbaselineoption
    """

    FONT_NORMAL_BASELINE = 11212
    FONT_FAUXED_SUPERSCRIPT = 11213
    FONT_FAUXED_SUBSCRIPT = 11214


class FontCapsOption(IntEnum):
    """Font caps option for text characters.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentfontcapsoption
    """

    FONT_NORMAL_CAPS = 11012
    FONT_SMALL_CAPS = 11013
    FONT_ALL_CAPS = 11014
    FONT_ALL_SMALL_CAPS = 11015


class LeadingType(IntEnum):
    """Paragraph leading type.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentleadingtype
    """

    ROMAN_LEADING_TYPE = 10812
    JAPANESE_LEADING_TYPE = 10813


class LineJoinType(IntEnum):
    """Line join type for text stroke.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentlinejointype
    """

    LINE_JOIN_MITER = 11812
    LINE_JOIN_ROUND = 11813
    LINE_JOIN_BEVEL = 11814


class LineOrientation(IntEnum):
    """Line orientation for text layers.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentlineorientation
    """

    HORIZONTAL = 13212
    VERTICAL_RIGHT_TO_LEFT = 13213
    VERTICAL_LEFT_TO_RIGHT = 13214


class ParagraphDirection(IntEnum):
    """Paragraph direction for text layers.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentdirection
    """

    DIRECTION_LEFT_TO_RIGHT = 10212
    DIRECTION_RIGHT_TO_LEFT = 10213


class ParagraphJustification(IntEnum):
    """Paragraph justification for text layers.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/#textdocumentjustification
    """

    MULTIPLE_JUSTIFICATIONS = 7412
    LEFT_JUSTIFY = 7413
    RIGHT_JUSTIFY = 7414
    CENTER_JUSTIFY = 7415
    FULL_JUSTIFY_LASTLINE_LEFT = 7416
    FULL_JUSTIFY_LASTLINE_RIGHT = 7417
    FULL_JUSTIFY_LASTLINE_CENTER = 7418
    FULL_JUSTIFY_LASTLINE_FULL = 7419
