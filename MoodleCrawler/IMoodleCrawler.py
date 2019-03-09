import abc

from DB import IDatabaseManager


class IMoodleCrawler:
    """
    IMoodleCrawler is for downloading all CourseData for a user, with the information of
    the course, lecturer, semester etc. and write these information to the database
     """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def startCrawler(self, database: IDatabaseManager, username: str, password: str):
        """
        Start the Download from the Moodlepage

            :param database: The communication tool with the database
            :param username: The name of the user in moodle
            :param password: The password from the user in moodle
        """
        pass