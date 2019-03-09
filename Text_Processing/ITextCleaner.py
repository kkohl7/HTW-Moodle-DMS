import abc


class ITextCleaner:
    """
    ITextCleaner is for the cleaning of texts.
     """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def cleaningText(self, text: str) -> str:
        """
        cleaningText return the text in a clean version. No links, multiple lines etc.

            :param text: The text, which shall be cleaned
            :return Returns a string, which is cleaned
        """