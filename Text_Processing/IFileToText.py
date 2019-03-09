import abc


class IFileToText:
    """
    FileToText is for read the text out of a file."
     """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def fileToText(self, filePath: str, datatype: str) -> str:
        """fileToText take the path to a file and the associated data type. Then it read the text from the file
        and return the text. If the datatype is not supported return an empty string.

        :param filePath: The path to the file
        :param datatype The data type of the file
        :return the text of the file, if the datatype is not supported the text is empty
        :raise ExceptionReadDataToText if an problem pop up
        """
