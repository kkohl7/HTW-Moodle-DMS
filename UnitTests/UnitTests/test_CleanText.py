from twisted.trial import unittest

from Text_Processing.TextCleaner import TextCleaner


class TestCleanText(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.textCleaner = TextCleaner()
        cls.textWithMultipleNewLines = "Hallo, mein Name ist kai. \n\n\n\n"
        cls.textWithMultiplePoints = "Hallo... So wird es weiter gehen..."
        cls.textWithHtmlLink = "Hallo schau mal hier: http://www.google.de"
    def test_cleaningText_Success(self):
        """
        Test if the cleaningText function will delete links multiple points and multiple \n from the source text
        Procedure:
            1. start cleaner
            2. set expected results
        Verification:
            3. textRemoveNewLines = expectedResultNewLines
            4. textRemoveMultiplePoints = expectedResultMultiplePoints
            5. textRemoveHtmlLink = expectedResultHtmlLink
        """
        textRemoveNewLines = self.textCleaner.cleaningText(self.textWithMultipleNewLines)
        textRemoveMultiplePoints = self.textCleaner.cleaningText(self.textWithMultiplePoints)
        textRemoveHtmlLink = self.textCleaner.cleaningText(self.textWithHtmlLink)
        expectedResultNewLines = "Hallo, mein Name ist kai. \n"
        expectedResultMultiplePoints = "Hallo. So wird es weiter gehen. "
        expectedResultHtmlLink = "Hallo schau mal hier: "

        self.assertEqual(textRemoveNewLines, expectedResultNewLines)
        self.assertEqual(textRemoveMultiplePoints, expectedResultMultiplePoints)
        self.assertEqual(textRemoveHtmlLink, expectedResultHtmlLink)

if __name__ == '__main__':
    unittest.main()