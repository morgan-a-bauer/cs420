"""
Lexeme enumeration for the Eck Compiler
Dr. Hilton
CS420, Spring 2020

This module contains an enumerated type for the different lexemes
created by the Eck scanner.
"""

from enum import Enum, unique, auto

"""
The Lexeme enumerated type provides a symbolic constant for each of the
possible lexeme categories in Eck.  The lexical description of Eck
has been augmented to include the lexeme EOF to signify the end-of-file.
"""


@unique
class Lexeme(Enum):
    EOF = auto()
    INTEGER_CONST = auto()
    STRING_CONST = auto()
    IDENTIFIER = auto()
    KW_BOOLEAN = auto()
    KW_CHAR = auto()
    KW_CLASS = auto()
    KW_CONSTRUCTOR = auto()
    KW_DO = auto()
    KW_ELSE = auto()
    KW_FALSE = auto()
    KW_FIELD = auto()
    KW_FUNCTION = auto()
    KW_IF = auto()
    KW_INT = auto()
    KW_METHOD = auto()
    KW_NULL = auto()
    KW_RETURN = auto()
    KW_STATIC = auto()
    KW_THIS = auto()
    KW_TRUE = auto()
    KW_VOID = auto()
    KW_WHILE = auto()
    SYMBOL_OPEN_BRACE = auto()
    SYMBOL_CLOSE_BRACE = auto()
    SYMBOL_OPEN_PAREN = auto()
    SYMBOL_CLOSE_PAREN = auto()
    SYMBOL_OPEN_BRACKET = auto()
    SYMBOL_CLOSE_BRACKET = auto()
    SYMBOL_DOT = auto()
    SYMBOL_COMMA = auto()
    SYMBOL_SEMICOLON = auto()
    SYMBOL_PLUS = auto()
    SYMBOL_MINUS = auto()
    SYMBOL_TIMES = auto()
    SYMBOL_DIVIDE = auto()
    SYMBOL_AND = auto()
    SYMBOL_OR = auto()
    SYMBOL_LT = auto()
    SYMBOL_GT = auto()
    SYMBOL_EQUAL = auto()
    SYMBOL_NEGATE = auto()


"""
The Eck scanner lumps keywords and identifiers together into a single
DFA that generates a string.  The LexemeMap.keywords dictionary must then
be used to map this string to its lexeme category.

The scanner also lumps together all the symbols, and the string generated
by the symbol DFA must be mapped to its lexeme category using the
LexemeMap.symbols dictionary.
"""


class LexemeMap:
    keywords = {
        "boolean": Lexeme.KW_BOOLEAN,
        "char": Lexeme.KW_CHAR,
        "class": Lexeme.KW_CLASS,
        "constructor": Lexeme.KW_CONSTRUCTOR,
        "do": Lexeme.KW_DO,
        "else": Lexeme.KW_ELSE,
        "false": Lexeme.KW_FALSE,
        "field": Lexeme.KW_FIELD,
        "function": Lexeme.KW_FUNCTION,
        "if": Lexeme.KW_IF,
        "int": Lexeme.KW_INT,
        "method": Lexeme.KW_METHOD,
        "null": Lexeme.KW_NULL,
        "return": Lexeme.KW_RETURN,
        "static": Lexeme.KW_STATIC,
        "this": Lexeme.KW_THIS,
        "true": Lexeme.KW_TRUE,
        "void": Lexeme.KW_VOID,
        "while": Lexeme.KW_WHILE
    }
    symbols = {
        "{": Lexeme.SYMBOL_OPEN_BRACE,
        "}": Lexeme.SYMBOL_CLOSE_BRACE,
        "(": Lexeme.SYMBOL_OPEN_PAREN,
        ")": Lexeme.SYMBOL_CLOSE_PAREN,
        "[": Lexeme.SYMBOL_OPEN_BRACKET,
        "]": Lexeme.SYMBOL_CLOSE_BRACKET,
        ".": Lexeme.SYMBOL_DOT,
        ",": Lexeme.SYMBOL_COMMA,
        ";": Lexeme.SYMBOL_SEMICOLON,
        "+": Lexeme.SYMBOL_PLUS,
        "-": Lexeme.SYMBOL_MINUS,
        "*": Lexeme.SYMBOL_TIMES,
        "/": Lexeme.SYMBOL_DIVIDE,
        "&": Lexeme.SYMBOL_AND,
        "|": Lexeme.SYMBOL_OR,
        "<": Lexeme.SYMBOL_LT,
        ">": Lexeme.SYMBOL_GT,
        "=": Lexeme.SYMBOL_EQUAL,
        "~": Lexeme.SYMBOL_NEGATE
    }
