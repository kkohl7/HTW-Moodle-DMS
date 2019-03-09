from sqlalchemy import Column, Integer, String, ForeignKey, BLOB, TEXT, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
import datetime

Base = declarative_base()


class CourseData(Base):
    """
    CorrseData is a data from the moodle platform
    """
    __tablename__ = "CourseData"
    __table_args__ = (
        UniqueConstraint('Link', 'CourseID', name='unique_component_commit'),
    )
    id = Column('ID', Integer, primary_key=True)
    dataContent = Column('DataContent', BLOB, nullable=False)
    link = Column('Link', String(255), nullable=False)
    name = Column('Name', String(255), nullable=False)
    courseID = Column('CourseID', Integer, ForeignKey("MoodleCourse.ID"), nullable=False)
    dataType = Column('DataType', String(255), nullable=False)
    moodleHeader = Column('MoodleHeader', String(255))
    position = Column('Position', Integer, nullable=False)
    isNew = Column('IsNew', Integer, nullable=False)
    fullText = Column('FullText', TEXT)
    abstract = Column('Abstract', TEXT)
    abstractWordFrequency = Column('AbstractWordFrequency', TEXT)
    error = Column('Error', TEXT)

    course = relationship("MoodleCourse", foreign_keys=[courseID])


class MoodleCourse(Base):
    """
    MoodleCourse is a course from the moodle platform
    """
    __tablename__ = "MoodleCourse"
    __table_args__ = (
        UniqueConstraint('Name', 'Semester', name='unique_component_commit'),
    )
    id = Column('ID', Integer, primary_key=True)
    name = Column('Name', String(255), nullable=False)
    semester = Column('Semester', String(255))


class Lecturer(Base):
    """
    Lecturer is a lecturer from the moodle platform
    """
    __tablename__ = "Lecturer"
    id = Column('ID', Integer, primary_key=True)
    name = Column('Name', String(255), unique=True, nullable=False)


class LecturerHasCourse(Base):
    """
    LecturerHasCourse is the connection between MoodleCourse and Lecturer
    """
    __tablename__ = "LecturerHasCourse"
    __table_args__ = (
        UniqueConstraint('CourseID', 'LecturerID', name='unique_component_commit'),
    )
    id = Column('ID', Integer, primary_key=True)
    courseID = Column('CourseID', Integer, ForeignKey("MoodleCourse.ID"), nullable=False)
    lecturerID = Column('LecturerID', Integer, ForeignKey("Lecturer.ID"), nullable=False)

    course = relationship("MoodleCourse", foreign_keys=[courseID])
    lecturer = relationship("Lecturer", foreign_keys=[lecturerID])


class DateOfCrawling(Base):
    """
    DateOfCrawling saves when a moodledownload was done
    """
    __tablename__ = "DateOfCrawling"

    id = Column('ID', Integer, primary_key=True)
    dateCrawling = Column('DateCrawling', DateTime, default=datetime.datetime.utcnow, nullable=False)


class User(Base):
    """
    User is a user of the moodle platform
    """
    __tablename__ = "User"

    id = Column('ID', Integer, primary_key=True)
    username = Column('Username', TEXT, nullable=False)
    password = Column('Password', TEXT, nullable=False)


class ErrorData(Base):
    """
    ErrorData is a CourseData, which had a problem in the text processing
    """
    __tablename__ = "ErrorData"

    id = Column('ID', Integer, primary_key=True)
    courseDataID = Column('CourseDataID', Integer, ForeignKey("CourseData.ID"), nullable=False)
    error = Column('Error', TEXT, nullable=False)

    courseData = relationship("CourseData", foreign_keys=[courseDataID])


class LoginSuccess(Base):
    """
    LoginSucess stores the information if a login in a moodle download process was successfull.
    """
    __tablename__ = "LoginSuccess"

    id = Column('ID', Integer, primary_key=True)
    success = Column('Success', Integer, nullable=False)


class MoodleError(Base):
    """
    MoodleError save the links of pages which cant be downloaded in the moodle download process
    """
    __tablename__ = "MoodleError"

    id = Column('ID', Integer, primary_key=True)
    courseID = Column('CourseID', Integer, ForeignKey("MoodleCourse.ID"))
    error = Column('Error', TEXT, nullable=False)
    link = Column('Link', String(255), nullable=False)

    moodleCourse = relationship("MoodleCourse", foreign_keys=[courseID])


class GeneralCourseInformation:
    """
    GeneralCourseInformation contains the fields for the courses, which the user booked.
    In this class the coursename, lecturer and semester are stored.
    """

    def __init__(self, courseName, lecturer, semester):
        self.courseName = courseName
        self.lecturer = lecturer
        self.semester = semester

    @classmethod
    def getHeader(self):
        return ["Kursname", "Dozent", "Semester"]

    def getListForPrinting(self):
        return [self.courseName, self.lecturer, self.semester]


class CourseDataWithInformation:
    """
    CourseDataWithInformation contains the fields for the course data with
    all needed information from the coursename, lecturername etc.
    """

    def __init__(self, courseName, lecturer, semester, moodleHeader, position, dataName, dataType, moodleLink, dataID):
        self.courseName = courseName
        self.lecturer = lecturer
        self.semester = semester
        self.moodleHeader = moodleHeader
        self.position = position
        self.dataName = dataName
        self.dataType = dataType
        self.moodleLink = moodleLink
        self.dataID = dataID

    @classmethod
    def getHeader(self):
        return ["Kursname", "Dozent", "Semester", "Moodle Überschrift", "Position", "Dateiname", "Dateityp",
                "Moodlelink", "DataID"]

    def getListForPrinting(self):
        return [self.courseName, self.lecturer, self.semester, self.moodleHeader, self.position, self.dataName,
                self.dataType, self.moodleLink, self.dataID]


class MoodleSummary:
    """
    MoodleSummary contains the information for a course name how many new, old, and failure data exists.
    """

    def __init__(self, courseName, countNewData, countOldData, countErrorData):
        self.courseName = courseName
        self.countNewData = countNewData
        self.countOldData = countOldData
        self.countErrorData = countErrorData

    @classmethod
    def getHeader(self):
        return ["Kursname", "Anazahl neuer Daten", "Anzahl alter Daten", "Anzahl fehlerhafter Daten"]

    def getListForPrinting(self):
        return [self.courseName, self.countNewData, self.countOldData, self.countErrorData]


class MoodleErrorSummary:
    """
    MoodleErrorSummary contains the information for a course name which links could not be downloaded
    """

    def __init__(self, courseName, error, link):
        self.courseName = courseName
        self.error = error
        self.link = link

    @classmethod
    def getHeader(self):
        return ["Kursname", "Fehler", "Link"]

    def getListForPrinting(self):
        return [self.courseName, self.error, self.link]
