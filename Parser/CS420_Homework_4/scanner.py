"""
Lexical scanner for the Eck programming language
Dr. Hilton
CS420, Spring 2025

"""
import string
from lexeme import Lexeme, LexemeMap


class ScannerError(Exception):
    """Custom error class for lexical errors in a Eck source code file."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return (repr(self.value))


class Scanner:
    """Lexical analyzer for the Eck programming language.  Each call to the
    nextLexeme() method will return one Eck lexeme, as a (category, value)
    pair. """

    def __init__(self, filename):
        """Initialize the Scanner object and open the file to be scanned"""
        # instance variables
        self.__char = None        # the last character read from stream
        self.__lineNumber = 1     # current line number in input file
        self.__stream = None      # file object associated with the input file
        # open the input file
        self.__stream = open(filename, "r")
        # prime the pump by reading the first character in the file
        self._nextChar()

    @property
    def char(self):
        return self.__char
    
    def getLineNumber(self):
        return self.__lineNumber

    def _nextChar(self):
        """Returns the next character from the input stream and advances to
        the next character.  None is returned when at the end of file. """
        self.__char = self.__stream.read(1)
        if self.__char == '':
            self.__char = None
        elif self.__char == '\n':
            self.__lineNumber += 1
        return self.__char

    def nextLexeme(self):
        """Returns the next lexeme in the input stream as a (category, value) pair."""
        # skip over any white space and comments
        if self._skipWhitespaceAndComments():
            return (Lexeme.SYMBOL_DIVIDE, None)

        # the current character is the start of a lexeme
        char = self.char
        if char is None:
            # at end of file
            self.__stream.close()
            return (Lexeme.EOF, None)
        elif char == "0":
            self._nextChar()
            return (Lexeme.INTEGER_CONST, 0)
        elif char.isdigit():
            return self._readIntegerConstant()
        elif char == '"':
            return self._readStringConstant()
        elif char == "_" or char.isalpha():
            return self._readIdentifierOrKeyword()
        elif char in LexemeMap.symbols:
            self._nextChar()
            return (LexemeMap.symbols[char], None)
        else:
            # illegal character
            self._nextChar()
            raise ScannerError(
                f"Line {self.getLineNumber()}: illegal character '{char}'")

    def _readIdentifierOrKeyword(self):
        """Reads either an identifier or a keyword from the input stream, returning
        a lexeme pair. 
        """
        word = self.char
        char = self._nextChar()
        # loop through legal characters for identifiers
        while char.isalnum() or char == "_":
            word += char
            char = self._nextChar()
        # determine if the word is a keyword or an identifier
        if word in LexemeMap.keywords:
            return (LexemeMap.keywords[word], None)
        else:
            return (Lexeme.IDENTIFIER, word)

    def _readIntegerConstant(self):
        """Reads an integer constant from the input stream, returning a
        lexeme pair.
        """
        # compute numeric value of the first digit
        val = ord(self.char) - ord("0")
        # read the rest of the digits
        char = self._nextChar()
        while char.isdigit():
            # accumulate the value of the integer
            digit = ord(char) - ord("0")
            val = val * 10 + digit
            char = self._nextChar()
        # make sure integer fits in 16 bits
        if val > 32767:
            raise ScannerError(
                f"Line {self.getLineNumber()}: Integer too large")
        return (Lexeme.INTEGER_CONST, val)

    def _readStringConstant(self):
        """Reads a string constant from the input stream, returning a
        lexeme pair."""
        s = ""
        # accumulate characters until we reach a double quote
        char = self._nextChar()
        while char != '"':
            if char is None:
                raise ScannerError(
                    f"Line {self.getLineNumber()}: end-of-file encountered in a string constant")
            s += char
            char = self._nextChar()
        # read past the end of the string constant
        self._nextChar()
        return (Lexeme.STRING_CONST, s)

    def _skipMultiLineComment(self):
        """Advances the input to the next character past the end of a comment
        delimited by a /* and */ pair. """
        char = self._nextChar()
        # skip over characters until a */ is read
        while True:
            if char is None:
                raise ScannerError(
                    f"Line {self.getLineNumber()}: end-of-file encountered in a multi-line comment")
            elif char == '*' and self._nextChar() == '/':
                # at the end of comment
                self._nextChar()
                return
            else:
                # inside the comment
                char = self._nextChar()

    def _skipSingleLineComment(self):
        """Advances the input to the next character past the end of a
        single line comment """
        # skip over characters until a newline is read
        while self.char != '\n':
            self._nextChar()
        # read past the end of comment
        self._nextChar()

    def _skipWhitespace(self):
        """Advances the input to the next character that is not white space."""
        char = self.char
        while char is not None and char in string.whitespace:
            char = self._nextChar()

    def _skipWhitespaceAndComments(self):
        """Skips over any contiguous whitespace and comments; also detects
        the division symbol lexeme.
        Returns:
            True if a division lexeme is encountered; False, otherwise
        """
        while True:
            self._skipWhitespace()
            if self.char == '/':
                # Either the start of a comment or the division symbol
                self._nextChar()
                if self.char == '/':
                    self._skipSingleLineComment()
                elif self.char == '*':
                    self._skipMultiLineComment()
                else:
                    # division symbol
                    return True
            else:
                # character does not start a comment
                return False


if __name__ == "__main__":
    import os

    def scan(filename, outfilename):
        """Scans a .eck file and writes each lexeme to an output file"""
        with open(outfilename, "w") as outFile:
            scanner = Scanner(filename)
            while True:
                try:
                    category, value = scanner.nextLexeme()
                    # output the lexeme category and value (if there is one)
                    if value is None:
                        outFile.write(f"{category}\n")
                        outFile.flush()
                    else:
                        outFile.write(f"{category}, {value}\n")
                        outFile.flush()

                    # test if we have reached the end-of-file
                    if category == Lexeme.EOF:
                        break

                except ScannerError as err:
                    outFile.write(err.value + "\n")
                    outFile.flush()
                    print(err.value)

    def test(filename):
        """Tests the scanner class by scanning a file and comparing it to a
        known-to-be correct output file"""
        # create the output file names
        root, _ = os.path.splitext(filename)
        scanOutfile = root + ".lexemes"
        answerFilename = root + ".answer"
        # scan the input file
        scan(filename, scanOutfile)
        # operating system-independent way of comparing files
        with open(scanOutfile, "r") as scanFile:
            scanStr = scanFile.read()
        with open(answerFilename, "r") as correctFile:
            correctStr = correctFile.read()
        if (scanStr != correctStr):
            print(f"{filename} does not produce the expected answer")
        else:
            print(f"{filename} scanned correctly")

    test("ScannerTests/Main.eck")
    test("ScannerTests/Square.eck")
    test("ScannerTests/SquareGame.eck")
    test("ScannerTests/Error1.eck")
    test("ScannerTests/Error2.eck")
    test("ScannerTests/Error3.eck")
    test("ScannerTests/Error4.eck")
