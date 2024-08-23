from common import *
from scanner import *

class eof(str):pass
EOF = eof("")
del eof

class TOKEN(enum):
    # Single-character tokens.
    LEFT_PAREN = enum_auto()
    RIGHT_PAREN = enum_auto()
    LEFT_BRACE = enum_auto()
    RIGHT_BRACE = enum_auto()
    COMMA = enum_auto()
    DOT = enum_auto()
    MINUS = enum_auto()
    PLUS = enum_auto()
    SEMICOLON = enum_auto()
    SLASH = enum_auto()
    STAR = enum_auto()
    # One or two character tokens.
    BANG = enum_auto()
    BANG_EQUAL = enum_auto()
    EQUAL = enum_auto()
    EQUAL_EQUAL = enum_auto()
    GREATER = enum_auto()
    GREATER_EQUAL = enum_auto()
    LESS = enum_auto()
    LESS_EQUAL = enum_auto()
    # Literals.
    IDENTIFIER = enum_auto()
    STRING = enum_auto()
    NUMBER = enum_auto()
    # Keywords.
    AND = enum_auto()
    CLASS = enum_auto()
    ELSE = enum_auto()
    FALSE = enum_auto()
    FOR = enum_auto()
    FUN = enum_auto()
    IF = enum_auto()
    NIL = enum_auto()
    OR = enum_auto()
    PRINT = enum_auto()
    RETURN = enum_auto()
    SUPER = enum_auto()
    THIS = enum_auto()
    TRUE = enum_auto()
    VAR = enum_auto()
    WHILE = enum_auto()

    ERROR = enum_auto()
    EOF = enum_auto()

class _tsynth:
    source = ""
    start = 0
    current = 0
    line = None

class Token:
    def __init__(self, scanner, type: TOKEN):
        self.type = type
        self.source = scanner.source[scanner.start:scanner.current]
        self.start = scanner.start
        self.line = scanner.line

    @staticmethod
    def error(scanner, message: str):
        t = Token(scanner, TOKEN.ERROR)
        t.source = message
        t.start = 0
        return t

    @staticmethod
    def synthetic(name: str):
        t = Token(_tsynth, None)
        t.source = name
        return t

def isDigit(c: str):
    if len(c)!=1: return False
    return ord("0") <= ord(c) <= ord("9")

def isAlpha(c: str):
    if len(c)!=1: return False
    return ((ord("a") <= ord(c) <= ord("z")) or
            (ord("A") <= ord(c) <= ord("Z")) or
            (c == "_"))

class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1

    def isAtEnd(self, offset: int=0):
        return self.current+offset >= len(self.source)

    def advance(self):
        self.current += 1
        return self.peek(-1)

    def peek(self, offset: int=0):
        if self.isAtEnd(offset): return EOF
        return self.source[self.current+offset]

    def match(self, expected: str):
        if self.isAtEnd(): return False
        if self.peek() != expected: return False
        self.current += 1
        return True

    def skipWhitespace(self):
        while True:
            c = self.peek()
            if c is EOF:
                return
            elif c in " \t\r":
                self.advance()
            elif c == "\n":
                self.line += 1
                self.advance()
            elif c == "/":
                if self.peek(1) == "/":
                    while self.peek() != "\n" and not self.isAtEnd():
                        self.advance()
                else:
                    return
            else:
                return

    def checkKeyword(self, start: int, rest: str, type: TOKEN):
        if (self.current-self.start-start == len(rest) and
            self.source[
             self.start+start:
             self.start+start+len(rest)
            ] == rest):
            return type

        return TOKEN.IDENTIFIER

    def identifierType(self):
        match self.source[self.start]:
            case "a": return self.checkKeyword(1, "nd", TOKEN.AND)
            case "c": return self.checkKeyword(1, "lass", TOKEN.CLASS)
            case "e": return self.checkKeyword(1, "lse", TOKEN.ELSE)
            case "i": return self.checkKeyword(1, "f", TOKEN.IF)
            case "f":
                if self.current - self.start > 1:
                    match self.source[self.start+1]:
                        case "a": return self.checkKeyword(2, "lse", TOKEN.FALSE)
                        case "o": return self.checkKeyword(2, "r", TOKEN.FOR)
                        case "u": return self.checkKeyword(2, "n", TOKEN.FUN)
            case "n": return self.checkKeyword(1, "il", TOKEN.NIL)
            case "o": return self.checkKeyword(1, "r", TOKEN.OR)
            case "p": return self.checkKeyword(1, "rint", TOKEN.PRINT)
            case "r": return self.checkKeyword(1, "eturn", TOKEN.RETURN)
            case "s": return self.checkKeyword(1, "uper", TOKEN.SUPER)
            case "t":
                if self.current - self.start > 1:
                    match self.source[self.start+1]:
                        case "h": return self.checkKeyword(2, "is", TOKEN.THIS)
                        case "r": return self.checkKeyword(2, "ue", TOKEN.TRUE)
            case "v": return self.checkKeyword(1, "ar", TOKEN.VAR)
            case "w": return self.checkKeyword(1, "hile", TOKEN.WHILE)

        return TOKEN.IDENTIFIER

    def identifier(self):
        while isAlpha(self.peek()) or isDigit(self.peek()): self.advance()
        return Token(self, self.identifierType())

    def number(self):
        while isDigit(self.peek()): self.advance()

        # Look for a fractional part.
        if self.peek() == "." and isDigit(self.peek(1)):
            # Consume the ".".
            self.advance()

            while isDigit(self.peek()): self.advance()

        return Token(self, TOKEN.NUMBER)

    def string(self):
        while self.peek() != '"' and not self.isAtEnd():
            if self.peek() == "\n": self.line += 1
            self.advance()

        if self.isAtEnd(): return Token.error(self, "Unterminated string.")

        # The closing quote.
        self.advance()
        return Token(self, TOKEN.STRING)

    def scanToken(self):
        self.skipWhitespace()
        self.start = self.current

        c = self.advance()
        if c is EOF: return Token(self, TOKEN.EOF)
        if isAlpha(c): return self.identifier()
        if isDigit(c): return self.number()

        match c:
            case "(": return Token(self, TOKEN.LEFT_PAREN)
            case ")": return Token(self, TOKEN.RIGHT_PAREN)
            case "{": return Token(self, TOKEN.LEFT_BRACE)
            case "}": return Token(self, TOKEN.RIGHT_BRACE)
            case ";": return Token(self, TOKEN.SEMICOLON)
            case ",": return Token(self, TOKEN.COMMA)
            case ".": return Token(self, TOKEN.DOT)
            case "-": return Token(self, TOKEN.MINUS)
            case "+": return Token(self, TOKEN.PLUS)
            case "/": return Token(self, TOKEN.SLASH)
            case "*": return Token(self, TOKEN.STAR)
            case "!":
                return Token(self,
                    TOKEN.BANG_EQUAL if self.match("=") else TOKEN.BANG)
            case "=":
                return Token(self,
                    TOKEN.EQUAL_EQUAL if self.match("=") else TOKEN.EQUAL)
            case "<":
                return Token(self,
                    TOKEN.LESS_EQUAL if self.match("=") else TOKEN.LESS)
            case ">":
                return Token(self,
                    TOKEN.GREATER_EQUAL if self.match("=") else TOKEN.GREATER)
            case '"': return self.string()

        return Token.error(self, "Unexpected character.")
