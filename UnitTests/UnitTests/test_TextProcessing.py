import logging
import unittest
from unittest import mock
from unittest.mock import Mock, MagicMock

from DB.DatabaseManager import DatabaseManager
from Exceptions.OwnExceptions import ExceptionReadDataToText, ExceptionTextAbstraction, ExceptionCheckLanguage
from FileHandler.FileHandler import FileHandler
from Model.Model import CourseData
from Text_Processing.TextCleaner import TextCleaner
from Text_Processing.FileToText import FileToText
from Text_Processing.TextAbstraction import TextAbstraction
from Text_Processing.TextProcessing import TextProcessing
from Text_Processing.CheckLanguage import CheckLanguage

class TestTextProcessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @mock.patch("multiprocessing.pool.Pool")
    @mock.patch("multiprocessing.pool.Pool.apply_async")
    def test_textProcessor_Success(self, mock_apply_async, mock_pool):
        """
        Test if the text processing process will work right.
        Procedure:
            1. Set the mocking results
            2. call the function
            ---------
            Verification:
            3. check if file handler was called right
            4. check if multiprocessing was called right
            5. check if text cleaner was called right
            6. check if check language was called right
            7. check if summarize text was called right
            8. check if frequency_words was called right
            9. check if update course data text fields was called right
            10. check if the course data object is right
        """
        dummyCourseData = CourseData(id=1, name="test.pdf", dataType="pdf")

        mock_database = Mock(spec=DatabaseManager)
        mock_fileToText = Mock(spec=FileToText)
        mock_textAbstraction = Mock(spec=TextAbstraction)
        mock_fileHandler = Mock(spec=FileHandler)
        mock_checkLanguage = Mock(spec=CheckLanguage)
        mock_textCleaner = Mock(spec=TextCleaner)
        textProcesser = TextProcessing(database=mock_database, fileHandler=mock_fileHandler, path="C:/", textSummarizer=mock_textAbstraction, fileToText=mock_fileToText, checkLanguage=mock_checkLanguage, textCleaner=mock_textCleaner)


        # mocking results
        resultFullText = "Das ist ein Volltext"
        resultAbstract = "Das ist ein Beispiel Abstract"
        resultWordFrequency = "Das 1; ein 1"
        resultCleanText = "Das ist ein sauberer Text"
        resultLanguage = 'german'

        # set mocking results
        mock_get = MagicMock()
        mock_get_function = MagicMock(return_value=resultFullText)
        mock_get.get = mock_get_function
        mock_apply_async.apply_async.return_value = mock_get
        mock_pool.return_value = mock_apply_async
        mock_fileHandler.saveFile.return_value = "C:/test.pdf"
        mock_fileToText.fileToText.return_value = resultFullText
        mock_textCleaner.cleaningText.return_value = resultCleanText
        mock_checkLanguage.checkLanguage.return_value = resultLanguage
        mock_textAbstraction.summarize_Text.return_value = resultAbstract
        mock_textAbstraction.frequency_Words.return_value = resultWordFrequency
        textProcesser.textProcessing(dummyCourseData)

        # check if FileHandler was called right
        mock_fileHandler.saveFile.assert_called_with(dummyCourseData, "C:/")
        self.assertTrue(mock_fileHandler.saveFile.called)

        # check if multiprocessing was called right
        called_args = mock_apply_async.apply_async.call_args_list[0][1]
        self.assertTrue(called_args['args'] == ("C:/test.pdf", "pdf"))
        self.assertTrue(called_args['func'] == mock_fileToText.fileToText)
        self.assertTrue(mock_apply_async.apply_async.called)

        # check if text cleaner was called right
        mock_textCleaner.cleaningText.assert_called_with(resultFullText)
        self.assertTrue(mock_textCleaner.cleaningText.called)

        # check if check language was called right
        mock_checkLanguage.checkLanguage.assert_called_with(resultCleanText)
        self.assertTrue(mock_checkLanguage.checkLanguage.called)

        # check if summarize text was called right
        mock_textAbstraction.summarize_Text.assert_called_with(resultCleanText, 5, language=resultLanguage)
        self.assertTrue(mock_textAbstraction.summarize_Text.called)

        # check if frequency_words was called right
        mock_textAbstraction.frequency_Words.assert_called_with(resultCleanText, 10, language=resultLanguage)
        self.assertTrue(mock_textAbstraction.frequency_Words.called)

        # check if update course data text fields was called right
        mock_database.UpdateCourseDataTextFields.assert_called_with(dummyCourseData)
        self.assertTrue(mock_database.UpdateCourseDataTextFields.called)

        # check if the course data object is right
        self.assertEqual(dummyCourseData.fullText, resultFullText)
        self.assertEqual(dummyCourseData.abstract, resultAbstract)
        self.assertEqual(dummyCourseData.abstractWordFrequency, resultWordFrequency)
        self.assertEqual(dummyCourseData.error, None)


    @mock.patch("multiprocessing.pool.Pool")
    @mock.patch("multiprocessing.pool.Pool.apply_async")
    def test_textProcessor_ExceptionReadDataToText(self, mock_apply_async, mock_pool):
        """
        Test if the text processing process will work right, if a ExceptionReadDataToText error pop up
        Procedure:
            1. Set the mocking results
            2. call the function
            ---------
            Verification:
            3. check if file handler was called right
            4. check if multiprocessing was called right
            5. check if text cleaner was not called
            6. check if check language was not called
            7. check if summarize text was not called
            8. check if frequency_words was not called
            9. check if update course data text fields was called right
            10. check if the course data object is right
        """

        def my_side_effect(func, args):
            raise ExceptionReadDataToText("ExceptionReadDataToText")

        dummyCourseData = CourseData(id=1, name="test.pdf", dataType="pdf")

        mock_database = Mock(spec=DatabaseManager)
        mock_fileToText = Mock(spec=FileToText)
        mock_textAbstraction = Mock(spec=TextAbstraction)
        mock_fileHandler = Mock(spec=FileHandler)
        mock_checkLanguage = Mock(spec=CheckLanguage)
        mock_textCleaner = Mock(spec=TextCleaner)
        textProcesser = TextProcessing(database=mock_database, fileHandler=mock_fileHandler, path="C:/",
                                       textSummarizer=mock_textAbstraction, fileToText=mock_fileToText,
                                       checkLanguage=mock_checkLanguage, textCleaner=mock_textCleaner)

        # mocking results
        resultFullText = "Das ist ein Volltext"
        resultAbstract = "Das ist ein Beispiel Abstract"
        resultWordFrequency = "Das 1; ein 1"
        resultCleanText = "Das ist ein sauberer Text"
        resultLanguage = 'german'

        # set mocking results
        mock_apply_async.apply_async.side_effect = my_side_effect
        mock_pool.return_value = mock_apply_async
        mock_fileHandler.saveFile.return_value = "C:/test.pdf"
        mock_fileToText.fileToText.return_value = resultFullText
        mock_textCleaner.cleaningText.return_value = resultCleanText
        mock_checkLanguage.checkLanguage.return_value = resultLanguage
        mock_textAbstraction.summarize_Text.return_value = resultAbstract
        mock_textAbstraction.frequency_Words.return_value = resultWordFrequency
        textProcesser.textProcessing(dummyCourseData)

        # check if FileHandler was called right
        mock_fileHandler.saveFile.assert_called_with(dummyCourseData, "C:/")
        self.assertTrue(mock_fileHandler.saveFile.called)

        # check if multiprocessing was called right
        called_args = mock_apply_async.apply_async.call_args_list[0][1]
        self.assertTrue(called_args['args'] == ("C:/test.pdf", "pdf"))
        self.assertTrue(called_args['func'] == mock_fileToText.fileToText)
        self.assertTrue(mock_apply_async.apply_async.called)

        # check if text cleaner was not called
        self.assertFalse(mock_textCleaner.cleaningText.called)

        # check if check language was not called
        self.assertFalse(mock_checkLanguage.checkLanguage.called)

        # check if summarize text was not called
        self.assertFalse(mock_textAbstraction.summarize_Text.called)

        # check if frequency_words was not called
        self.assertFalse(mock_textAbstraction.frequency_Words.called)

        # check if update course data text fields was called right
        mock_database.UpdateCourseDataTextFields.assert_called_with(dummyCourseData)
        self.assertTrue(mock_database.UpdateCourseDataTextFields.called)

        # check if the course data object is right
        self.assertEqual(dummyCourseData.fullText, None)
        self.assertEqual(dummyCourseData.abstract, None)
        self.assertEqual(dummyCourseData.abstractWordFrequency, None)
        self.assertEqual(dummyCourseData.error, "ExceptionReadDataToText")

    @mock.patch("multiprocessing.pool.Pool")
    @mock.patch("multiprocessing.pool.Pool.apply_async")
    def test_textProcessor_TextIsEmpty(self, mock_apply_async, mock_pool):
        """
        Test if the text processing process will work right, if the read text is empty
        Procedure:
            1. Set the mocking results
            2. call the function
            ---------
            Verification:
            3. check if file handler was called right
            4. check if multiprocessing was called right
            5. check if text cleaner was called right
            6. check if check language was called right
            7. check if summarize text was called right
            8. check if frequency_words was called right
            9. check if update course data text fields was called right
            10. check if the course data object is right
        """
        dummyCourseData = CourseData(id=1, name="test.pdf", dataType="pdf")

        mock_database = Mock(spec=DatabaseManager)
        mock_fileToText = Mock(spec=FileToText)
        mock_textAbstraction = Mock(spec=TextAbstraction)
        mock_fileHandler = Mock(spec=FileHandler)
        mock_checkLanguage = Mock(spec=CheckLanguage)
        mock_textCleaner = Mock(spec=TextCleaner)
        textProcesser = TextProcessing(database=mock_database, fileHandler=mock_fileHandler, path="C:/",
                                       textSummarizer=mock_textAbstraction, fileToText=mock_fileToText,
                                       checkLanguage=mock_checkLanguage, textCleaner=mock_textCleaner)

        # mocking results
        resultFullText = ""

        # set mocking results
        mock_get = MagicMock()
        mock_get_function = MagicMock(return_value=resultFullText)
        mock_get.get = mock_get_function
        mock_apply_async.apply_async.return_value = mock_get
        mock_pool.return_value = mock_apply_async
        mock_fileHandler.saveFile.return_value = "C:/test.pdf"
        mock_fileToText.fileToText.return_value = resultFullText

        textProcesser.textProcessing(dummyCourseData)

        # check if FileHandler was called right
        mock_fileHandler.saveFile.assert_called_with(dummyCourseData, "C:/")
        self.assertTrue(mock_fileHandler.saveFile.called)

        # check if multiprocessing was called right
        called_args = mock_apply_async.apply_async.call_args_list[0][1]
        self.assertTrue(called_args['args'] == ("C:/test.pdf", "pdf"))
        self.assertTrue(called_args['func'] == mock_fileToText.fileToText)
        self.assertTrue(mock_apply_async.apply_async.called)

        # check if text cleaner was not called
        self.assertFalse(mock_textCleaner.cleaningText.called)

        # check if check language was not called
        self.assertFalse(mock_checkLanguage.checkLanguage.called)

        # check if summarize text was not called
        self.assertFalse(mock_textAbstraction.summarize_Text.called)

        # check if frequency_words was not called
        self.assertFalse(mock_textAbstraction.frequency_Words.called)

        # check if update course data text fields was called right
        mock_database.UpdateCourseDataTextFields.assert_called_with(dummyCourseData)
        self.assertTrue(mock_database.UpdateCourseDataTextFields.called)

        # check if the course data object is right
        self.assertEqual(dummyCourseData.fullText, None)
        self.assertEqual(dummyCourseData.abstract, None)
        self.assertEqual(dummyCourseData.abstractWordFrequency, None)
        self.assertEqual(dummyCourseData.error, "Die Datei besteht wahrscheinlich nur aus Bildern. Es gibt keinen Text")

    @mock.patch("multiprocessing.pool.Pool")
    @mock.patch("multiprocessing.pool.Pool.apply_async")
    def test_textProcessor_LanguageNotSupported(self, mock_apply_async, mock_pool):
        """
        Test if the text processing process will work right, if the language of text of the course data is not supported
        Procedure:
            1. Set the mocking results
            2. call the function
            ---------
            Verification:
            3. check if file handler was called right
            4. check if multiprocessing was called right
            5. check if text cleaner was called right
            6. check if check language was called right
            7. check if summarize text was called right
            8. check if frequency_words was called right
            9. check if update course data text fields was called right
            10. check if the course data object is right
        """
        dummyCourseData = CourseData(id=1, name="test.pdf", dataType="pdf")

        mock_database = Mock(spec=DatabaseManager)
        mock_fileToText = Mock(spec=FileToText)
        mock_textAbstraction = Mock(spec=TextAbstraction)
        mock_fileHandler = Mock(spec=FileHandler)
        mock_checkLanguage = Mock(spec=CheckLanguage)
        mock_textCleaner = Mock(spec=TextCleaner)
        textProcesser = TextProcessing(database=mock_database, fileHandler=mock_fileHandler, path="C:/",
                                       textSummarizer=mock_textAbstraction, fileToText=mock_fileToText,
                                       checkLanguage=mock_checkLanguage, textCleaner=mock_textCleaner)

        # mocking results
        resultFullText = "Das ist ein Volltext"
        resultCleanText = "Das ist ein sauberer Text"
        resultLanguage = 'uncertain'

        # set mocking results
        mock_get = MagicMock()
        mock_get_function = MagicMock(return_value=resultFullText)
        mock_get.get = mock_get_function
        mock_apply_async.apply_async.return_value = mock_get
        mock_pool.return_value = mock_apply_async
        mock_fileHandler.saveFile.return_value = "C:/test.pdf"
        mock_fileToText.fileToText.return_value = resultFullText
        mock_textCleaner.cleaningText.return_value = resultCleanText
        mock_checkLanguage.checkLanguage.return_value = resultLanguage
        textProcesser.textProcessing(dummyCourseData)

        # check if FileHandler was called right
        mock_fileHandler.saveFile.assert_called_with(dummyCourseData, "C:/")
        self.assertTrue(mock_fileHandler.saveFile.called)

        # check if multiprocessing was called right
        called_args = mock_apply_async.apply_async.call_args_list[0][1]
        self.assertTrue(called_args['args'] == ("C:/test.pdf", "pdf"))
        self.assertTrue(called_args['func'] == mock_fileToText.fileToText)
        self.assertTrue(mock_apply_async.apply_async.called)

        # check if text cleaner was called right
        mock_textCleaner.cleaningText.assert_called_with(resultFullText)
        self.assertTrue(mock_textCleaner.cleaningText.called)

        # check if check language was called right
        mock_checkLanguage.checkLanguage.assert_called_with(resultCleanText)
        self.assertTrue(mock_checkLanguage.checkLanguage.called)

        # check if summarize text was not called
        self.assertFalse(mock_textAbstraction.summarize_Text.called)

        # check if frequency_words was not called
        self.assertFalse(mock_textAbstraction.frequency_Words.called)

        # check if update course data text fields was called right
        mock_database.UpdateCourseDataTextFields.assert_called_with(dummyCourseData)
        self.assertTrue(mock_database.UpdateCourseDataTextFields.called)

        # check if the course data object is right
        self.assertEqual(dummyCourseData.fullText, resultFullText)
        self.assertEqual(dummyCourseData.abstract, None)
        self.assertEqual(dummyCourseData.abstractWordFrequency, None)
        self.assertEqual(dummyCourseData.error, "Die Sprache der Datei wird nicht unterstuetzt.")

    @mock.patch("multiprocessing.pool.Pool")
    @mock.patch("multiprocessing.pool.Pool.apply_async")
    def test_textProcessor_ExceptionTextAbstraction(self, mock_apply_async, mock_pool):
        """
        Test if the text processing process will work right, if a ExceptionTextAbstraction pop up
        Procedure:
            1. Set the mocking results
            2. call the function
            ---------
            Verification:
            3. check if file handler was called right
            4. check if multiprocessing was called right
            5. check if text cleaner was called right
            6. check if check language was called right
            7. check if summarize text was called right
            8. check if frequency_words was called right
            9. check if update course data text fields was called right
            10. check if the course data object is right
        """
        def my_side_effect(func, args, language):
            raise ExceptionTextAbstraction("ExceptionReadDataToText")
        # mocking results
        dummyCourseData = CourseData(id=1, name="test.pdf", dataType="pdf")

        mock_database = Mock(spec=DatabaseManager)
        mock_fileToText = Mock(spec=FileToText)
        mock_textAbstraction = Mock(spec=TextAbstraction)
        mock_fileHandler = Mock(spec=FileHandler)
        mock_checkLanguage = Mock(spec=CheckLanguage)
        mock_textCleaner = Mock(spec=TextCleaner)
        textProcesser = TextProcessing(database=mock_database, fileHandler=mock_fileHandler, path="C:/",
                                       textSummarizer=mock_textAbstraction, fileToText=mock_fileToText,
                                       checkLanguage=mock_checkLanguage, textCleaner=mock_textCleaner)

        resultFullText = "Das ist ein Volltext"
        resultCleanText = "Das ist ein sauberer Text"
        resultLanguage = 'german'

        # set mocking results
        mock_get = MagicMock()
        mock_get_function = MagicMock(return_value=resultFullText)
        mock_get.get = mock_get_function
        mock_apply_async.apply_async.return_value = mock_get
        mock_pool.return_value = mock_apply_async
        mock_fileHandler.saveFile.return_value = "C:/test.pdf"
        mock_fileToText.fileToText.return_value = resultFullText
        mock_textCleaner.cleaningText.return_value = resultCleanText
        mock_checkLanguage.checkLanguage.return_value = resultLanguage
        mock_textAbstraction.summarize_Text.side_effect = my_side_effect
        textProcesser.textProcessing(dummyCourseData)

        # check if FileHandler was called right
        mock_fileHandler.saveFile.assert_called_with(dummyCourseData, "C:/")
        self.assertTrue(mock_fileHandler.saveFile.called)

        # check if multiprocessing was called right
        called_args = mock_apply_async.apply_async.call_args_list[0][1]
        self.assertTrue(called_args['args'] == ("C:/test.pdf", "pdf"))
        self.assertTrue(called_args['func'] == mock_fileToText.fileToText)
        self.assertTrue(mock_apply_async.apply_async.called)

        # check if text cleaner was called right
        mock_textCleaner.cleaningText.assert_called_with(resultFullText)
        self.assertTrue(mock_textCleaner.cleaningText.called)

        # check if check language was called right
        mock_checkLanguage.checkLanguage.assert_called_with(resultCleanText)
        self.assertTrue(mock_checkLanguage.checkLanguage.called)

        # check if summarize text was called right
        mock_textAbstraction.summarize_Text.assert_called_with(resultCleanText, 5, language=resultLanguage)
        self.assertTrue(mock_textAbstraction.summarize_Text.called)

        # check if frequency_words was not called
        self.assertFalse(mock_textAbstraction.frequency_Words.called)

        # check if update course data text fields was called right
        mock_database.UpdateCourseDataTextFields.assert_called_with(dummyCourseData)
        self.assertTrue(mock_database.UpdateCourseDataTextFields.called)

        # check if the course data object is right
        self.assertEqual(dummyCourseData.fullText, resultFullText)
        self.assertEqual(dummyCourseData.abstract, None)
        self.assertEqual(dummyCourseData.abstractWordFrequency, None)
        self.assertEqual(dummyCourseData.error, "Die Datei besitzt weniger Sätze oder Wörter, als die Zusammenfassung benötigt.")

    @mock.patch("multiprocessing.pool.Pool")
    @mock.patch("multiprocessing.pool.Pool.apply_async")
    def test_textProcessor_ExceptionCheckLanguage(self, mock_apply_async, mock_pool):
        """
        Test if the text processing process will work right, if a ExceptionTextAbstraction pop up
        Procedure:
            1. Set the mocking results
            2. call the function
            ---------
            Verification:
            3. check if file handler was called right
            4. check if multiprocessing was called right
            5. check if text cleaner was called right
            6. check if check language was called right
            7. check if summarize text was called right
            8. check if frequency_words was called right
            9. check if update course data text fields was called right
            10. check if the course data object is right
        """

        def my_side_effect(text):
            raise ExceptionCheckLanguage("ExceptionCheckLanguage")

        dummyCourseData = CourseData(id=1, name="test.pdf", dataType="pdf")

        mock_database = Mock(spec=DatabaseManager)
        mock_fileToText = Mock(spec=FileToText)
        mock_textAbstraction = Mock(spec=TextAbstraction)
        mock_fileHandler = Mock(spec=FileHandler)
        mock_checkLanguage = Mock(spec=CheckLanguage)
        mock_textCleaner = Mock(spec=TextCleaner)
        textProcesser = TextProcessing(database=mock_database, fileHandler=mock_fileHandler, path="C:/",
                                       textSummarizer=mock_textAbstraction, fileToText=mock_fileToText,
                                       checkLanguage=mock_checkLanguage, textCleaner=mock_textCleaner)

        # mocking results
        resultFullText = "Das ist ein Volltext"
        resultCleanText = "Das ist ein sauberer Text"

        # set mocking results
        mock_get = MagicMock()
        mock_get_function = MagicMock(return_value=resultFullText)
        mock_get.get = mock_get_function
        mock_apply_async.apply_async.return_value = mock_get
        mock_pool.return_value = mock_apply_async
        mock_fileHandler.saveFile.return_value = "C:/test.pdf"
        mock_fileToText.fileToText.return_value = resultFullText
        mock_textCleaner.cleaningText.return_value = resultCleanText
        mock_checkLanguage.checkLanguage.side_effect = my_side_effect

        textProcesser.textProcessing(dummyCourseData)

        # check if FileHandler was called right
        mock_fileHandler.saveFile.assert_called_with(dummyCourseData, "C:/")
        self.assertTrue(mock_fileHandler.saveFile.called)

        # check if multiprocessing was called right
        called_args = mock_apply_async.apply_async.call_args_list[0][1]
        self.assertTrue(called_args['args'] == ("C:/test.pdf", "pdf"))
        self.assertTrue(called_args['func'] == mock_fileToText.fileToText)
        self.assertTrue(mock_apply_async.apply_async.called)

        # check if text cleaner was called right
        mock_textCleaner.cleaningText.assert_called_with(resultFullText)
        self.assertTrue(mock_textCleaner.cleaningText.called)

        # check if check language was called right
        mock_checkLanguage.checkLanguage.assert_called_with(resultCleanText)
        self.assertTrue(mock_checkLanguage.checkLanguage.called)

        # check if summarize text was not called
        self.assertFalse(mock_textAbstraction.summarize_Text.called)

        # check if frequency_words was not called
        self.assertFalse(mock_textAbstraction.frequency_Words.called)

        # check if update course data text fields was called right
        mock_database.UpdateCourseDataTextFields.assert_called_with(dummyCourseData)
        self.assertTrue(mock_database.UpdateCourseDataTextFields.called)

        # check if the course data object is right
        self.assertEqual(dummyCourseData.fullText, resultFullText)
        self.assertEqual(dummyCourseData.abstract, None)
        self.assertEqual(dummyCourseData.abstractWordFrequency, None)
        self.assertEqual(dummyCourseData.error, "ExceptionCheckLanguage")


if __name__ == '__main__':
    unittest.main()
