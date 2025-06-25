# coding: utf-8
"""
Additional comprehensive test for BOM handling edge cases.
"""
from __future__ import absolute_import, unicode_literals, division
import io
from aep_parser.cos.cos import CosParser, TokenType


def test_utf8_bom_with_unicode_content():
    """Test UTF-8 BOM removal with unicode content following it."""
    # UTF-8 BOM followed by unicode content
    utf8_bom_string = b"(\xef\xbb\xbf\xe2\x9c\x93 unicode)"  # BOM + checkmark + " unicode"
    parser = CosParser(io.BytesIO(utf8_bom_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    # Should NOT contain the BOM character (\ufeff) but should contain the unicode
    assert token.value == "✓ unicode"
    assert "\ufeff" not in token.value


def test_partial_utf8_bom():
    """Test that partial UTF-8 BOM sequences are treated as normal content."""
    # Only first 2 bytes of UTF-8 BOM
    partial_bom_string = b"(\xef\xbbtest)"
    parser = CosParser(io.BytesIO(partial_bom_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    # Should contain the partial BOM bytes as regular content
    assert len(token.value) == 6  # 2 BOM bytes + "test"


def test_false_utf16_bom():
    """Test that UTF-16 BOM-like sequences in middle of string are preserved."""
    # UTF-16 BE BOM bytes in the middle (not at start)
    false_bom_string = b"(test\xfe\xffmore)"
    parser = CosParser(io.BytesIO(false_bom_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    # Should contain all content including the false BOM
    # Since this contains invalid UTF-8, it should return bytes
    if isinstance(token.value, bytes):
        assert b"test" in token.value
        assert b"more" in token.value
    else:
        assert "test" in token.value
        assert "more" in token.value


def test_mixed_bom_scenario():
    """Test string with UTF-8 content that contains UTF-16 BOM bytes."""
    # This is UTF-8 encoded string that happens to contain the UTF-16 BOM bytes
    mixed_string = b"(prefix\xfe\xffsuffix)"
    parser = CosParser(io.BytesIO(mixed_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    # Since this contains invalid UTF-8, it should return bytes
    if isinstance(token.value, bytes):
        assert token.value.startswith(b"prefix")
        assert token.value.endswith(b"suffix")
    else:
        assert token.value.startswith("prefix")
        assert token.value.endswith("suffix")