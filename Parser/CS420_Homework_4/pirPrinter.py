"""
Printer for PIR trees
Dr. Hilton
CS420, Spring 2025

This file defines a class for printing PIR (Parser Intermediate Representation)
abstract syntax trees.

For this code to work, you must be running Python version 3.8 or later.
"""

from functools import singledispatchmethod
from parserIR import *


class PIR_Printer:
    """
    This class implements a print method for objects derived from the
    PIR_Base class.
    """
    # number of spaces between each printing indentation level
    INDENTATION_INCR = 3

    def __init__(self):
        self.__filename = None   # pathname for output file
        self.__ioStream = None   # I/O stream object used for writing

    def print(self, filename, pirObject):
        self.__filename = filename
        self.__ioStream = open(self.__filename, "w")
        self.printNode(pirObject)
        self.__ioStream.close()

    @singledispatchmethod
    def printNode(self, arg, indentation=0):
        print(f"printNode not implemented yet for objects of type {type(arg)}")

    @printNode.register(PIR_AssignmentStatement)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
        nextIndent = " " * nextIndentation
        self.__ioStream.write(
            f"{arg.lineNumber:3d}{indent}assignment {arg.variable}\n")
        if arg.arrayExpression is not None:
            self.__ioStream.write(
                f"{arg.lineNumber:3d}{nextIndent}array index\n")
            self.printNode(arg.arrayExpression,
                           nextIndentation + PIR_Printer.INDENTATION_INCR)
        self.printNode(arg.expression, nextIndentation)

    @printNode.register(PIR_Class)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
        self.__ioStream.write(f"{arg.lineNumber:3d}{indent}class {arg.name}\n")
        for var in arg.variables:
            self.printNode(var, nextIndentation)
        for sub in arg.subroutines:
            self.printNode(sub, nextIndentation)

    @printNode.register(PIR_DoStatement)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
        self.__ioStream.write(f"{arg.lineNumber:3d}{indent}do\n")
        self.printNode(arg.subprogram, nextIndentation)

    @printNode.register(PIR_ExpressionBinop)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
        self.__ioStream.write(f"{arg.lineNumber:3d}{indent}exprBinop {arg.operator}\n")
        self.printNode(arg.leftExp, nextIndentation)
        self.printNode(arg.rightExp, nextIndentation)

    @printNode.register(PIR_ExpressionConstant)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        self.__ioStream.write(f"{arg.lineNumber:3d}{indent}constant {arg.type} {arg.value}\n")

    @printNode.register(PIR_ExpressionUnop)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
        self.__ioStream.write(f"{arg.lineNumber:3d}{indent}exprUnop {arg.operator}\n")
        print(f"{arg.lineNumber:3d}{indent}exprUnop {arg.operator}\n")
        self.printNode(arg.expression, nextIndentation)

    @printNode.register(PIR_ExpressionVariable)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
        self.__ioStream.write(f"{arg.lineNumber:3d}{indent}expVar {arg.name}")
        if arg.arrayExpression is not None:
            self.__ioStream.write(" array index\n")
            self.printNode(arg.arrayExpression, nextIndentation)
        else:
            self.__ioStream.write("\n")

    @printNode.register(PIR_IfStatement)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
        nextIndent = " " * nextIndentation
        self.__ioStream.write(f"{arg.lineNumber:3d}{indent}if\n")
        self.__ioStream.write(f"{arg.lineNumber:3d}{nextIndent}condition\n")
        self.printNode(arg.condition, nextIndentation + PIR_Printer.INDENTATION_INCR)
        self.__ioStream.write(f"{arg.lineNumber:3d}{nextIndent}then\n")
        for s in arg.thenBranch:
            self.printNode(s, indentation + 2*PIR_Printer.INDENTATION_INCR)
        if arg.elseBranch is not None:
            self.__ioStream.write(f"{arg.lineNumber:3d}{nextIndent}else\n")
            print(f"{arg.lineNumber:3d}{nextIndent}else\n")
            for s in arg.elseBranch:
                self.printNode(s, indentation + 2*PIR_Printer.INDENTATION_INCR)

    @printNode.register(PIR_None)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        self.__ioStream.write(f"{indent}None\n")

    @printNode.register(PIR_ReturnStatement)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        self.__ioStream.write(f"{arg.lineNumber:3d}{indent}return\n")
        if arg.expression is not None:
            nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
            self.printNode(arg.expression, nextIndentation)

    @printNode.register(PIR_SubroutineBody)
    def _(self, arg, indentation=0):
        for v in arg.variables:
            self.printNode(v, indentation)
        for s in arg.statements:
            self.printNode(s, indentation)

    @printNode.register(PIR_SubroutineCall)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
        if arg.varOrClass is None:
            self.__ioStream.write(f"{arg.lineNumber:3d}{indent}subroutineCall {arg.subroutineName}\n")
        else:
            self.__ioStream.write(f"{arg.lineNumber:3d}{indent}subroutineCall {arg.varOrClass}.{arg.subroutineName}\n")
        for p in arg.actualParameters:
            self.printNode(p, nextIndentation)

    @printNode.register(PIR_SubroutineDeclaration)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
        self.__ioStream.write(
            f"{arg.lineNumber:3d}{indent}subroutine {arg.specifier} {arg.type[0]} {arg.name}\n")
        for p in arg.parameters:
            self.printNode(p, nextIndentation)
        self.printNode(arg.body, nextIndentation)

    @printNode.register(PIR_VariableDeclaration)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        self.__ioStream.write(f"{arg.lineNumber:3d}{indent}variable {arg.scope} {arg.type[0]} {arg.name}\n")

    @printNode.register(PIR_WhileStatement)
    def _(self, arg, indentation=0):
        indent = " " * indentation
        nextIndentation = indentation + PIR_Printer.INDENTATION_INCR
        nextIndent = " " * nextIndentation
        self.__ioStream.write(f"{arg.lineNumber:3d}{indent}while\n")
        self.__ioStream.write(f"{arg.lineNumber:3d}{nextIndent}condition\n")
        self.printNode(arg.condition, nextIndentation + PIR_Printer.INDENTATION_INCR)
        self.__ioStream.write(f"{arg.lineNumber:3d}{nextIndent}statements\n")
        for s in arg.statements:
            self.printNode(s, nextIndentation + PIR_Printer.INDENTATION_INCR)
