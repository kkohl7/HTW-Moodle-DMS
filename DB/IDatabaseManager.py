import abc
from abc import ABCMeta

from Model.Model import MoodleCourse, Lecturer, LecturerHasCourse, CourseData, DateOfCrawling, User, LoginSuccess


class IDatabaseManager:
    """The IDatabaseManager is for the communication with the deposited database
       The functions are:
                - create all Tables for the model
                - check if a object is already stored in the database
                - insert object in the database
                - get objects from the database
                - delete objects from the database

    """
    __metaclass__ = ABCMeta

    @abc.abstractmethod
    def createTables(self):
        """The createTables function creates all tables from the model
        """

    @abc.abstractmethod
    def insertObject(self, object):
        """insertObject is for inserting a object from the model to the database and commit the insert.

        :param object: object from the model, which will be inserted.
                        """

    @abc.abstractmethod
    def doesCourseExist(self, moodleCourseName: str, moodleCourseSemester: str) -> bool:
        """doesCourseExist check if the MoodleCourse already exist in the database.

            :param moodleCourseName: The name of the moodle course.
            :param moodleCourseSemester:  The semester, when the moodle course is.
            :return True if a course with this name and semester is already in the database, False otherwise.
                                """

    @abc.abstractmethod
    def getCourse(self, moodleCourseName: str, moodleCourseSemester: str) -> MoodleCourse:
        """getCourse return die MoodleCourse, which has the given name and semester

            :param moodleCourseName: The name of the moodle course.
            :param moodleCourseSemester:  The semester, when the moodle course is.
            :return MoodleCourse if in the database is a course with the course name and
            the semester. Otherwise return None.
        """

    @abc.abstractmethod
    def doesLecturerExist(self, lecturername: str) -> bool:
        """doesLecturerExist check if a lecturer with this name already exist in the database.

            :param lecturername: The name of the lecturer.
            :return True if a lecturer with this name is already in the database, False otherwise.
                                """

    @abc.abstractmethod
    def getLecturer(self, lecturername: str) -> Lecturer:
        """getLecturer returns lecturer with the lecturername.

            :param lecturername: The name of the lecturer.
            :return Lecturer if in the database is a lecturer with the name. Otherwise return None.
        """

    @abc.abstractmethod
    def getAllLecturer(self) -> list:
        """getAllLecturer returns all lecturer from the database.

            :return Returns a list of all lecturers in the database.
        """

    @abc.abstractmethod
    def doesLecturerHasCourseExist(self, idLecturer: int, idCourse: int) -> bool:
        """doesLecturerHasCourseExist check if the lecturer already has the course in the database.

            :param idLecturer: The primary key from the lecturer
            :param idCourse: The primary key from the course
            :return True if the lecturer has the course in the database. False otherwise.
        """

    @abc.abstractmethod
    def getLecturerHasCourse(self, idLecturer: int, idCourse: int) -> LecturerHasCourse:
        """getLecturerHasCourse returns the lecturerHasCourse Object.

            :param idLecturer: The primary key from the lecturer
            :param idCourse: The primary key from the course
            :return  Returns LecturerHasCourse object, if the lecturer has the course. None otherwise.
        """

    @abc.abstractmethod
    def doesCourseDataExist(self, idCourse: int, link: str) -> bool:
        """doesCourseDataExist check if the data from the course already is stored in the database.

            :param idCourse: The primary key from the course
            :param link: The link, where the data is stored
            :return Returns True if the data is already stored. False otherwise.
        """

    @abc.abstractmethod
    def doesCourseDataExistWithPositionAndHeader(self, idCourse: int, link: str, pos: int, header: str) -> bool:
        """doesCourseDataExistWithPositionAndHeader check if the data is stored with the header and the position from
        the moodle page
        :param idCourse: The primary key from the course
        :param link: The link, where the data is stored
        :param pos: The position on the moodle page
        :param header: The header from the moodle section
        :return Returns True if the data is already stored with this information. False otherwise.
        """

    @abc.abstractmethod
    def UpdateCourseDataWithPositionAndHeader(self, courseData: CourseData):
        """UpdateCourseDataWithPositionAndHeader updates the fields position and header of the  given course data

           :param courseData: The course data which shall be updated
        """

    @abc.abstractmethod
    def UpdateCourseDataTextFields(self, courseData: CourseData):
        """
        UpdateCourseDataTextFields updates the columns FullText, Abstract, AbstractWordFrequency and Error for the given CourseData

        :param courseData: the course data, which shall be updated
        """

    @abc.abstractmethod
    def getCourseDataByID(self, idCourseData: int) -> CourseData:
        """getCourseDataByID get the course data by the id.

            :param idCourseData: The primary key from the data of the course
            :return Returns a CourseData object if the primary key is in the database. None otherwise.
        """

    @abc.abstractmethod
    def getCourseDataWithoutTextMiningForParsing(self, fileTypes: list) -> list:
        """getCourseDataWithoutTextMiningForParsing return a
            list of CourseData, which are not parsed and not have any failure in a past parsing process.

            :param fileTypes: list of strings types of files, which are for the parsing supported
            :return Returns a CourseData list with data, which is not parsed and had no failure in a past parsing process
        """

    @abc.abstractmethod
    def getMaxDateOfCrawling(self) -> DateOfCrawling:
        """getMaxDateOfCrawling return DateOfCrawling object from the last crawling process.

            :return getMaxDateOfCrawling: Returns a getMaxDateOfCrawling object with the newest timestamp.
        """

    @abc.abstractmethod
    def getCourseDataByText(self, searchString: str, filter: str) -> list:
        """getCourseDataByText return all information for CourseData, which satisfy the search string and the filter
        for course name, lecturer name or semester.

        :param searchString: words, which the user is searching
        :param filter: filter for the consider data (course name, lecturer name or semester).
        :return List of CourseDataWithInformation (course data and the metainformations), which are in the filter and have the search string in the content of the data.
        """

    @abc.abstractmethod
    def getCourseDataWithoutTextMining(self, filter: str) -> list:
        """getCourseDataWithoutTextMining return all information for course data, which satisfy the filter
        and had a problem in the text mining process.

                :param filter: filter for the consider data (course name, lecturer name or semester).
                :return List of CourseDataWithInformation (course data and the metainformations), which are in the filter
                and had a problem in the text mining process
                """

    @abc.abstractmethod
    def getUser(self) -> User:
        """getUser return the user from the database

            :return User: Return the user from the database. If there is no user return None.
                        """

    @abc.abstractmethod
    def deleteUsers(self):
        """deleteUsers delete all users from the database.
                        """

    @abc.abstractmethod
    def getGeneralCourseInformation(self) -> list:
        """getGeneralCourseInformation return all information for the courses.

            :return List of GeneralCourseInformation, like semester, course name and lecturer name.
                        """

    @abc.abstractmethod
    def getAllCourseData(self, filter: str) -> list:
        """getAllCourseData return all information for course data, which satisfy the filter.

                :param filter: filter for the consider data (course name, lecturer name or semester).
                :return List of CourseDataWithInformation (course data and the metainformation), which are in the filter
                """

    @abc.abstractmethod
    def loginSuccessfully(self) -> LoginSuccess:
        """loginSuccessfully check if the last login was successfully.

                :return: True if the last login was successfully, False otherwise
                """

    @abc.abstractmethod
    def deleteloginSuccess(self):
        """deleteloginSuccess delete all LoginSuccess from the database.
                        """

    @abc.abstractmethod
    def setCourseDataOnOld(self):
        """setCourseDataOnOld update CourseData Table and set all course data to old.
                """

    @abc.abstractmethod
    def deleteMoodleError(self):
        """deleteMoodleError delete all MoodleError from the database.
                        """

    @abc.abstractmethod
    def getMoodleErrorSummary(self) -> list:
        """getMoodleErrorSummary return all errors, which occured in the last crawling.

        :return: List of MoodleErrorSummary from the last crawling.
                        """

    @abc.abstractmethod
    def getMoodleSummary(self) -> list:
        """getMoodleSummary return a summary from the last crawling. How many new, old and error data per course are
        in the database.

        :return: List of MoodleSummary (count of new, old and error data per course).
        """
