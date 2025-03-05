"""
Lexical scanner for the Eck programming language
Morgan Bauer
CS420, Spring 2025
Homework 01
Pledged

"""
import string
from lexeme import Lexeme, LexemeMap


class ScannerError(Exception):
    """
    Custom error class for lexical errors in a Eck source code file.
    """

    def __init__(self, value):
        self.value = value

    # __str__ is to print() the value
    def __str__(self):
        return (repr(self.value))


class Scanner:
    """
    Lexical analyzer for the Eck programming language.  Each call to the
    nextLexeme() method will return one Eck lexeme, as a (category, value)
    pair.
    """

    def __init__(self, filename):
        """
        Initialize the Scanner object and open the file to be scanned.
        Input:
            filename        string; path to input file
        """

        # Concatenate all lines of the .eck input file as a string
        self.__file_contents = ''
        with open(filename, 'r') as infile:
            lines = infile.readlines()
            for line in lines:
                self.__file_contents += line

        # An index to keep track of which character in the file is being read
        self.__ch_index = 0

        # Keeps track of line number in the program
        self.__line_number = 1

        # Accepting states for the Scanner's transition graph
        self.__accepting_states = [2, 4, 7, 9, 12, 13]

    def __nextChar(self):
        """
        Returns the next character in the input file and increments the
        Scanner's index counter
        """
        ch = self.__file_contents[self.__ch_index]
        self.__ch_index += 1
        return ch

    def nextLexeme(self):
        """
        Returns the next lexeme in the input stream as a (category, value) pair.
        White space and comments are skipped over.  When the end of file is reached,
        the next lexeme returned should be the pair (Lexeme.EOF, None).
        """
        # Initialize character and state variables
        ch = "Don't Panic"
        state = 0

        try:
            # Loop through characters until in an accepting state
            while (state not in self.__accepting_states):
                # Get next character
                ch = self.__nextChar()

                # increment line number if new line
                if ch == "\n":
                    self.__line_number += 1

                # Start state
                if state == 0:
                    if ch == '"':  # Double quote signifying the start of a stringConstant
                        state = 1
                        str_val = ""
                    elif ch == "0":  # An integer
                        state = 4
                        int_str = ch
                    elif ch in string.digits and ch != "0":  # The first digit of an integer
                        state = 3
                        int_str = ch
                    elif ch == "/":  # Either the first character of a comment or the symbol /
                        state = 5
                    elif ch in string.ascii_letters or ch == "_":  # The first character of an identifier
                        state = 11
                        id_name = ch
                    elif ch in LexemeMap.symbols.keys():  # If the character is a symbol recognized by Eck
                        state = 13
                    elif ch == " ":  # Ignore spaces
                        pass
                    elif ch == "\n":  # Ignore newline
                        pass
                    else:  # Otherwise the character is not in Eck's set of Lexemes
                        raise ScannerError(f"Line {self.__line_number}: illegal character '{ch}'")

                # String constants
                elif state == 1:
                    if ch == '"':  # If the string is closed
                        state = 2
                    else:
                        str_val = str_val + ch

                # Integer constants
                elif state == 3:
                    if ch not in string.digits:  # If the string of digits has ended
                        state = 4

                        # Decrement so the character can be used for the next lexeme
                        self.__ch_index -= 1
                    else:
                        int_str = int_str + ch

                # Comments
                elif state == 5:
                    if ch == "*":  # If a multi-line comment is opened
                        state = 6
                    elif ch == "/":  # If a single line comment is opened
                        state = 10
                    else:  # Otherwise the lexeme is the symbol /
                        state = 7
                        self.__ch_index -= 1 # Decrement so the character can be used for the next lexeme

                # Multi-line comments
                elif state == 6:
                    if ch == "*":
                        state = 8

                # Multi-line comments
                elif state == 8:
                    if ch == "/":  # If comment is closed
                        state = 9
                    else:
                        state = 6

                # Single line comments
                elif state == 10:
                    if ch == "\n":
                        state = 9

                # Identifiers
                elif state == 11:
                    if (ch not in string.ascii_letters) and (ch not in string.digits)\
                    and (ch != "_"):  # Legal identifier terminated
                        state = 12
                        self.__ch_index -= 1
                    else:
                        id_name = id_name + ch

            # Return values depending on accepting state
            if state == 2:
                return Lexeme.STRING_CONST, str_val
            elif state == 4:
                # Get integer value
                int_val = 0
                for digit in int_str:
                    int_val = int_val * 10 + ord(digit) - ord('0')
                return Lexeme.INTEGER_CONST, int_val
            elif state == 7:
                return Lexeme.SYMBOL_DIVIDE, None
            elif state == 9:  # If the lexeme was a comment, get next lexeme
                return self.nextLexeme()
            elif state == 12:
                if id_name in LexemeMap.keywords.keys():
                    return LexemeMap.keywords[id_name], None
                else:
                    return Lexeme.IDENTIFIER, id_name
            elif state == 13:
                return LexemeMap.symbols[ch], None

        # Handle Scanner errors
        except IndexError as err:
            if state == 1:
                raise ScannerError(f"Line {self.__line_number}: end-of-file encountered in a string constant")
            elif state == 6 or state == 8:
                raise ScannerError(f"Line {self.__line_number}: end-of-file encountered in a multi-line comment")
            else:
                return Lexeme.EOF, None


if __name__ == "__main__":
    """
    Testing Code
    This is the script that Dr. Hilton will use to test you scanner.  For full credit,
    the test() function should print "scanned correctly" for each of the supplied
    test files.
    """
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
