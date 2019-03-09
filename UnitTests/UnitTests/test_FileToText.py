import unittest
import os

from Exceptions.OwnExceptions import ExceptionReadDataToText
from Text_Processing.FileToText import FileToText


class TestFileToText(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pathTestFiles = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + "/TestFiles/"
        cls.fileToText = FileToText()
    def test_fileToText_SuccessReadPDF(self):
        """
        Test if the fileToText function with pdf scripts works
        Procedure:
            1. Create the path to file
            2. set dataType
            3. read text from file
            ---------
            Verification:
            4. text = expectedResult
        """
        pdfData = self.pathTestFiles + 'PDF_Test_Data.pdf'
        dataType = 'pdf'

        text = self.fileToText.fileToText(filePath=pdfData, datatype=dataType)

        expectedResult = """Das ist die Beispiel Überschrift. 
• Das ist der erste Stichpunkt. 
• Das ist der Zweite Stichpunkt, der länger ist. 
Hier ist noch ein Satz!. 
"""
        self.assertEqual(text, expectedResult)

    def test_fileToText_SuccessReadPPTX(self):
        """
        Test if the fileToText function with pptx scripts works
        Procedure:
            1. Create the path to file
            2. set dataType
            3. read text from file
            ---------
            Verification:
            4. text = expectedResult
        """
        pdfData = self.pathTestFiles + 'PPTX_Test_Data.pptx'
        dataType = 'pptx'

        text = self.fileToText.fileToText(filePath=pdfData, datatype=dataType)

        expectedResult = """Das ist die Beispiel Überschrift. Das ist der erste Stichpunkt. Das ist der Zweite Stichpunkt, der länger ist. Hier ist noch ein Satz!. """

        self.assertEqual(text, expectedResult)

    def test_fileToText_SuccessReadDOCX(self):
        """
        Test if the fileToText function with docx scripts works
        Procedure:
            1. Create the path to file
            2. set dataType
            3. read text from file
            ---------
            Verification:
            4. text = expectedResult
        """
        pdfData = self.pathTestFiles + 'DOCX_Test_Data.docx'
        dataType = 'docx'

        text = self.fileToText.fileToText(filePath=pdfData, datatype=dataType)

        expectedResult = """Das ist die Beispiel Überschrift
Das ist der erste Stichpunkt
Das ist der Zweite Stichpunkt, der länger ist

Hier ist noch ein Satz!

"""
        self.assertEqual(text, expectedResult)

    def test_fileToText_SuccessReadHTML(self):
        """
        Test if the fileToText function with html scripts works
        Procedure:
            1. Create the path to file
            2. set dataType
            3. read text from file
            ---------
            Verification:
            4. text = expectedResult
        """
        pdfData = self.pathTestFiles + 'HTML_Test_Data.html'
        dataType = 'html'

        text = self.fileToText.fileToText(filePath=pdfData, datatype=dataType)

        expectedResult = """Das ist die Beispiel Überschrift. Das ist die Unterüberschrift. Das ist die Unterüberschrift5. Das ist der erste Stichpunkt. Das ist der Zweite Stichpunkt, der länger ist. Hier ist noch ein Satz!"""

        self.assertEqual(text, expectedResult)

    def test_fileToText_Success_wrongDataType(self):
        """
        Test if the fileToText give an empty string back, if an unsupported datatype is an argument
        Procedure:
            1. Create the path to file
            2. set dataType, which is not supported
            3. read text from file
            ---------
            Verification:
            4. text = ""
        """
        pdfData = self.pathTestFiles + 'HTML_Test_Data.html'
        dataType = 'ht1'

        text = self.fileToText.fileToText(filePath=pdfData, datatype=dataType)

        expectedResult = ""
        self.assertEqual(text, expectedResult)

    def test_fileToText_Failed_PDF_Password(self):
        """
        Test if the fileToText raise ExceptionReadDataToText when the pdf file is protected with a password
        Procedure:
            1. Create the path to file
            2. set dataType, which is not supported
            3. read text from file
            ---------
            Verification:
            4. raise ExceptionReadDataToText
        """
        pdfData = self.pathTestFiles + 'PDF_Test_Data_Password.pdf'
        dataType = 'pdf'

        self.assertRaises(ExceptionReadDataToText, self.fileToText.fileToText, filePath=pdfData, datatype=dataType)

    def test_fileToText_Failed_PDF_Is_not_Extracable(self):
        """
        Test if the fileToText raise ExceptionReadDataToText when the pdf file is not extractable
        Procedure:
            1. Create the path to file
            2. set dataType, which is not supported
            3. read text from file
            ---------
            Verification:
            4. raise ExceptionReadDataToText
        """
        pdfData = self.pathTestFiles + 'PDF_Test_Data_Not_Extractable.pdf'
        dataType = 'pdf'

        self.assertRaises(ExceptionReadDataToText, self.fileToText.fileToText, filePath=pdfData, datatype=dataType)
if __name__ == '__main__':
    unittest.main()