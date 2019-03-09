import unittest
from unittest.mock import Mock

from DB.DatabaseManager import DatabaseManager
from Exceptions.OwnExceptions import ExceptionTextAbstraction
from Model.Model import Lecturer
from Text_Processing.TextAbstraction import TextAbstraction


class Test_TextAbstraction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Assumption:
            Axel Hochstein and Martin Spott are Lecturer in the MoodleCourses and have no influence on the
            abstracts.
        """
        cls.textWithEnoughSentences = \
"""Ein Beispieltext.
Von: Kai Kohl der Doktor und Professor ist.
Axel Hochstein und Martin Spott sind ein Professor und ein Doktor.
Die HTW ist eine Hochschule an der Axel Hochstein Doktor und Professor ist.
Ich mag das DWH.

Von: Kai Kohl.
"""
        cls.textWithoutEnoughSentences = """Hier ist nur ein Satz."""
        database = Mock(spec=DatabaseManager)
        lecturer1 = Lecturer(id=1, name="Axel Hochstein")
        lecturer2 = Lecturer(id=2, name="Martin Spott")
        database.getAllLecturer.return_value = [lecturer1, lecturer2]

        cls.textMiner = TextAbstraction(database=database)

    def test_summarize_TextSuccess(self):
        """
        Test if the summarize_Text works with enough sentences
        Procedure:
            1. Take the 2 sentences with the highest score
            2. Take the 3 sentences with the highest score
            ---------
            Verification:
            3. abstract2sentences = expectedResult2
            4. abstract3sentences = expectedResult3
        """
        abstract2sentences = self.textMiner.summarize_Text(self.textWithEnoughSentences, 2, language='german')
        abstract3sentences = self.textMiner.summarize_Text(self.textWithEnoughSentences, 3, language='german')
        expectedResult2 = \
"""-> Von: Kai Kohl der Doktor und Professor ist.
-> Ich mag das DWH.
"""
        expectedResult3 = \
"""-> Von: Kai Kohl der Doktor und Professor ist.
-> Ich mag das DWH.
-> Ein Beispieltext.
"""
        self.assertEqual(abstract2sentences, expectedResult2)
        self.assertEqual(abstract3sentences, expectedResult3)
    def test_summarize_Text_Failed_NotEnoughSentences(self):
        """
        Test if the summarize_Text raise ExceptionTextAbstraction, when the
        text has not enough sentences
        Procedure:
            1. Call function with not enough sentences
            2. Call function with not enough sentences
            ---------
            Verification:
            3. raise ExceptionTextAbstraction
            4. raise ExceptionTextAbstraction
                """
        self.assertRaises(ExceptionTextAbstraction, self.textMiner.summarize_Text, self.textWithoutEnoughSentences, 3, language='german')
        self.assertRaises(ExceptionTextAbstraction, self.textMiner.summarize_Text, self.textWithoutEnoughSentences, 2, language='german')

    def test_frequency_WordsSuccess(self):
        """
        Test if the frequency_Words works
        Procedure:
            1. Take the 4 words with the highest score
            2. Take the 5 words with the highest score
            ---------
            Verification:
            3. abstract4words = expectedResult4
            4. abstract5words = expectedResult5
        """
        abstract4words = self.textMiner.frequency_Words(self.textWithEnoughSentences, 4, language='german')
        abstract5words = self.textMiner.frequency_Words(self.textWithEnoughSentences, 5, language='german')
        expectedResult4 = \
"""-> kai: 2
-> kohl: 2
-> beispieltext: 1
-> mag: 1
"""
        expectedResult5 = \
"""-> kai: 2
-> kohl: 2
-> beispieltext: 1
-> mag: 1
-> dwh: 1
"""
        self.assertEqual(abstract4words, expectedResult4)
        self.assertEqual(abstract5words, expectedResult5)


    def test_frequency_Words_Failed_NotEnoughWords(self):
        """
        Test if the frequency_Words raise ExceptionTextAbstraction, when the
        text has not enough words
        Procedure:
            1. Call function with not enough words
            2. Call function with not enough words
            ---------
            Verification:
            3. raise ExceptionTextAbstraction
            4. raise ExceptionTextAbstraction
                """
        self.assertRaises(ExceptionTextAbstraction, self.textMiner.frequency_Words, self.textWithEnoughSentences, 6, language='german')
        self.assertRaises(ExceptionTextAbstraction, self.textMiner.frequency_Words, self.textWithEnoughSentences, 7, language='german')


    def test_compute_frequencies_Success(self):
        """
        Test if the compute_frequencies retun a dictionary with the right values
        Assumption all sentences are in lowercase
        Procedure:
            1. create a list of sentences, which contains a list of words
            2. add stopwords to the set of stopwords, to check if the stopword works
            3. Call function the list
            ---------
            Verification:
            4. returnDict = expectedResult4
                """
        listOfLowerSentences = [["kai", "kohl", "htw", "."], ["kai", "master"]]
        self.textMiner.stopwords.add("htw")
        self.textMiner.stopwords.add(".")
        self.textMiner.stopwords.add("master")
        returnDict = self.textMiner._compute_frequencies(listOfLowerSentences)

        self.assertGreaterEqual(returnDict["kai"], 0.66)
        self.assertLess(returnDict["kai"], 0.67)

        self.assertGreaterEqual(returnDict["kohl"], 0.33)
        self.assertLess(returnDict["kohl"], 0.34)

    def test__fillStopwords_Success(self):
        """
        Test if the _fillStopwords fill the set of stopwords
            Procedure:
            1. set language
            2. fill stopwords
            ---------
            Verification:
            3. In stop word set are more than 0 words
            4. Are the lecturer in the set
                """
        self.textMiner.language = 'german'
        self.textMiner._fillStopwords()
        self.assertGreaterEqual(len(self.textMiner.stopwords), 0)
        self.assertTrue('hochstein' in self.textMiner.stopwords)
        self.assertTrue('spott' in self.textMiner.stopwords)




if __name__ == '__main__':
    unittest.main()
