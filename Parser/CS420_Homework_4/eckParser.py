"""
Recursive Descent Parser for Eck Programming Language
Dr. Hilton
CS420, Spring 2025
"""

from eckTypes import DataTypes, SubroutineSpecifiers, VariableScopes
from lexeme import Lexeme, LexemeMap
from scanner import Scanner
from parserIR import *


class ParserError(Exception):
    """Custom error class for parser errors in a Eck source code file."""

    def __init__(self, value):
        self.value = value

    # __str__ is to print() the value
    def __str__(self):
        return (repr(self.value))


class Parser:
    """
    Recursive descent parser for the Eck programming language.  A call
    to the parse(filename) method returns the abstract syntax tree for the
    specified Eck source code file.

    The methods whose names begin with lowercase "p" followed by an uppercase
    letter are direct embodiments of similarly named rules in the Eck
    grammar BNF.
    """

    def __init__(self):
        self.__class = None       # name of the class being parsed
        self.__filename = None    # file being parsed
        self.__lineNumber = None  # line number for current token
        self.__lookahead = None   # lookahead token
        self.__scanner = None     # Scanner object providing tokens to parser
        self.__token = None       # most recently scanned token

    @property
    def lineNumber(self):
        return self.__lineNumber
    
    @property
    def token(self):
        return self.__token
    
    def lookaheadToken(self):
        """Returns the next token, but does not remove it from the
        input stream."""
        if self.__lookahead is not None:
            raise ParserError(
                f"Line {self.lineNumber}: More than one level of lookahead attempted")
        else:
            # cache the lookahead token and line number in self._lookahead
            token = self.__scanner.nextLexeme()
            lineNo = self.__scanner.getLineNumber()
            self.__lookahead = (token, lineNo)
            return token

    def match(self, lexeme, errorMsg=None):
        """Returns if the current token matches the specified lexeme.
        If an errorMsg string is provided, a ParserError is raised when
        the lexeme does not match.
        Inputs:
            lexeme      The Lexeme enumerated type constant to match on
            errorMsg    The descriptive portion of the error message to
                        raise if there is no match.  This function will
                        prepend the line number to errorMsg.
        Returns:
            The value True if there is a match; the value False otherwise
            (unless an error is raised).
        """
        if (self.token[0] == lexeme):
            return True
        elif errorMsg is not None:
            raise ParserError(f"Line {self.lineNumber}: {errorMsg}")
        else:
            return False

    def matchNext(self, lexeme, errorMsg=None):
        """Reads the next token and then returns if the token matches
        the specified lexeme. If an errorMsg string is provided, a
        ParserError is raised when the lexeme does not match.
        Inputs:
            lexeme      The Lexeme enumerated type constant to match on
            errorMsg    The descriptive portion of the error message to
                        raise if there is no match.  This function will
                        prepend the line number to errorMsg.
        Returns:
            The value True if there is a match; the value False otherwise
            (unless an error is raised).
        """
        self.nextToken()
        return self.match(lexeme, errorMsg)

    def nextToken(self):
        """Fetches the next token from the scanner"""
        # check if there is a cached lookahead value
        if self.__lookahead is not None:
            # consume the cached value
            self.__token = self.__lookahead[0]
            self.__lineNumber = self.__lookahead[1]
            self.__lookahead = None
        else:
            # fetch a new token from the scanner
            self.__token = self.__scanner.nextLexeme()
            self.__lineNumber = self.__scanner.getLineNumber()
        return self.__token

    def parse(self, filename):
        """Parse the specified file.  Returns a PIR abstract syntax tree."""
        self.__filename = filename
        self.__scanner = Scanner(filename)
        # prime the pump by getting the first lexeme
        self.nextToken()
        # attempt to parse the class
        return self.pClass()

    def pClass(self):
        """<classDec> →  class <className> { <classVarDec>*  <subroutineDec>* }"""
        if self.match(Lexeme.KW_CLASS, "Expected a class definition"):
            line = self.lineNumber
            # get the class name
            name = self.pClassVarName()
            self.__class = name
            # parse body of class
            self.matchNext(Lexeme.SYMBOL_OPEN_BRACE, "Expected a '{'")
            pirVars = self.pClassVarDecs()
            pirSubs = self.pSubroutineDecs()
            self.match(Lexeme.SYMBOL_CLOSE_BRACE, "Expected a '}'")
            # create the AST node for a class
            pirClass = PIR_Class(line, name, pirVars, pirSubs)
            return pirClass

    def pClassVarDecs(self):
        """<classVarDec > →  <classVarModifier> <type>  <varList>;"""
        scope = self.pClassVarModifier()
        type = self.pType()

    def pClassVarModifier(self):
        """<classVarModifier> → static | field"""
        if self.matchNext(Lexeme.KW_STATIC):
            return VariableScopes.STATIC
        elif self.match(Lexeme.KW_FIELD):
            return VariableScopes.FIELD

    def pClassVarName(self):
        """<varName> →  identifier"""
        self.matchNext(Lexeme.IDENTIFIER, "Expected a class name")
        return self.token[1]

    def pSubroutineDecs(self):
        """
        <subroutineDec> →  <subroutineSpecifier>  <subroutineType>
                <subroutineName>  (<formalParameters>) { <subroutineBody> }
        """
        pass

    def pType(self):
        """<type> →  int | char | boolean | int[] | char[] | boolean[] | <className>"""

if __name__ == "__main__":
    import io
    import os
    from pirPrinter import PIR_Printer

    def tester(filename):
        """
        Testing function for the Parser class.  The parser is called on the
        specified file and the intermediate representation returned by the
        parser is written to a file with suffix ".parse" and compared to
        the expected output, which is found in the corresponding ".answer" file.
        A message is printed to the console indicating if the input file parsed
        properly.
        """
        # create the output file names
        root, _ = os.path.splitext(filename)
        parserOutfile = root + ".parse"
        answerFilename = root + ".answer"

        # parse the file
        p = Parser()
        try:
            pirClass = p.parse(filename)
            # print out the IR
            printer = PIR_Printer()
            printer.print(parserOutfile, pirClass)
        except ParserError as err:
            print(err.value)
        else:
            # compare the parsing result file to the expected answer
            if os.path.exists(answerFilename):
                passed = True
                with open(parserOutfile, "r") as parsedFile:
                    with open(answerFilename, "r") as answerFile:
                        for parseLine in parsedFile:
                            # for some reason, I need to strip off newlines
                            parseLine = parseLine.replace("\n", "")
                            answerLine = answerFile.readline().replace("\n", "")
                            # compare the text after the 3-digit line number
                            if (parseLine[3:] != answerLine[3:]):
                                passed = False
                                break

                if passed:
                    print(f"{filename} parsed correctly")
                else:
                    print(f"{filename} does not produce the expected answer")

    """
    You can use these files to test your parser before you
    implement the rules for expressions, if you wish
    """
    # TODO: Change path names back (take out Parser/CS420_Homework_4/)
    tester("Parser/CS420_Homework_4/ParserTests/ExpressionlessSquare/Main.eck")
    tester("Parser/CS420_Homework_4/ParserTests/ExpressionlessSquare/Square.eck")
    tester("Parser/CS420_Homework_4/ParserTests/ExpressionlessSquare/SquareGame.eck")

    """
    These files test expressions
    """
    tester("Parser/CS420_Homework_4/ParserTests/ExpressionTests.eck")

    """
    These files require the full parser to be implemented
    """
    tester("Parser/CS420_Homework_4/ParserTests/Square/Main.eck")
    tester("Parser/CS420_Homework_4/ParserTests/Square/Square.eck")
    tester("Parser/CS420_Homework_4/ParserTests/Square/SquareGame.eck")
    tester("Parser/CS420_Homework_4/ParserTests/ArrayTests.eck")
