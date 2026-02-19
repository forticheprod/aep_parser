"""TextDocument model for After Effects text layers."""

from __future__ import annotations

import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from ..enums import (
        AutoKernType,
        BaselineDirection,
        BoxAutoFitPolicy,
        BoxFirstBaselineAlignment,
        BoxVerticalAlignment,
        ComposerEngine,
        DigitSet,
        FontBaselineOption,
        FontCapsOption,
        LeadingType,
        LineJoinType,
        LineOrientation,
        ParagraphDirection,
        ParagraphJustification,
    )
    from .font_object import FontObject


@dataclass
class TextDocument:
    """Stores a value for a TextLayer's Source Text property.

    See: https://ae-scripting.docsforadobe.dev/text/textdocument/
    """

    text: str = ""
    """The text value for the Text layer's Source Text property."""

    all_caps: bool | None = None
    """
    `True` if a Text layer has All Caps enabled; otherwise `False`.
    To set this value, use [font_caps_option][TextDocument.font_caps_option].

    Note:
        This functionality was added in After Effects 13.2 (CC 2014.2).

    Warning:
        This value only reflects the first character in the Text layer.
    """

    apply_fill: bool | None = None
    """
    When `True`, the Text layer shows a fill. Access the
    [fill_color][TextDocument.fill_color] attribute for the actual color.
    When `False`, only a stroke is shown.
    """

    apply_stroke: bool | None = None
    """
    When `True`, the Text layer shows a stroke. Access the
    [stroke_color][TextDocument.stroke_color] attribute for the actual color
    and [stroke_width][TextDocument.stroke_width] for its thickness. When
    `False`, only a fill is shown.
    """

    auto_hyphenate: bool | None = None
    """
    The Text layer's auto hyphenate paragraph option.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    auto_leading: bool | None = None
    """
    The Text layer's auto leading character option.

    If this attribute has a mixed value, it will be read as `None`.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    auto_kern_type: AutoKernType | None = None
    """
    The Text layer's auto kern type option.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    baseline_direction: BaselineDirection | None = None
    """
    The Text layer's baseline direction option. This is significant for
    Japanese language in vertical texts.
    ``BASELINE_VERTICAL_CROSS_STREAM`` is also known as Tate-Chu-Yoko.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    baseline_locs: list[float] | None = None
    """
    The baseline (x, y) locations for a Text layer. Line wraps in a
    paragraph text box are treated as multiple lines.

    The array contains groups of four floats per line:
    ``[line0.start_x, line0.start_y, line0.end_x, line0.end_y, ...]``.

    Note:
        This functionality was added in After Effects 13.6 (CC 2015).

    Tip:
        If a line has no characters, the x and y values for start and end
        will be the maximum float value (``3.402823466e+38``).
    """

    baseline_shift: float | None = None
    """
    This Text layer's baseline shift in pixels.

    Note:
        This functionality was added in After Effects 13.2 (CC 2014.2).

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    box_auto_fit_policy: BoxAutoFitPolicy | None = None
    """
    Enables the automated change of the box height to fit the text content
    in the box. The box only grows down.

    Defaults to ``BoxAutoFitPolicy.NONE``.

    Will be disabled if
    [box_vertical_alignment][TextDocument.box_vertical_alignment] is
    anything other than ``BoxVerticalAlignment.TOP``.

    Note:
        This functionality was added in After Effects 24.6.
    """

    box_first_baseline_alignment: BoxFirstBaselineAlignment | None = None
    """
    Controls the position of the first line of composed text relative to
    the top of the box.

    Disabled if
    [box_first_baseline_alignment_minimum][TextDocument.box_first_baseline_alignment_minimum]
    is anything other than zero.

    Defaults to ``BoxFirstBaselineAlignment.ASCENT``.

    Note:
        This functionality was added in After Effects 24.6.
    """

    box_first_baseline_alignment_minimum: float | None = None
    """
    Manually controls the position of the first line of composed text
    relative to the top of the box.

    A value set here other than zero will override the effect of the
    [box_first_baseline_alignment][TextDocument.box_first_baseline_alignment]
    value. Defaults to zero.

    Note:
        This functionality was added in After Effects 24.6.
    """

    box_inset_spacing: float | None = None
    """
    Controls the inner space between the box bounds and where the
    composable text box begins. The same value is applied to all four sides
    of the box. Defaults to zero.

    Note:
        This functionality was added in After Effects 24.6.
    """

    box_overflow: bool | None = None
    """
    Returns `True` if some part of the text did not compose into the box.

    Note:
        This functionality was added in After Effects 24.6.
    """

    box_text: bool | None = None
    """
    `True` if a Text layer is a layer of paragraph (bounded) text;
    otherwise `False`.
    """

    box_text_pos: list[float] | None = None
    """
    The layer coordinates from a paragraph (box) Text layer's anchor point
    as a ``[width, height]`` array of pixel dimensions.

    Note:
        This functionality was added in After Effects 13.2 (CC 2014.2).

    Warning:
        Only valid when [box_text][TextDocument.box_text] is `True`.
    """

    box_text_size: list[int] | None = None
    """
    The size of a paragraph (box) Text layer as a ``[width, height]`` array
    of pixel dimensions.

    Warning:
        Only valid when [box_text][TextDocument.box_text] is `True`.
    """

    box_vertical_alignment: BoxVerticalAlignment | None = None
    """
    Enables the automated vertical alignment of the composed text in the
    box. Defaults to ``BoxVerticalAlignment.TOP``.

    Note:
        This functionality was added in After Effects 24.6.
    """

    composed_line_count: int | None = None
    """
    The number of composed lines in the Text layer, may be zero if all text
    is overset.

    The [TextDocument][] instance is initialized from the composed state
    and subsequent changes to the [TextDocument][] instance does not cause
    recomposition. Even if you remove all the text from the [TextDocument][]
    instance, the value returned here remains unchanged.
    """

    composer_engine: ComposerEngine | None = None
    """
    The Text layer's paragraph composer engine option. By default new Text
    layers will use ``ComposerEngine.UNIVERSAL_TYPE_ENGINE``; the other
    enum value will only be encountered in projects created before the
    Universal Type Engine became the default in After Effects 22.1.1.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    digit_set: DigitSet | None = None
    """
    The Text layer's digit set option.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    direction: ParagraphDirection | None = None
    """
    The Text layer's paragraph direction option.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    end_indent: float | None = None
    """
    The Text layer's paragraph end indent option.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    every_line_composer: bool | None = None
    """
    The Text layer's Every-Line Composer paragraph option. If set to
    `False`, the [TextDocument][] will use the Single-Line Composer.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    faux_bold: bool | None = None
    """
    `True` if a Text layer has faux bold enabled; otherwise `False`.

    Note:
        The read functionality was added in After Effects 13.2 (CC 2014.2).
        The write functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    faux_italic: bool | None = None
    """
    `True` if a Text layer has faux italic enabled; otherwise `False`.

    Note:
        The read functionality was added in After Effects 13.2 (CC 2014.2).
        The write functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    fill_color: list[float] | None = None
    """
    The Text layer's fill color, as an array of ``[r, g, b]``
    floating-point values. For example, in an 8-bpc project, a red value
    of 255 would be 1.0, and in a 32-bpc project, an overbright blue value
    can be something like 3.2.

    Setting this value will also set
    [apply_fill][TextDocument.apply_fill] to `True` across the affected
    characters.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    first_line_indent: float | None = None
    """
    The Text layer's paragraph first line indent option.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    font: str | None = None
    """
    The Text layer's font specified by its PostScript name.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    font_baseline_option: FontBaselineOption | None = None
    """
    The Text layer's font baseline option. This is for setting a
    [TextDocument][] to superscript or subscript.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    font_caps_option: FontCapsOption | None = None
    """
    The Text layer's font caps option.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    font_family: str | None = None
    """
    The name of the font family.

    Note:
        This functionality was added in After Effects 13.1 (CC 2014.1).

    Warning:
        This value only reflects the first character in the Text layer.
    """

    font_location: str | None = None
    """
    Path of font file, providing its location on disk.

    Note:
        This functionality was added in After Effects 13.1 (CC 2014.1).

    Warning:
        Not guaranteed to be returned for all font types; return value may
        be empty string for some kinds of fonts.

    Warning:
        This value only reflects the first character in the Text layer.
    """

    font_object: FontObject | None = None
    """
    The Text layer's [FontObject][] specified by its PostScript name.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer.
    """

    font_size: float | None = None
    """
    The Text layer's font size in pixels.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    font_style: str | None = None
    """
    Style information, e.g., "bold", "italic".

    Note:
        This functionality was added in After Effects 13.1 (CC 2014.1).

    Warning:
        This value only reflects the first character in the Text layer.
    """

    hanging_roman: bool | None = None
    """
    The Text layer's Roman Hanging Punctuation paragraph option. This is
    only meaningful to box Text layers -- it allows punctuation to fit
    outside the box rather than flow to the next line.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    horizontal_scale: float | None = None
    """
    This Text layer's horizontal scale in pixels.

    Note:
        This functionality was added in After Effects 13.2 (CC 2014.2).

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    justification: ParagraphJustification | None = None
    """
    The paragraph justification for the Text layer.

    Text layers with mixed justification values will be read as
    ``ParagraphJustification.MULTIPLE_JUSTIFICATIONS``.

    Setting a [TextDocument][] to use
    ``ParagraphJustification.MULTIPLE_JUSTIFICATIONS`` will result in
    ``ParagraphJustification.CENTER_JUSTIFY`` instead.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    kerning: int | None = None
    """
    The Text layer's kerning option.

    Returns zero for ``AutoKernType.METRIC_KERN`` and
    ``AutoKernType.OPTICAL_KERN``.

    Setting this value will also set ``AutoKernType.NO_AUTO_KERN`` to
    `True` across the affected characters.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    leading: float | None = None
    """
    The Text layer's spacing between lines.

    Returns zero if [auto_leading][TextDocument.auto_leading] is `True`.

    Setting this value will also set
    [auto_leading][TextDocument.auto_leading] to `True` across the
    affected characters.

    Note:
        This functionality was added in After Effects 14.2 (CC 2017.1).

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting. The minimum accepted value to set is 0,
        but this will be silently clipped to 0.01.
    """

    leading_type: LeadingType | None = None
    """
    The Text layer's paragraph leading type option.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    ligature: bool | None = None
    """
    The Text layer's ligature option.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    line_join_type: LineJoinType | None = None
    """
    The Text layer's line join type option for Stroke.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    line_orientation: LineOrientation | None = None
    """
    The Text layer's line orientation, in general horizontal vs vertical,
    which affects how all text in the layer is composed.

    Note:
        This functionality was added in After Effects 24.2.
    """

    no_break: bool | None = None
    """
    The Text layer's no break attribute.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    paragraph_count: int | None = None
    """
    The number of paragraphs in the text layer, always greater than or
    equal to 1.
    """

    point_text: bool | None = None
    """
    `True` if a Text layer is a layer of point (unbounded) text; otherwise
    `False`.
    """

    small_caps: bool | None = None
    """
    `True` if a Text layer has small caps enabled; otherwise `False`.
    To set this value, use
    [font_caps_option][TextDocument.font_caps_option].

    Note:
        This functionality was added in After Effects 13.2 (CC 2014.2).

    Warning:
        This value only reflects the first character in the Text layer.
    """

    space_after: float | None = None
    """
    The Text layer's paragraph space after option.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    space_before: float | None = None
    """
    The Text layer's paragraph space before option.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    start_indent: float | None = None
    """
    The Text layer's paragraph start indent option.

    If this attribute has a mixed value, it will be read as `None`.

    Note:
        This functionality was added in After Effects 24.0.

    Warning:
        This value reflects all paragraphs in the Text layer. If you change
        this value, it will set all paragraphs in the Text layer to the
        specified setting.
    """

    stroke_color: list[float] | None = None
    """
    The Text layer's stroke color, as an array of ``[r, g, b]``
    floating-point values. For example, in an 8-bpc project, a red value
    of 255 would be 1.0, and in a 32-bpc project, an overbright blue value
    can be something like 3.2.

    Setting this value will also set
    [apply_stroke][TextDocument.apply_stroke] to `True` across the
    affected characters.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    stroke_over_fill: bool | None = None
    """
    Indicates the rendering order for the fill and stroke of a Text layer.
    When `True`, the stroke appears over the fill.

    The Text layer can override the per-character attribute setting if the
    Text layer is set to use All Strokes Over All Fills or All Fills Over
    All Strokes in the Character Panel. Thus the value returned here might
    be different than the actual attribute value set on the character.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    stroke_width: float | None = None
    """
    The Text layer's stroke thickness in pixels.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting. The minimum accepted value to set is 0,
        but this will be silently clipped to 0.01.
    """

    subscript: bool | None = None
    """
    `True` if a Text layer has subscript enabled; otherwise `False`.
    To set this value, use
    [font_baseline_option][TextDocument.font_baseline_option].

    Note:
        This functionality was added in After Effects 13.2 (CC 2014.2).

    Warning:
        This value only reflects the first character in the Text layer.
    """

    superscript: bool | None = None
    """
    `True` if a Text layer has superscript enabled; otherwise `False`.
    To set this value, use
    [font_baseline_option][TextDocument.font_baseline_option].

    Note:
        This functionality was added in After Effects 13.2 (CC 2014.2).

    Warning:
        This value only reflects the first character in the Text layer.
    """

    tracking: float | None = None
    """
    The Text layer's spacing between characters.

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """

    tsume: float | None = None
    """
    This Text layer's tsume value as a normalized percentage, from
    0.0 to 1.0.

    Note:
        This functionality was added in After Effects 13.2 (CC 2014.2).

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting. This attribute accepts values from
        0.0 to 100.0, however the value is expecting a normalized value
        from 0.0 to 1.0. Using a value higher than 1.0 will produce
        unexpected results.
    """

    vertical_scale: float | None = None
    """
    This Text layer's vertical scale in pixels.

    Note:
        This functionality was added in After Effects 13.2 (CC 2014.2).

    Warning:
        This value only reflects the first character in the Text layer. If
        you change this value, it will set all characters in the Text layer
        to the specified setting.
    """
