from __future__ import annotations

import enum
import io

"""
https://gitlab.com/mattbas/python-lottie/-/blob/master/lib/lottie/parsers/aep/cos.py
https://lottiefiles.github.io/lottie-docs/aep/#list-btdk
"""


class TokenType(enum.Enum):
    # /foo
    Identifier = 1
    # 123
    Number = 2
    # (foo)
    String = 3
    # <f000>
    HexString = 4
    # true
    Boolean = 5
    # <<
    ObjectStart = 6
    # >>
    ObjectEnd = 7
    # [
    ArrayStart = 8
    # ]
    ArrayEnd = 9
    # null
    Null = 10
    # end of file
    Eof = 11
    # obj
    IndirectObjectStart = 12
    # endobj
    IndirectObjectEnd = 13
    # R
    IndirectReference = 14
    # stream...endstream
    Stream = 15


class Token:
    __slots__ = ("type", "value")

    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        return "(%s, %s)" % (self.type.name, self.value)

    def __repr__(self):
        return "<Token %s>" % self


class IndirectObject(object):
    __slots__ = ("object_number", "generation_number", "data")

    def __init__(self, object_number, generation_number, data):
        self.object_number = object_number
        self.generation_number = generation_number
        self.data = data


class IndirectReference(object):
    __slots__ = ("object_number", "generation_number")

    def __init__(self, object_number, generation_number):
        self.object_number = object_number
        self.generation_number = generation_number


class Stream(object):
    __slots__ = ("dictionary", "data")

    def __init__(self, dictionary, data):
        self.dictionary = dictionary
        self.data = data


class CosParser:
    __slots__ = ("file", "max_pos", "lookahead")

    def __init__(self, file, max_pos=None):
        self.file = file
        self.max_pos = max_pos
        self.lookahead = None

    def parse(self):
        self.lex()
        if self.lookahead.type == TokenType.Identifier:
            return self.parse_dict_content()

        val = self.parse_value()
        if self.lookahead.type == TokenType.Eof:
            return val

        return [val] + self.parse_array_content()

    def parse_value(self):
        if (
            self.lookahead.type == TokenType.String
            or self.lookahead.type == TokenType.HexString
            or self.lookahead.type == TokenType.Null
            or self.lookahead.type == TokenType.Boolean
            or self.lookahead.type == TokenType.Identifier
            or self.lookahead.type == TokenType.Stream
        ):
            val = self.lookahead.value
            self.lex()
            return val

        if self.lookahead.type == TokenType.Number:
            val = self.lookahead.value
            self.lex()
            if self.lookahead.type == TokenType.Number:
                gen = self.lookahead.value
                state = self.save_state()
                self.lex()
                if self.lookahead.type == TokenType.IndirectObjectStart:
                    self.lex()
                    data = self.parse_value()
                    self.expect(TokenType.IndirectObjectEnd)
                    self.lex()
                    return IndirectObject(val, gen, data)
                elif self.lookahead.type == TokenType.IndirectReference:
                    self.lex()
                    return IndirectReference(val, gen)
                else:
                    self.restore_state(state)
            return val

        if self.lookahead.type == TokenType.ObjectStart:
            self.lex()
            val = self.parse_dict_content()
            self.expect(TokenType.ObjectEnd)
            self.lex()
            if self.lookahead.type == TokenType.Stream:
                val = Stream(val, self.lookahead.value)
                self.lex()
            return val

        if self.lookahead.type == TokenType.ArrayStart:
            self.lex()
            val = self.parse_array_content()
            self.expect(TokenType.ArrayEnd)
            self.lex()
            return val

        raise SyntaxError("Expected COS value, got %s" % self.lookahead)

    def save_state(self):
        return (self.max_pos, self.file.tell(), self.lookahead)

    def restore_state(self, state):
        self.max_pos, pos, self.lookahead = state
        self.file.seek(pos)

    def parse_dict_content(self):
        value = {}
        while True:
            if (
                self.lookahead.type == TokenType.Eof
                or self.lookahead.type == TokenType.ObjectEnd
            ):
                break

            self.expect(TokenType.Identifier)
            key = self.lookahead.value
            self.lex()
            val = self.parse_value()
            value[key] = val

        return value

    def parse_array_content(self):
        value = []
        while True:
            if (
                self.lookahead.type == TokenType.Eof
                or self.lookahead.type == TokenType.ArrayEnd
            ):
                break
            value.append(self.parse_value())
        return value

    def parse_indirect(self, object_number, generation_number):
        self.lex()
        if self.lookahead.type == TokenType.IndirectObjectStart:
            self.lex()
            data = self.parse_value()
            self.expect(TokenType.IndirectObjectEnd)
            self.lex()
            return IndirectObject(object_number, generation_number, data)
        elif self.lookahead.type == TokenType.IndirectReference:
            self.lex()
            return IndirectReference(object_number, generation_number)
        else:
            raise SyntaxError("Expected `obj` or `R`, got %s" % self.lookahead)

    def expect(self, token_type):
        if self.lookahead.type != token_type:
            raise SyntaxError("Expected %s, got %s" % (token_type, self.lookahead))

    def lex(self):
        self.lookahead = self.lex_token()

    def lex_token(self):
        while True:
            char = self.get_char()
            if char is None:
                return Token(TokenType.Eof)
            elif char == b"%":
                self.lex_comment()
            elif not char.isspace():
                break

        # <<
        if char == b"<":
            char = self.get_char()
            if char == b"<":
                return Token(TokenType.ObjectStart)
            elif char is None:
                self.raise_lex(b"<")
            elif self.is_hex(char):
                return self.lex_hex_string(char)
            else:
                self.raise_lex(b"<" + char)

        # >>
        if char == b">":
            self.expect_char(b">", char)
            return Token(TokenType.ObjectEnd)

        # [
        if char == b"[":
            return Token(TokenType.ArrayStart)

        # ]
        if char == b"]":
            return Token(TokenType.ArrayEnd)

        # /foo
        if char == b"/":
            return self.lex_identifier()

        # (foo)
        if char == b"(":
            return self.lex_string()

        # Keyword
        if char.isalpha():
            return self.lex_keyword(char)

        # Number
        if char.isdigit() or char in b".+-":
            return self.lex_number(char)

        self.raise_lex(char)

    def expect_char(self, exp, head):
        char = self.get_char()
        if char != exp:
            self.raise_lex(head + char, head + exp)

    def raise_lex(self, token, exp=None):
        msg = "Unknown COS token %s" % token
        if exp is not None:
            msg += ", expected %s" % exp
        raise SyntaxError(msg)

    def get_char(self):
        if self.max_pos is None:
            return self.file.read(1)

        if self.max_pos <= 0:
            return None

        char = self.file.read(1)
        self.max_pos -= 1
        return char

    def unget(self):
        self.file.seek(-1, io.SEEK_CUR)
        if self.max_pos is not None:
            self.max_pos += 1

    # Skip until newline
    def lex_comment(self):
        while True:
            char = self.get_char()
            if char == b"\n":
                break
            elif char is None:
                break

    def lex_number(self, char):
        if char == b".":
            return self.lex_num_fract(self.get_char(), char)
        elif char == b"+" or char == b"-":
            return self.lex_num_int(self.get_char(), char)
        else:
            return self.lex_num_int(char, b"")

    def lex_num_int(self, char, head):
        while True:
            if char == b".":
                return self.lex_num_fract(self.get_char(), head + char)
            elif char is None:
                break
            elif char.isdigit():
                head += char
                char = self.get_char()
            else:
                self.unget()
                break
        return Token(TokenType.Number, int(head))

    def lex_num_fract(self, char, head):
        while True:
            if char is None:
                break
            elif char.isdigit():
                head += char
                char = self.get_char()
            else:
                self.unget()
                break
        return Token(TokenType.Number, float(head))

    def lex_keyword(self, char):
        kw = char
        while True:
            char = self.get_char()
            if char is None:
                break
            elif char.isalpha():
                kw += char
            else:
                self.unget()
                break

        if kw == b"true":
            return Token(TokenType.Boolean, True)
        elif kw == b"false":
            return Token(TokenType.Boolean, False)
        elif kw == b"null":
            return Token(TokenType.Boolean, None)
        elif kw == b"obj":
            return Token(TokenType.IndirectObjectStart)
        elif kw == b"endobj":
            return Token(TokenType.IndirectObjectEnd)
        elif kw == b"R":
            return Token(TokenType.IndirectReference)
        elif kw == b"stream":
            return self.lex_stream()
        elif kw == b"xref":
            return Token(TokenType.Eof)
        else:
            raise SyntaxError("Unknown keyword %s" % kw)

    def lex_stream(self):
        char = self.get_char()
        if char == b"\r":
            if self.get_char() != b"\n":
                raise SyntaxError("Invalid newline")
        elif char != b"\n":
            raise SyntaxError("Expected newline after `stream`")

        stream = b""
        marker = b"endstream"
        while True:
            char = self.get_char()
            if char is None:
                raise SyntaxError("Unterminated stream")
            stream += char
            if stream.endswith(marker):
                break

        return Token(TokenType.Stream, stream[: -len(marker)])

    def lex_string(self):
        # Read the entire string content first
        string = b""
        while True:
            char = self.lex_string_char()
            if char is None:
                break
            string += char

        # Default to UTF-8 encoding
        encoding = "utf-8"

        # Check for BOM at the start of the string and remove it
        if string.startswith(b"\xef\xbb\xbf"):
            # UTF-8 BOM - remove it (3 bytes)
            string = string[3:]
            encoding = "utf-8"
        elif string.startswith(b"\xfe\xff"):
            # UTF-16 BE BOM - remove it (2 bytes)
            string = string[2:]
            encoding = "utf-16-be"
        elif string.startswith(b"\xff\xfe"):
            # UTF-16 LE BOM - remove it (2 bytes)
            string = string[2:]
            encoding = "utf-16-le"

        try:
            return Token(TokenType.String, string.decode(encoding))
        except UnicodeDecodeError:
            return Token(TokenType.String, string)

    def lex_string_char(self):
        char = self.get_char()
        if char is None:
            raise SyntaxError("Unterminated string")
        elif char == b")":
            return None
        elif char == b"\\":
            return self.lex_string_escape()
        elif char == b"\r":
            if self.get_char() != b"\n":
                self.unget()
            return b"\n"
        elif char == b"\n":
            if self.get_char() != b"\r":
                self.unget()
            return b"\n"
        else:
            return char

    def lex_string_escape(self):
        char = self.get_char()
        if char is None:
            raise SyntaxError("Unterminated string")

        if char == b"n":
            return b"\n"
        elif char == b"r":
            return b"\r"
        elif char == b"b":
            return b"\b"
        elif char == b"f":
            return b"\f"
        elif char == b"(":
            return b"("
        elif char == b")":
            return b")"
        elif char == b"\\":
            return b"\\"
        elif self.is_octal(char):
            octal = char[0] - b"0"[0]
            for i in range(2):
                char = self.get_char()
                if char is None:
                    break
                elif not self.is_octal(char):
                    self.unget()
                    break
                octal = octal * 8 + char - b"0"[0]
            return octal.to_bytes(1, "big")

        raise SyntaxError("Invalid escape sequence")

    def is_octal(self, char):
        return b"0" <= char <= b"8"

    def is_hex(self, char):
        return char.isdigit() or b"a" <= char <= b"f" or b"A" <= char <= b"F"

    def lex_hex_string(self, hstr):
        while True:
            char = self.get_char()
            if char is None:
                raise SyntaxError("Unterminated hex string")
            elif char.is_hex():
                hstr += char
            elif char == b">":
                break
            elif not char.isspace():
                raise SyntaxError("Invalid character in hex string: %s" % char)

        if len(hstr) % 2:
            hstr += b"0"

        data = b""
        for i in range(0, len(hstr), 2):
            data += int(hstr[i : i + 1], 16).to_bytes(1, "big")

        return Token(TokenType.HexString, data)

    def lex_identifier(self):
        ident = ""
        special = b"()[]<>{}/%"
        while True:
            char = self.get_char()
            if char is None:
                break
            elif char < b"!" or char > b"~":
                self.unget()
                break
            elif char == b"#":
                hexstr = b""
                for i in range(2):
                    char = self.get_char()
                    if char is None or not self.is_hex(char):
                        raise SyntaxError("Invalid identifier")
                    hexstr += char
                ident += chr(int(hexstr, 16))
            elif char in special:
                self.unget()
                break
            else:
                ident += chr(char[0])

        return Token(TokenType.Identifier, ident)
