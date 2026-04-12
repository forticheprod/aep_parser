"""Tests for TextDocument and FontObject model parsing and roundtrip."""

from __future__ import annotations

from pathlib import Path

import pytest

from aep_parser import parse as parse_aep
from aep_parser.enums import (
    AutoKernType,
    FontBaselineOption,
    FontCapsOption,
    LeadingType,
    ParagraphJustification,
)

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "models" / "layer"


def _get_text_document(aep_path: Path):
    """Parse and return the first text document from an .aep file."""
    app = parse_aep(aep_path)
    comp = app.project.compositions[0]
    text_layer = comp.text_layers[0]
    return app.project, text_layer.text.source_text.value


class TestTextDocumentParsing:
    """Tests for TextDocument lazy COS field access."""

    def test_text(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.text == "TextLayer"

    def test_font(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.font == "TimesNewRomanPSMT"

    def test_font_size(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.font_size == 36.0

    def test_fill_color(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.fill_color is not None
        assert len(doc.fill_color) == 3
        assert all(isinstance(c, float) for c in doc.fill_color)

    def test_stroke_color(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.stroke_color is not None
        assert doc.stroke_color == [0.0, 0.0, 0.0]

    def test_faux_bold(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.faux_bold is False

    def test_faux_italic(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.faux_italic is False

    def test_tracking(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.tracking is not None

    def test_justification(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.justification == ParagraphJustification.LEFT_JUSTIFY

    def test_font_caps_option(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.font_caps_option == FontCapsOption.FONT_NORMAL_CAPS

    def test_font_baseline_option(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.font_baseline_option == FontBaselineOption.FONT_NORMAL_BASELINE

    def test_derived_all_caps(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.all_caps is False

    def test_derived_small_caps(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.small_caps is False

    def test_derived_superscript(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.superscript is False

    def test_derived_subscript(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.subscript is False

    def test_paragraph_count(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.paragraph_count == 1

    def test_auto_leading(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.auto_leading is True

    def test_auto_hyphenate(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.auto_hyphenate is True

    def test_every_line_composer(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.every_line_composer is False

    def test_hanging_roman(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.hanging_roman is False

    def test_auto_kern_type(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.auto_kern_type == AutoKernType.NO_AUTO_KERN

    def test_leading_type(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.leading_type == LeadingType.ROMAN_LEADING_TYPE

    def test_apply_fill(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.apply_fill is True

    def test_apply_stroke(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.apply_stroke is False


class TestFontObject:
    """Tests for FontObject COS field access."""

    def test_post_script_name(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.font_object is not None
        assert doc.font_object.post_script_name == "TimesNewRomanPSMT"

    def test_version(self) -> None:
        _project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.font_object is not None
        assert doc.font_object.version == "Version 7.00"


class TestRoundtripFontSize:
    """Roundtrip tests for TextDocument.font_size."""

    def test_modify_font_size(self, tmp_path: Path) -> None:
        project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.font_size == 36.0

        doc.font_size = 72.0
        out = tmp_path / "modified.aep"
        project.save(out)

        _project2, doc2 = _get_text_document(out)
        assert doc2.font_size == 72.0


class TestRoundtripFauxBold:
    """Roundtrip tests for TextDocument.faux_bold."""

    def test_enable_faux_bold(self, tmp_path: Path) -> None:
        project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.faux_bold is False

        doc.faux_bold = True
        out = tmp_path / "modified.aep"
        project.save(out)

        _project2, doc2 = _get_text_document(out)
        assert doc2.faux_bold is True


class TestRoundtripFillColor:
    """Roundtrip tests for TextDocument.fill_color."""

    def test_modify_fill_color(self, tmp_path: Path) -> None:
        project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")

        doc.fill_color = [1.0, 0.0, 0.0]
        out = tmp_path / "modified.aep"
        project.save(out)

        _project2, doc2 = _get_text_document(out)
        assert doc2.fill_color is not None
        assert doc2.fill_color[0] == 1.0
        assert doc2.fill_color[1] == 0.0
        assert doc2.fill_color[2] == 0.0


class TestRoundtripText:
    """Roundtrip tests for TextDocument.text."""

    def test_modify_text(self, tmp_path: Path) -> None:
        project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")

        doc.text = "Modified"
        out = tmp_path / "modified.aep"
        project.save(out)

        _project2, doc2 = _get_text_document(out)
        assert doc2.text == "Modified"


class TestRoundtripJustification:
    """Roundtrip tests for TextDocument.justification."""

    def test_modify_justification(self, tmp_path: Path) -> None:
        project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")
        assert doc.justification == ParagraphJustification.LEFT_JUSTIFY

        doc.justification = ParagraphJustification.CENTER_JUSTIFY
        out = tmp_path / "modified.aep"
        project.save(out)

        _project2, doc2 = _get_text_document(out)
        assert doc2.justification == ParagraphJustification.CENTER_JUSTIFY


class TestRoundtripTracking:
    """Roundtrip tests for TextDocument.tracking."""

    def test_modify_tracking(self, tmp_path: Path) -> None:
        project, doc = _get_text_document(SAMPLES_DIR / "type_text.aep")

        doc.tracking = 50.0
        out = tmp_path / "modified.aep"
        project.save(out)

        _project2, doc2 = _get_text_document(out)
        assert doc2.tracking == 50.0
