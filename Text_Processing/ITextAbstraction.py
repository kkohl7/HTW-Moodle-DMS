import abc
from abc import ABCMeta


class ITextAbstraction:
    """
         The TextAbstraction is for the summarization of texts.
           The functions are:
            - summarize_Text for summarize a text
            - frequency_Words returns the occurs of words in text
    """
    __metaclass__ = ABCMeta

    @abc.abstractmethod
    def summarize_Text(self, text: str, n: int, language: str) -> str:
        """
        summarize_Text return a text with n main sentences of the input text.

        :param text: The text, which shall be summarized
        :param n: Number of sentences, which shall be used
        :param language: The language of the text
        :return Return the abstract text
        :raise ExceptionTextAbstraction: When n < number of sentences in text
        """

    @abc.abstractmethod
    def frequency_Words(self, text: str, n: int, language: str) -> str:
        """
        frequency_Words compute the frequency of each word in text and give the n words with the highest pop up back
        as a string.

        :param text: The text for which the n highest words shall be extract
        :param n: number of words which shall be extract
        :param language: The language of the text
        :return: Returns a String, where each row contains the word and how often it occurs
        :raise: ExceptionTextAbstraction: When n < number of words in text
        """
