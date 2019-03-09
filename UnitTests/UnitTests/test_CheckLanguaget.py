import unittest
from Text_Processing.CheckLanguage import CheckLanguage


class TestCheckLanguage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.germanText = "Hallo. Mein Name ist Kai und das ist ein deutscher Text."
        cls.englishText = "Hi. My name is Kai and this is an english text."
        cls.frenchText = "Bonjour. Je m appelle Kai et c'est un francais texte."
        cls.specialCharacterText = "♥\f\i\n♀É♠重いフルーティーな\c幸せ非常に強力な頭石のバースト"
        cls.checkLanguage = CheckLanguage()

    def test_checkLanguage_Sucess(self):
        """
        Test if the checkLanguage function classifies german and english texts correct and others uncertain
        Procedure:
            1. Call the classifier with german, english and other language text
            ---------
            Verification:
            2. germanLanguage = germanExpectedLanguage
            3. englishLanguage = englishExpectedLanguage
            4. uncertainLanguage = uncertainExpectedLanguage
        """
        germanLanguage = self.checkLanguage.checkLanguage(self.germanText)
        englishLanguage = self.checkLanguage.checkLanguage(self.englishText)
        uncertainLanguage = self.checkLanguage.checkLanguage(self.frenchText)

        self.assertEqual(germanLanguage, 'german')
        self.assertEqual(englishLanguage, 'english')
        self.assertEqual(uncertainLanguage, 'uncertain')


if __name__ == '__main__':
    unittest.main()