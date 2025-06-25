# coding: utf-8
"""
Test cases for BOM (Byte Order Mark) handling in COS string parsing.
"""
from __future__ import absolute_import, unicode_literals, division
import io
from aep_parser.cos.cos import CosParser, TokenType


def test_utf8_bom_removal():
    """Test that UTF-8 BOM is removed from parsed strings."""
    # UTF-8 BOM followed by "test"
    utf8_bom_string = b"(\xef\xbb\xbftest)"
    parser = CosParser(io.BytesIO(utf8_bom_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    # Should NOT contain the BOM character (\ufeff)
    assert token.value == "test"
    assert "\ufeff" not in token.value


def test_utf16_be_bom_preserved():
    """Test that UTF-16 BE BOM handling continues to work."""
    # UTF-16 BE BOM followed by "test" in UTF-16 BE
    utf16_be_string = b"(\xfe\xff\x00t\x00e\x00s\x00t)"
    parser = CosParser(io.BytesIO(utf16_be_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == "test"


def test_utf16_le_bom_preserved():
    """Test that UTF-16 LE BOM handling continues to work."""
    # UTF-16 LE BOM followed by "test" in UTF-16 LE
    utf16_le_string = b"(\xff\xfet\x00e\x00s\x00t\x00)"
    parser = CosParser(io.BytesIO(utf16_le_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == "test"


def test_no_bom_string():
    """Test that strings without BOM work normally."""
    plain_string = b"(hello world)"
    parser = CosParser(io.BytesIO(plain_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == "hello world"


def test_empty_string():
    """Test that empty strings work normally."""
    empty_string = b"()"
    parser = CosParser(io.BytesIO(empty_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == ""


def test_short_string_no_bom():
    """Test that short strings (1-2 chars) without BOM work normally."""
    short_string = b"(ab)"
    parser = CosParser(io.BytesIO(short_string))
    token = parser.lex_token()
    
    assert token.type == TokenType.String
    assert token.value == "ab"