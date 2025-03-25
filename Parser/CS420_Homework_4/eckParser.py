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

    def pActualParameters(self):
        """<actualParameters> →  ( <expressionList> )"""
        self.matchNext(Lexeme.SYMBOL_OPEN_PAREN, "Expected a '('")
        lk = self.lookaheadToken()[0]
        if lk == Lexeme.SYMBOL_CLOSE_PAREN:
            self.nextToken()
            return []
        exprList = self.pExpressionList()
        self.matchNext(Lexeme.SYMBOL_CLOSE_PAREN, "Expected a ')'")
        return exprList

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
            self.matchNext(Lexeme.SYMBOL_CLOSE_BRACE, "Expected a '}'")
            # create the AST node for a class
            pirClass = PIR_Class(line, name, pirVars, pirSubs)
            return pirClass

    def pClassVarDecs(self):
        """<classVarDec > →  <classVarModifier> <type>  <varList>;"""
        scope = self.pClassVarModifier()
        typ = self.pType()
        names = self.pVarList()
        self.matchNext(Lexeme.SYMBOL_SEMICOLON, "Expected a ';'")
        line = self.lineNumber
        pirVars = []
        for name in names:
            self.__lineNumber = self.__scanner.getLineNumber()
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

    def pDoStatement(self):
        """<doStatement> →  do identifier <doStatement1><actualParameters>;"""
        self.nextToken()
        #TODO: Add error
        self.matchNext(Lexeme.IDENTIFIER)
        name = self.token[1]
        scope = None
        lk = self.lookaheadToken()[0]
        if lk == Lexeme.SYMBOL_DOT:
            scope = name
            name = self.pDoStatement1()
        params = self.pActualParameters()
        self.__lineNumber = self.__scanner.getLineNumber()
        sub_call = PIR_SubroutineCall(self.lineNumber, scope, name, params)
        self.matchNext(Lexeme.SYMBOL_SEMICOLON, "Expected a ';'")
        self.__lineNumber = self.__scanner.getLineNumber()
        return PIR_DoStatement(self.lineNumber, sub_call)

    def pDoStatement1(self):
        """<doStatement1> →  .identifier | epsilon"""
        self.nextToken()
        #TODO: error
        self.matchNext(Lexeme.IDENTIFIER)
        return self.token[1]

    def pElseStatement(self):
        """<elseStatement> →  else { <statements } | epsilon"""
        self.nextToken()
        self.matchNext(Lexeme.SYMBOL_OPEN_BRACE, "Expected a '{'")
        stmts = self.pStatements()
        self.matchNext(Lexeme.SYMBOL_CLOSE_BRACE, "Expected a '}'")
        return stmts

    def pExpression(self):
        """<expression> →  <exp1><expression'>"""
        operand1 = self.pExp1()
        if self.__lookahead is not None and (self.__lookahead[0][0] == Lexeme.SYMBOL_SEMICOLON or\
                                             self.__lookahead[0][0] == Lexeme.SYMBOL_CLOSE_PAREN or\
                                             self.__lookahead[0][0] == Lexeme.SYMBOL_CLOSE_BRACKET):
            return operand1
        op, operand2 = self.pExpressionp()
        self.__lineNumber = self.__scanner.getLineNumber()
        return PIR_ExpressionBinop(self.lineNumber, op, operand1, operand2)

    def pExpressionList(self):
        """<expressionList> →  <expressionList> | epsilon"""
        exprs = self.pExpressionList1()
        return exprs

    def pExpressionList1(self):
        """<expressionList1> →  <expression><expressionList2>"""
        exprs = []
        exprs.append(self.pExpression())
        lk = self.lookaheadToken()[0]
        if lk == Lexeme.SYMBOL_COMMA:
            exprs = exprs + self.pExpressionList2()
        return exprs

    def pExpressionList2(self):
        """<expressionList2> →  , <expressionList1> | epsilon"""
        self.nextToken()
        exprs = self.pExpressionList1()
        return exprs

    def pExpressionp(self):
        """<expression'> →  & <exp1><expression'> | | <exp1><expression'> | epsilon"""
        if self.matchNext(Lexeme.SYMBOL_SEMICOLON) or self.match(Lexeme.SYMBOL_CLOSE_BRACKET) or\
           self.match(Lexeme.SYMBOL_CLOSE_PAREN) or self.match(Lexeme.SYMBOL_COMMA):
            return None, None
        elif self.match(Lexeme.SYMBOL_AND):
            op = Lexeme.SYMBOL_AND
            operand2 = self.pExpression()
            return op, operand2
        elif self.match(Lexeme.SYMBOL_OR):
            op = Lexeme.SYMBOL_OR
            operand2 = self.pExpression()
            return op, operand2

    def pExp1(self):
        """<exp1> →  <exp2><exp1'>"""
        operand1 = self.pExp2()
        if self.__lookahead[0][0] in [Lexeme.SYMBOL_SEMICOLON, Lexeme.SYMBOL_CLOSE_BRACKET,
                        Lexeme.SYMBOL_CLOSE_PAREN, Lexeme.SYMBOL_COMMA,
                        Lexeme.SYMBOL_AND, Lexeme.SYMBOL_OR]:
            return operand1
        op, operand2 = self.pExp1p()
        if op is None:
            return None, None
        self.__lineNumber = self.__scanner.getLineNumber()
        return PIR_ExpressionBinop(self.lineNumber, op, operand1, operand2)

    def pExp1p(self):
        """<exp1'> →  < <exp2><exp1'> | > <exp2><exp1'> | = <exp2><exp1'>| epsilon"""
        if self.matchNext(Lexeme.SYMBOL_LT):
            op = Lexeme.SYMBOL_LT
            operand2 = self.pExp2()
            return op, operand2
        elif self.match(Lexeme.SYMBOL_GT):
            op = Lexeme.SYMBOL_GT
            operand2 = self.pExp2()
            return op, operand2
        elif self.match(Lexeme.SYMBOL_EQUAL):
            op = Lexeme.SYMBOL_EQUAL
            operand2 = self.pExp2()
            return op, operand2
        elif self.match(Lexeme.SYMBOL_SEMICOLON):
            return None, 'a'

    def pExp2(self):
        """<exp2> →  <exp3><exp2'>"""
        operand1 = self.pExp3()
        if self.__lookahead[0][0] in [Lexeme.SYMBOL_SEMICOLON, Lexeme.SYMBOL_CLOSE_BRACKET,
                        Lexeme.SYMBOL_CLOSE_PAREN, Lexeme.SYMBOL_COMMA,
                        Lexeme.SYMBOL_LT, Lexeme.SYMBOL_GT,
                        Lexeme.SYMBOL_EQUAL, Lexeme.SYMBOL_AND,
                        Lexeme.SYMBOL_OR]:
            return operand1
        op, operand2 = self.pExp2p()
        if op is None:
            return operand1
        self.__lineNumber = self.__scanner.getLineNumber()
        return PIR_ExpressionBinop(self.lineNumber, op, operand1, operand2)

    def pExp2p(self):
        """<exp2'> →  + <exp3><exp2'> | - <exp3><exp2'> | epsilon"""
        if self.matchNext(Lexeme.SYMBOL_PLUS):
            op = Lexeme.SYMBOL_PLUS
            operand2 = self.pExp2()
            return op, operand2
        elif self.match(Lexeme.SYMBOL_MINUS):
            op = Lexeme.SYMBOL_MINUS
            operand2 = self.pExp2()
            return op, operand2
        elif self.match(Lexeme.SYMBOL_SEMICOLON):
            return None, None

    def pExp3(self):
        """<exp3> →  <exp4><exp3'>"""
        operand1 = self.pExp4()
        if self.__lookahead[0][0] in [Lexeme.SYMBOL_SEMICOLON, Lexeme.SYMBOL_CLOSE_BRACKET,
                        Lexeme.SYMBOL_CLOSE_PAREN, Lexeme.SYMBOL_COMMA,
                        Lexeme.SYMBOL_PLUS, Lexeme.SYMBOL_MINUS,
                        Lexeme.SYMBOL_LT, Lexeme.SYMBOL_GT,
                        Lexeme.SYMBOL_EQUAL, Lexeme.SYMBOL_AND,
                        Lexeme.SYMBOL_OR]:
            return operand1
        op, operand2 = self.pExp3p()
        if op is None:
            return None, None
        self.__lineNumber = self.__scanner.getLineNumber()
        return PIR_ExpressionBinop(self.lineNumber, op, operand1, operand2)

    def pExp3p(self):
        """<exp3'> →  * <exp4><exp3'> | / <exp4><exp3'> | epsilon"""
        if self.matchNext(Lexeme.SYMBOL_TIMES):
            op = Lexeme.SYMBOL_TIMES
            operand2 = self.pExp3()
            return op, operand2
        elif self.match(Lexeme.SYMBOL_DIVIDE):
            op = Lexeme.SYMBOL_DIVIDE
            operand2 = self.pExp3()
            return op, operand2
        elif self.match(Lexeme.SYMBOL_SEMICOLON):
            return None, None

    def pExp4(self):
        """<exp4> →  - <exp4> | ~ <exp4> | integerConstant | stringConstant |
                     <keywordConstant> | identifier <exp4Id> |
                     ( <expression> )
        """
        if self.matchNext(Lexeme.SYMBOL_MINUS):
            op = Lexeme.SYMBOL_MINUS
            expr = self.pExp4()
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_ExpressionUnop(self.lineNumber, op, expr)
        elif self.match(Lexeme.SYMBOL_NEGATE):
            op = Lexeme.SYMBOL_NEGATE
            expr = self.pExp4()
        elif self.match(Lexeme.INTEGER_CONST):
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_ExpressionConstant(self.lineNumber, Lexeme.INTEGER_CONST,
                                          self.token[1])
        elif self.match(Lexeme.STRING_CONST):
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_ExpressionConstant(self.lineNumber, Lexeme.STRING_CONST,
                                          self.token[1])
        elif self.match(Lexeme.IDENTIFIER):
            ident = self.token[1]
            lk = self.lookaheadToken()[0]
            if lk == Lexeme.SYMBOL_OPEN_BRACKET:
                expr = self.pExp4Id()
                self.__lineNumber = self.__scanner.getLineNumber()
                return PIR_ExpressionVariable(self.lineNumber, ident, expr)
            elif lk == Lexeme.SYMBOL_DOT:
                name, params = self.pExp4Id()
                self.__lineNumber = self.__scanner.getLineNumber()
                return PIR_SubroutineCall(self.lineNumber, ident, name, params)
            elif lk == Lexeme.SYMBOL_OPEN_PAREN:
                params = self.pExp4Id()
                self.__lineNumber = self.__scanner.getLineNumber()
                return PIR_SubroutineCall(self.lineNumber, None, ident, params)
            elif lk in [Lexeme.SYMBOL_SEMICOLON, Lexeme.SYMBOL_CLOSE_BRACKET,
                        Lexeme.SYMBOL_CLOSE_PAREN, Lexeme.SYMBOL_COMMA,
                        Lexeme.SYMBOL_TIMES, Lexeme.SYMBOL_DIVIDE,
                        Lexeme.SYMBOL_PLUS, Lexeme.SYMBOL_MINUS,
                        Lexeme.SYMBOL_LT, Lexeme.SYMBOL_GT,
                        Lexeme.SYMBOL_EQUAL, Lexeme.SYMBOL_AND,
                        Lexeme.SYMBOL_OR]:
                self.__lineNumber = self.__scanner.getLineNumber()
                return PIR_ExpressionVariable(self.lineNumber, ident, None)
        else:
            return self.pKeywordConstant()

    def pExp4Id(self):
        """<exp4Id> →  [ <expression> ] | . <subroutineName><actualParameters> |
           <actualParameters> | epsilon"""
        if self.lookaheadToken()[0] == Lexeme.SYMBOL_OPEN_PAREN:
            params = self.pActualParams()
            return params
        elif self.matchNext(Lexeme.SYMBOL_OPEN_BRACKET):
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
            return []
        return self.pParameterList()

    def pKeywordConstant(self):
        """<keywordConstant> →  true | false | null | this"""
        if self.matchNext(Lexeme.KW_TRUE):
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_ExpressionConstant(self.lineNumber, (DataTypes.BOOLEAN_SCALAR, None), Lexeme.KW_TRUE)
        elif self.matchNext(Lexeme.KW_FALSE):
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_ExpressionConstant(self.lineNumber, (DataTypes.BOOLEAN_SCALAR, None), Lexeme.KW_FALSE)
        elif self.matchNext(Lexeme.KW_NULL):
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_ExpressionConstant(self.lineNumber, (DataTypes.VOID, None), None)
        elif self.matchNext(Lexeme.KW_THIS):
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_ExpressionConstant(self.lineNumber, (DataTypes.CLASS_SCALAR, None), Lexeme.KW_THIS)

    def pIfStatement(self):
        """<ifStatement> →  if ( <expression> ) { <statements> } <elseStatement>"""
        # Consume if keyword
        self.nextToken()
        self.matchNext(Lexeme.SYMBOL_OPEN_PAREN, "Expected a '('")
        expr = self.pExpression()
        self.matchNext(Lexeme.SYMBOL_CLOSE_PAREN, "Expected a ')'")
        self.matchNext(Lexeme.SYMBOL_OPEN_BRACE, "Expected a '{'")
        stmts = self.pStatements()
        self.matchNext(Lexeme.SYMBOL_CLOSE_BRACE, "Expected a '}'")
        if self.lookaheadToken()[0] == Lexeme.KW_ELSE:
            else_stmt = self.pElseStatement()
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_IfStatement(self.lineNumber, expr, stmts, else_stmt)
        self.__lineNumber = self.__scanner.getLineNumber()
        return PIR_IfStatement(self.lineNumber, expr, stmts)

    def pParameterList(self):
        """<parameterList> →  <type><varName><parameterList1>"""
        params = []
        typ = self.pType()
        name = self.pVarName()
        self.__lineNumber = self.__scanner.getLineNumber()
        pirVarDec = PIR_VariableDeclaration(self.lineNumber, typ, name,
                                            VariableScopes.PARAMETER)
        params.append(pirVarDec)
        params = params + self.pParameterList1()
        return params

    def pParameterList1(self):
        """<parameterList1> →  <parameterList> | epsilon"""
        if self.lookaheadToken()[0] == Lexeme.SYMBOL_CLOSE_PAREN:
            self.nextToken()
            return []
        self.matchNext(Lexeme.SYMBOL_COMMA, "Expected a ','")
        return self.pParameterList()

    def pReturnStatement(self):
        """<returnStatement> →  return <returnStatement1> ;"""
        self.nextToken()
        lk = self.lookaheadToken()[0]
        if lk == Lexeme.SYMBOL_SEMICOLON:
            self.nextToken()
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_ReturnStatement(self.lineNumber)
        expr = self.pReturnStatement1()
        self.matchNext(Lexeme.SYMBOL_SEMICOLON, "Expected a ';'")
        self.__lineNumber = self.__scanner.getLineNumber()
        return PIR_ReturnStatement(self.lineNumber, expr)

    def pReturnStatement1(self):
        """<returnStatement1> →  <expression> | epsilon"""
        expr = self.pExpression()
        return expr

    def pStatement(self):
        """<statement> →  <assignmentStatement> | <ifStatement> |
                          <whileStatement> | <doStatement> |
                          <returnStatement>"""
        lk = self.lookaheadToken()[0] if self.__lookahead is None else self.__lookahead[0][0]
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
        lk = self.lookaheadToken()[0] if self.__lookahead is None else self.__lookahead[0][0]
        while lk != Lexeme.SYMBOL_CLOSE_BRACE:
            statement = self.pStatement()
            statements.append(statement)
            lk = self.lookaheadToken()[0] if self.__lookahead is None else self.__lookahead[0][0]
        return statements

    def pSubroutineBody(self):
        """<subroutineBody> →  <varDec>*<statements>"""
        #TODO: if no variables
        vars = []
        stmts = []
        lk = self.lookaheadToken()[0]
        while lk == Lexeme.KW_INT or lk == Lexeme.KW_CHAR or lk == Lexeme.KW_BOOLEAN or\
              lk ==Lexeme.IDENTIFIER:
            typ, names = self.pVarDec()
            if names is None:
                stmts.append(typ)
                break
            for name in names:
                self.__lineNumber = self.__scanner.getLineNumber()
                var = PIR_VariableDeclaration(self.lineNumber, typ, name,
                                              VariableScopes.LOCAL)
                vars.append(var)
            lk = self.lookaheadToken()[0]
        stmts = stmts + self.pStatements()

        self.__lineNumber = self.__scanner.getLineNumber()
        return PIR_SubroutineBody(self.lineNumber, vars, stmts)

    def pSubroutineDec(self):
        """
        <subroutineDec> →  <subroutineSpecifier>  <subroutineType>
                <subroutineName>  (<formalParameters>) { <subroutineBody> }
        """
        spec = self.pSubroutineSpecifier()
        typ = self.pSubroutineType()
        name = self.pSubroutineName()
        # parse parameter list
        self.matchNext(Lexeme.SYMBOL_OPEN_PAREN, "Expected a '('")
        formal_params = self.pFormalParameters()
        self.matchNext(Lexeme.SYMBOL_CLOSE_PAREN, "Expected a ')'")
        # parse body of a subroutine
        self.matchNext(Lexeme.SYMBOL_OPEN_BRACE, "Expected a '{'")
        body = self.pSubroutineBody()
        self.matchNext(Lexeme.SYMBOL_CLOSE_BRACE, "Expected a '}'")
        self.__lineNumber = self.__scanner.getLineNumber()
        return PIR_SubroutineDeclaration(self.lineNumber, spec, typ, name,
                                         formal_params, body)

    def pSubroutineDecs(self):
        """<subroutineDec>*"""
        subroutines = []
        while self.lookaheadToken()[0] != Lexeme.SYMBOL_CLOSE_BRACE:
            sub = self.pSubroutineDec()
            subroutines.append(sub)
        return subroutines

    def pSubroutineName(self):
        """<subroutineName> →  identifier"""
        #TODO: Error message
        self.matchNext(Lexeme.IDENTIFIER, "")
        return self.token[1]

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
            return (DataTypes.VOID, None)
        return self.pType

    def pType(self):
        """<type> →  int | char | boolean | int[] | char[] | boolean[] | <className>"""
        if self.matchNext(Lexeme.IDENTIFIER):
            return (DataTypes.CLASS_SCALAR, None)
        elif self.match(Lexeme.KW_INT):
            if self.lookaheadToken()[0] == Lexeme.SYMBOL_OPEN_BRACE:
                self.nextToken()
                self.nextToken()
                return (DataTypes.INT_ARRAY, None)
            return (DataTypes.INT_SCALAR, None)
        elif self.match(Lexeme.KW_CHAR):
            if self.lookaheadToken()[0] == Lexeme.SYMBOL_OPEN_BRACE:
                self.nextToken()
                self.nextToken()
                return (DataTypes.CHAR_ARRAY, None)
            return (DataTypes.CHAR_SCALAR, None)
        elif self.match(Lexeme.KW_BOOLEAN):
            if self.lookaheadToken()[0] == Lexeme.SYMBOL_OPEN_BRACE:
                self.nextToken()
                self.nextToken()
                return (DataTypes.BOOLEAN_ARRAY, None)
            return (DataTypes.BOOLEAN_SCALAR, None)

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
        lk = self.lookaheadToken()[0] if self.__lookahead is None else self.__lookahead[0][0]
        if lk == Lexeme.SYMBOL_EQUAL:
            name = self.token[1]
            self.matchNext(Lexeme.SYMBOL_EQUAL)
            expr = self.pExpression()
            self.matchNext(Lexeme.SYMBOL_SEMICOLON, "Expected a ';'")
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_AssignmentStatement(self.lineNumber, name, None, expr), None
        elif lk == Lexeme.SYMBOL_OPEN_BRACE:
            self.nextToken()
            array_expr = self.pVarArray()
            self.matchNext(Lexeme.SYMBOL_EQUAL, "Expected a '='")
            expr = self.pExpression()
            self.matchNext(Lexeme.SYMBOL_SEMICOLON, "Expected a ';'")
            self.__lineNumber = self.__scanner.getLineNumber()
            return PIR_AssignmentStatement(self.lineNumber, variable, array_expr, expr), None
        varNames = self.pVarList()
        self.matchNext(Lexeme.SYMBOL_SEMICOLON, "Expected a ';'")
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
        self.matchNext(Lexeme.IDENTIFIER, "")
        return self.token[1]

    def pWhileStatement(self):
        """<whileStatement> →  while ( <expression> ) { <statements> }"""
        # Consume keyword while
        self.nextToken()
        self.matchNext(Lexeme.SYMBOL_OPEN_PAREN, "Expected a '('")
        expr = self.pExpression()
        self.matchNext(Lexeme.SYMBOL_CLOSE_PAREN, "Expected a ')'")
        self.matchNext(Lexeme.SYMBOL_OPEN_BRACE, "Expected a '{'")
        stmts = self.pStatements()
        self.matchNext(Lexeme.SYMBOL_CLOSE_BRACE, "Expected a '}'")
        self.__lineNumber = self.__scanner.getLineNumber()
        return PIR_WhileStatement(self.lineNumber, expr, stmts)

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
    #tester("Parser/CS420_Homework_4/ParserTests/ExpressionlessSquare/Square.eck")
    #tester("Parser/CS420_Homework_4/ParserTests/ExpressionlessSquare/SquareGame.eck")

    """
    These files test expressions
    """
    #tester("Parser/CS420_Homework_4/ParserTests/ExpressionTests.eck")

    """
    These files require the full parser to be implemented
    """
    #tester("Parser/CS420_Homework_4/ParserTests/Square/Main.eck")
    #tester("Parser/CS420_Homework_4/ParserTests/Square/Square.eck")
    #tester("Parser/CS420_Homework_4/ParserTests/Square/SquareGame.eck")
    #tester("Parser/CS420_Homework_4/ParserTests/ArrayTests.eck")
