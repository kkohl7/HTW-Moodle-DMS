import abc


class ICheckLanguage:
    """
    CheckLanguage is for the classification of a text in which language it is written
     """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def checkLanguage(self, text: str) -> str:
        """
        checkLanguage return the language of a text

            :param text: The text, which shall be classified
            :return Returns a string, which represent the language
            :raise ExceptionCheckLanguage if a problem pop up
        """