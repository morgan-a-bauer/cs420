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

    def pAssignmentStatement(self):
        """<assignmentStatement> →  <varName><varArray> = <expression> ;"""
        varName = self.pVarName()
        varArray = self.pVarArray()
        self.matchNext(Lexeme.SYMBOL_EQUAL, "Expected a '='")
        expr = self.pExpression()
        self.matchNext(Lexeme.SYMBOL_SEMICOLON, "Expected a ';'")
        asmt = PIR_AssignmentStatement(self.lineNumber, varName, varArray, expr)
        return asmt

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
        typ = self.pType()
        names = self.pVarList()
        line = self.lineNumber
        pirVars = []
        for name in names:
            pirVarDec = PIR_VariableDeclaration(line, typ, name, scope)
            pirVars.append(pirVarDec)
        return pirVars

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

    def pExpression(self):
        """<expression> →  <exp1><expression'>"""
        pass

    def pExp3p(self):
        """<exp3'> →  * <exp4><exp3'> | / <exp4><exp3'> | epsilon"""
        if self.matchNext(Lexeme.SYMBOL_TIMES):
            op = Lexeme.SYMBOL_TIMES
    def pExp4(self):
        """<exp4> →  - <exp4> | ~ <exp4> | integerConstant | stringConstant |
                     <keywordConstant> | identifier <exp4Id> |
                     ( <expression> )
        """
        if self.matchNext(Lexeme.SYMBOL_MINUS):
            op = Lexeme.SYMBOL_MINUS
            expr = self.pExp4()
            return PIR_ExpressionUnop(self.lineNumber, op, expr)
        elif self.match(Lexeme.SYMBOL_NEGATE):
            op = Lexeme.SYMBOL_NEGATE
            expr = self.pExp4()
        elif self.match(Lexeme.INTEGER_CONST):
            return PIR_ExpressionConstant(self.lineNumber, Lexeme.INTEGER_CONST,
                                          self.token[1])
        elif self.match(Lexeme.STRING_CONST):
            return PIR_ExpressionConstant(self.lineNumber, Lexeme.STRING_CONST,
                                          self.token[1])
        elif self.match(Lexeme.IDENTIFIER):
            lk = self.lookaheadToken()[0]
            if lk == Lexeme.SYMBOL_OPEN_BRACKET:
                expr = self.pExpression()
                return PIR_ExpressionVariable(self.lineNumber, self.token[1], expr)
        elif self.match(Lexeme.SYMBOL_OPEN_PAREN):
            expr = self.pExpression()
            self.matchNext(Lexeme.SYMBOL_CLOSE_PAREN, "Expected a ')'")
            return expr
        else:
            return self.pKeywordConstant()
        
    def pExp4Id(self):
        """<exp4Id> →  [ <expression> ] | . <subroutineName><actualParameters> |
           <actualParameters> | epsilon"""
        if self.matchNext(Lexeme.SYMBOL_OPEN_BRACKET):
            expr = self.pExpression()
            self.matchNext(Lexeme.SYMBOL_CLOSE_BRACKET, "Expected a ']'")
            return expr
        elif self.match(Lexeme.SYMBOL_DOT):
            subName = self.pSubroutineName()
            params = self.pActualParameters()
            return subName, params

    def pFormalParameters(self):
        """<formalParameters> →  <parameterList> | epsilon"""
        if self.lookaheadToken()[0] == Lexeme.SYMBOL_CLOSE_PAREN:
            self.nextToken()
            return []
        return self.pParameterList()

    def pParameterList(self):
        """<parameterList> →  <type><varName><parameterList1>"""
        params = []
        typ = self.pType()
        name = self.pVarName()
        pirVarDec = PIR_VariableDeclaration(self.lineNumber, typ, name,
                                            VariableScopes.PARAMETER)
        params.append(pirVarDec)
        params = params + self.pParameterList1()
        return params

    def pParameterList1(self):
        """<parameterList1> →  <parameterList> | epsilon"""
        if self.lookaheadToken()[0] == Lexeme.SYMBOL_CLOSE_PAREN:
            return []
        self.matchNext(Lexeme.SYMBOL_COMMA, "Expected a ','")
        return self.pParameterList()

    def pSubroutineBody(self):
        """<subroutineBody> →  <varDec>*<statements>"""
        #TODO: if no variables
        while self.lookaheadToken()[0] != Lexeme.SYMBOL_SEMICOLON:
            typ, names = self.pVarDec()
            vars = []
            for name in names:
                var = PIR_VariableDeclaration(self.lineNumber, typ, name,
                                              VariableScopes.LOCAL)
                vars.append(var)
            body = vars
        body = body + self.pStatements()

        return body

    def pStatement(self):
        """<statement> →  <assignmentStatement> | <ifStatement> |
                          <whileStatement> | <doStatement> |
                          <returnStatement>"""
        lk = self.lookaheadToken()[0]
        if lk == Lexeme.KW_IF:
            statement = self.pIfStatement()
        elif lk == Lexeme.KW_WHILE:
            statement = self.pWhileStatement()
        elif lk == Lexeme.KW_DO:
            statement = self.pDoStatement()
        elif lk == Lexeme.KW_RETURN:
            statement = self.pReturnStatement()
        else:
            statement = self.pAssignmentStatement()
        return statement

    def pStatements(self):
        """<statements> →  <statement>*"""
        statements = []
        while self.lookaheadToken()[0] != Lexeme.SYMBOL_CLOSE_BRACE:
            statement = self.pStatement()
            statements.append(statement)
        return statements

    def pSubroutineDecs(self):
        """
        <subroutineDec> →  <subroutineSpecifier>  <subroutineType>
                <subroutineName>  (<formalParameters>) { <subroutineBody> }
        """
        spec = self.pSubroutineSpecifier()
        typ = self.pSubroutineType()
        name = self.pSubroutineName()
        # parse parameter list
        self.matchNext(Lexeme.SYMBOL_CLOSE_PAREN, "Expected a '('")
        formal_params = self.pFormalParameters()
        # parse body of a subroutine
        self.matchNext(Lexeme.SYMBOL_OPEN_BRACE, "Expected a '{'")
        body = self.pSubroutineBody()

    def pSubroutineName(self):
        """<subroutineName> →  identifier"""
        #TODO: Error message
        name = self.matchNext(Lexeme.IDENTIFIER, "")
        return name

    def pSubroutineSpecifier(self):
        """<subroutineSpecifier> →  constructor | function | method"""
        if self.matchNext(Lexeme.KW_CONSTRUCTOR):
            return SubroutineSpecifiers.CONSTRUCTOR
        elif self.match(Lexeme.KW_FUNCTION):
            return SubroutineSpecifiers.FUNCTION
        elif self.match(Lexeme.KW_METHOD):
            return SubroutineSpecifiers.METHOD

    def pSubroutineType(self):
        """<subroutineType> →  void | <type>"""
        if self.lookaheadToken()[0] == (Lexeme.KW_VOID):
            self.nextToken()
            return DataTypes.VOID
        return self.pType

    def pType(self):
        """<type> →  int | char | boolean | int[] | char[] | boolean[] | <className>"""
        if self.matchNext(Lexeme.IDENTIFIER):
            return self.token[1]
        elif self.match(Lexeme.KW_INT):
            if self.lookaheadToken()[0] == Lexeme.SYMBOL_OPEN_BRACE:
                self.nextToken()
                self.nextToken()
                return DataTypes.INT_ARRAY
            return DataTypes.INT_SCALAR
        elif self.match(Lexeme.KW_CHAR):
            if self.lookaheadToken()[0] == Lexeme.SYMBOL_OPEN_BRACE:
                self.nextToken()
                self.nextToken()
                return DataTypes.CHAR_ARRAY
            return DataTypes.CHAR_SCALAR
        elif self.match(Lexeme.KW_BOOLEAN):
            if self.lookaheadToken()[0] == Lexeme.SYMBOL_OPEN_BRACE:
                self.nextToken()
                self.nextToken()
                return DataTypes.BOOLEAN_ARRAY
            return DataTypes.BOOLEAN_SCALAR

    def pVarArray(self):
        """<varArray> →  [ <expression> ] | epsilon"""
        if self.lookaheadToken()[0] == Lexeme.SYMBOL_EQUAL:
            return None
        self.matchNext(Lexeme.SYMBOL_OPEN_BRACKET, "Expected a '['")
        expr = self.pExpression()
        self.matchNext(Lexeme.SYMBOL_CLOSE_BRACKET, "Expected a ']'")
        return expr

    def pVarDec(self):
        """<varDec> →  <type><varList>"""
        typ = self.pType()
        varNames = self.pVarList()
        return typ, varNames

    def pVarList(self):
        """<varList> →  <varName><varList1>"""
        varList = []
        if self.matchNext(Lexeme.IDENTIFIER):
            varList.append(self.token[1])
        #TODO: raise parser error is not an identifier
        varList = varList + self.pVarList1()
        return varList

    def pVarList1(self):
        """<varList1> →  <varList> | epsilon"""
        varList = []
        if self.lookaheadToken()[0] == Lexeme.SYMBOL_SEMICOLON:
            return []
        self.matchNext(Lexeme.SYMBOL_COMMA, "Expected a ','")
        return self.pVarList()

    def pVarName(self):
        """<varName> →  identifier"""
        #TODO: err message
        name = self.matchNext(Lexeme.IDENTIFIER, "")
        return name


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
        print(parserOutfile)
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
