"""
Lexical scanner for the Eck programming language
Morgan Bauer
CS420, Spring 2025

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

    def nextChar(self):
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
        pass

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
