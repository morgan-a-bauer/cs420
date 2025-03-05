"""
Enumeration Types for the Eck compiler.
Dr. Hilton
CS420, Spring 2020

This module contains various enumerated types used in the Eck compiler.
"""

from enum import Enum, unique, auto


@unique
class DataTypes(Enum):
    """
    Enumerated type providing a symbolic constant for each of 
    the data types allowed in the Eck programming language.
    """
    BOOLEAN_SCALAR = auto()
    BOOLEAN_ARRAY = auto()
    CHAR_SCALAR = auto()
    CHAR_ARRAY = auto()
    CLASS_SCALAR = auto()
    INT_SCALAR = auto()
    INT_ARRAY = auto()
    STRING = auto()
    VOID = auto()


@unique
class SubroutineSpecifiers(Enum):
    """
    Enumerated type for the kinds of subroutines in Eck
    """
    CONSTRUCTOR = auto()
    FUNCTION = auto()
    METHOD = auto()


@unique
class VariableScopes(Enum):
    """
    Enumerated type for the kinds of variable scoping in Eck
    """
    FIELD = auto()
    LOCAL = auto()
    PARAMETER = auto()
    STATIC = auto()
