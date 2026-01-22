# coding: utf-8
"""
Test cases for BOM (Byte Order Mark) handling in COS string parsing.

Tests that BOMs are properly detected and removed from string values,
addressing issue #12 where UTF-8 BOM was appearing in decoded strings.
"""
from __future__ import absolute_import, unicode_literals, division
import io
from aep_parser.cos.cos import CosParser, TokenType


def test_utf8_bom_removal():
    """Test that UTF-8 BOM is properly removed from parsed strings."""
    # UTF-8 BOM (\xef\xbb\xbf) followed by "test"
    utf8_bom_string = b"(\xef\xbb\xbftest)"
    parser = CosParser(io.BytesIO(utf8_bom_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == "test", f"Expected 'test', got {repr(token.value)}"
    assert "\ufeff" not in token.value, "BOM character should not be in the decoded string"


def test_utf16_be_bom_removal():
    """Test that UTF-16 BE BOM is properly removed."""
    # UTF-16 BE BOM (\xfe\xff) followed by "test" in UTF-16 BE encoding
    utf16_be_string = b"(\xfe\xff\x00t\x00e\x00s\x00t)"
    parser = CosParser(io.BytesIO(utf16_be_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == "test", f"Expected 'test', got {repr(token.value)}"


def test_utf16_le_bom_removal():
    """Test that UTF-16 LE BOM is properly removed."""
    # UTF-16 LE BOM (\xff\xfe) followed by "test" in UTF-16 LE encoding
    utf16_le_string = b"(\xff\xfet\x00e\x00s\x00t\x00)"
    parser = CosParser(io.BytesIO(utf16_le_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == "test", f"Expected 'test', got {repr(token.value)}"


def test_no_bom_string():
    """Test that strings without BOM work correctly."""
    plain_string = b"(hello world)"
    parser = CosParser(io.BytesIO(plain_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == "hello world"


def test_empty_string():
    """Test that empty strings work correctly."""
    empty_string = b"()"
    parser = CosParser(io.BytesIO(empty_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == ""


def test_utf8_bom_with_unicode():
    """Test UTF-8 BOM with unicode content following it."""
    # UTF-8 BOM followed by checkmark (✓) and text
    utf8_bom_unicode = b"(\xef\xbb\xbf\xe2\x9c\x93 check)"
    parser = CosParser(io.BytesIO(utf8_bom_unicode))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == "✓ check", f"Expected '✓ check', got {repr(token.value)}"
    assert "\ufeff" not in token.value


def test_partial_utf8_bom():
    """Test that partial UTF-8 BOM sequences are treated as regular content."""
    # Only first 2 bytes of UTF-8 BOM (not a valid BOM)
    partial_bom = b"(\xef\xbbtest)"
    parser = CosParser(io.BytesIO(partial_bom))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    # Should contain the partial BOM bytes as regular content
    # This may return bytes due to invalid UTF-8 sequence
    if isinstance(token.value, bytes):
        assert b"test" in token.value
    else:
        assert "test" in token.value


def test_short_strings():
    """Test short strings (1-2 characters) work correctly."""
    test_cases = [
        (b"(a)", "a"),
        (b"(ab)", "ab"),
        (b"(x)", "x"),
    ]
    
    for input_bytes, expected in test_cases:
        parser = CosParser(io.BytesIO(input_bytes))
        token = parser.lex_token()
        assert token.type == TokenType.String
        assert token.value == expected, f"Expected {repr(expected)}, got {repr(token.value)}"


def test_bom_only_strings():
    """Test strings that contain only a BOM."""
    # String with only UTF-8 BOM
    utf8_bom_only = b"(\xef\xbb\xbf)"
    parser = CosParser(io.BytesIO(utf8_bom_only))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == "", f"Expected empty string, got {repr(token.value)}"
    assert "\ufeff" not in token.value
