from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

from Exceptions.OwnExceptions import ExceptionCheckLanguage
from Text_Processing.ICheckLanguage import ICheckLanguage


class CheckLanguage(ICheckLanguage):

    def checkLanguage(self, text):
        """
            TODO The problem is, that nltk needs the language as a full word, like *german'. The used framework would return "de" so every language has to be translate in the whole word
        """
        try:
            # detect the language of the text
            language = detect(text)
            # if language de then 'german'
            if(language == 'de'):
                language = 'german'
            # if language en then 'english'
            elif(language == 'en'):
                language = 'english'
            # else the language is uncertain
            else:
                language = 'uncertain'
            return language
        except LangDetectException:
            raise(ExceptionCheckLanguage('Die ausgelesene Datei besteht vermutlich nur aus Sonderzeichen und '
                                         'Steuerungszeichen.'))
