import abc
from abc import ABCMeta

from Model.Model import CourseData


class IFileHandler:
    """
    FileHandler is responsible for the saving and opening of the courseData. It also delete specific files or all files
    from a folder.
    """
    __metaclass__ = ABCMeta

    @abc.abstractmethod
    def openFile(self, courseData: CourseData, path: str):
        """
        openFile open the CourseData, that the user can see the file and can work with
        the file

        :param courseData: The CourseData which shall be open
        :param path: The path where the file shall be stored
        """

    @abc.abstractmethod
    def saveFile(self, courseData: CourseData, path: str) -> str:
        """
        saveFile save the CourseData to the path

        :param courseData: The CourseData which shall be saved
        :param path: The path where the file shall be stored
        :return path: The updated path with the name of the file (str)
        """

    @abc.abstractmethod
    def deleteFile(self, path: str):
        """
        deleteFile tries to delete the file behind the path. If the file is still in use, the function does nothing.

        :param path: The path where the file is stored
        """

    @abc.abstractmethod
    def deleteAllFilesInFolder(self, path: str):
        """
        deleteAllFilesInFolder tries to delete all files behind the path. If a file is still in use, the function does
        nothing to this file.

        :param path: The path where the file is stored
        """