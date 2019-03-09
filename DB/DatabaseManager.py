from sqlalchemy import create_engine, update, delete, desc, inspect
from sqlalchemy.orm import sessionmaker

from DB.IDatabaseManager import IDatabaseManager
from Model.Model import Base, CourseData, MoodleCourse, LecturerHasCourse, Lecturer, \
    DateOfCrawling, User, LoginSuccess, MoodleError, GeneralCourseInformation, CourseDataWithInformation, MoodleSummary, \
    MoodleErrorSummary
import os


class DatabaseManager(IDatabaseManager):
    """Attributes:
            - databasePath (str): The path, where the database will/is stored
            - engine (engine): The engine of the database
            - Sesseion (sessionmaker): For binding the engine for sessions in the future
            - session (Session): A session for transactional communication

    """

    def __init__(self):
        """The init function does:
                - create or load the database in the databasePath
                - set the engine from the database
                - makes a session for the database
            """
        self.databasePath = (os.path.dirname(os.path.abspath(__file__)) + '/Moodle.db').replace('\\', '/')
        self.engine = create_engine('sqlite:///' + self.databasePath, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def createTables(self):
        tables = inspect(self.engine).get_table_names()
        if tables is None or len(tables) == 0:
            Base.metadata.create_all(bind=self.engine)

    def insertObject(self, object):
        self.session.add(object)
        self.session.commit()

    def doesCourseExist(self, moodleCourseName, moodleCourseSemester):
        return (self.session.query(MoodleCourse).filter(MoodleCourse.name == moodleCourseName).filter(
            MoodleCourse.semester == moodleCourseSemester).first() is not None)

    def getCourse(self, moodleCourseName, moodleCourseSemester):
        return (self.session.query(MoodleCourse).filter(
            MoodleCourse.name == moodleCourseName and MoodleCourse.semester == moodleCourseSemester).first())

    def doesLecturerExist(self, lecturername):
        return self.session.query(Lecturer).filter(Lecturer.name == lecturername).first() is not None

    def getLecturer(self, lecturername):
        return self.session.query(Lecturer).filter(Lecturer.name == lecturername).first()

    def getAllLecturer(self):
        result = self.session.query(Lecturer)
        return [r for r in result]

    def doesLecturerHasCourseExist(self, idLecturer, idCourse):
        return (self.session.query(LecturerHasCourse).filter(LecturerHasCourse.courseID == idCourse).filter(
            LecturerHasCourse.lecturerID == idLecturer).first() is not None)

    def getLecturerHasCourse(self, idLecturer, idCourse):
        return (self.session.query(LecturerHasCourse).filter(
            LecturerHasCourse.courseID == idCourse).filter(LecturerHasCourse.lecturerID == idLecturer).first())

    # CourseData statements:
    def doesCourseDataExist(self, idCourse, link):
        return (self.session.query(CourseData).filter(
            CourseData.courseID == idCourse).
                filter(CourseData.link == link).
                first() is not None)

    def doesCourseDataExistWithPositionAndHeader(self, idCourse, link, pos, header):
        return (self.session.query(CourseData).filter(
            CourseData.courseID == idCourse).
                filter(CourseData.link == link).
                filter(CourseData.position == pos).
                filter(CourseData.moodleHeader == header).
                first() is not None)

    def UpdateCourseDataWithPositionAndHeader(self, courseData):
        data = {'position': courseData.position, 'moodleHeader': courseData.moodleHeader}
        self.session.query(CourseData).filter(CourseData.courseID == courseData.course.id).filter(
            CourseData.link == courseData.link).update(data)
        self.session.commit()

    def UpdateCourseDataTextFields(self, courseData):
        data = {'fullText': courseData.fullText, 'abstract': courseData.abstract,
                'abstractWordFrequency': courseData.abstractWordFrequency, 'error': courseData.error}
        self.session.query(CourseData).filter(CourseData.id == courseData.id).update(data)
        self.session.commit()

    def getCourseDataByID(self, idCourseData):
        return (self.session.query(CourseData).filter(
            CourseData.id == idCourseData).first())

    def getCourseDataWithoutTextMiningForParsing(self, fileTypes):
        result = self.session.query(CourseData) \
            .filter(CourseData.dataType.in_(fileTypes)) \
            .filter(CourseData.fullText == None) \
            .filter(CourseData.error == None)
        return [r for r in result]

    def getMaxDateOfCrawling(self):
        return self.session.query(DateOfCrawling).order_by(desc(DateOfCrawling.dateCrawling)).first()

    def getCourseDataByText(self, searchString, filter):
        searchString = "'%" + searchString.lower().replace(' ', '%') + "%'"
        if len(filter) == 0:
            filterString = ""
        else:
            filterString = """AND (mc.Name = %s
                                    OR l.Name = %s
                                    OR mc.semester = %s)""".replace("%s", "'" + filter + "'")
        result = self.engine.execute("""SELECT mc.Name Kursname,
                                                            l.Name Dozent,
                                                            mc.semester,
                                                            cd.MoodleHeader MoodleUeberschrift,
                                                            cd.position,
                                                            cd.Name Dateiname,
                                                            cd.DataType DateiTyp,
                                                            cd.link Moodlelink,
                                                            cd.id dataID
                                                   FROM MoodleCourse mc, Lecturer l
                                                   INNER JOIN LecturerHasCourse lhc ON lhc.CourseID = mc.ID AND lhc.LecturerID = l.ID
                                                   INNER JOIN CourseData cd ON cd.CourseID = mc.ID
                                                   WHERE fullText LIKE %WHERE1 
                                                    %WHERE2
                                                   ORDER BY cd.position
                                                   """.replace("%WHERE1", searchString).replace("%WHERE2",
                                                                                                filterString))
        result2 = []
        for item in result:
            result2.append(CourseDataWithInformation(courseName=item._row[0], lecturer=item._row[1], semester=item._row[2],
                                                     moodleHeader=item._row[3], position=item._row[4],
                                                     dataName=item._row[5], dataType=item._row[6], moodleLink=item._row[7],
                                                     dataID=item._row[8]))
        return result2

    def getCourseDataWithoutTextMining(self, filter):
        if len(filter) == 0:
            filterString = ""
        else:
            filterString = """and (mc.Name = %s
                                    OR l.Name = %s
                                    OR mc.semester = %s)""".replace("%s", "'" + filter + "'")
        result = self.engine.execute("""SELECT mc.Name Kursname,
                                                 l.Name Dozent,
                                                 mc.semester,
                                                 cd.MoodleHeader MoodleUeberschrift,
                                                 cd.position,
                                                 cd.Name Dateiname,
                                                 cd.DataType DateiTyp,
                                                 cd.link Moodlelink,
                                                 cd.id dataID
                                        FROM MoodleCourse mc, Lecturer l
                                        INNER JOIN LecturerHasCourse lhc ON lhc.CourseID = mc.ID AND lhc.LecturerID = l.ID
                                        INNER JOIN CourseData cd ON cd.CourseID = mc.ID
                                        WHERE cd.Error is not NULL 
                                        """ + filterString + " ORDER BY cd.position")
        result2 = []
        for item in result:
            result2.append(CourseDataWithInformation(courseName=item._row[0], lecturer=item._row[1], semester=item._row[2], moodleHeader=item._row[3], position=item._row[4], dataName=item._row[5], dataType=item._row[6], moodleLink=item._row[7], dataID=item._row[8]))
        return result2

    def getUser(self):
        return self.session.query(User).first()

    def deleteUsers(self):
        users = self.session.query(User)
        users.delete()
        self.session.commit()

    def getGeneralCourseInformation(self):
        result = self.engine.execute("""SELECT mc.Name Kursname, l.Name Dozent, semester
                                        FROM MoodleCourse mc, Lecturer l
                                        INNER JOIN LecturerHasCourse lhc ON lhc.CourseID = mc.ID AND lhc.LecturerID = l.ID
                                        """)
        result2 = []
        for row in result:
            result2.append(GeneralCourseInformation(courseName=row._row[0], lecturer=row._row[1], semester=row._row[2]))
        return result2

    def getAllCourseData(self, filter):
        filter = """WHERE (mc.Name = %s
                        OR l.Name = %s
                        OR mc.semester = %s)""".replace("%s", "'" + filter + "'")
        result = self.engine.execute("""SELECT mc.Name Kursname,
                                                 l.Name Dozent,
                                                 mc.semester,
                                                 cd.MoodleHeader MoodleUeberschrift,
                                                 cd.position,
                                                 cd.Name Dateiname,
                                                 cd.DataType DateiTyp,
                                                 cd.link Moodlelink,
                                                 cd.id dataID
                                        FROM MoodleCourse mc, Lecturer l
                                        INNER JOIN LecturerHasCourse lhc ON lhc.CourseID = mc.ID AND lhc.LecturerID = l.ID
                                        INNER JOIN CourseData cd ON cd.CourseID = mc.ID
                                        %WHERE
                                        ORDER BY cd.position
                                        """.replace('%WHERE', filter))
        result2 = []
        for item in result:
            result2.append(CourseDataWithInformation(courseName=item._row[0], lecturer=item._row[1], semester=item._row[2], moodleHeader=item._row[3], position=item._row[4], dataName=item._row[5], dataType=item._row[6], moodleLink=item._row[7], dataID=item._row[8]))
        return result2

    def loginSuccessfully(self):
        success = self.session.query(LoginSuccess).first()
        if success is None:
            return
        else:
            return success.success == 1

    def deleteloginSuccess(self):
        success = self.session.query(LoginSuccess)
        success.delete()
        self.session.commit()

    def setCourseDataOnOld(self):
        update_statement = update(CourseData).where(CourseData.isNew == 1).values(IsNew=0)
        self.session.execute(update_statement)
        self.session.commit()

    def deleteMoodleError(self):
        delete_statement = delete(MoodleError)
        self.session.execute(delete_statement)
        self.session.commit()

    def getMoodleErrorSummary(self):
        result = self.engine.execute("""
            SELECT mc.name, me.Error, me.Link
            FROM MoodleError me
            INNER JOIN MoodleCourse mc ON me.CourseID = mc.id 
        """)

        result2 = []
        for item in result:
            result2.append(MoodleErrorSummary(courseName=item._row[0], error=item._row[1], link=item._row[2]))
        return result2

    def getMoodleSummary(self):
        result = self.engine.execute("""
        WITH Anzahl_Fehler_Kurs as (
            SELECT me.CourseID
                , COUNT(*) AnzahlFehler
            FROM MoodleError me
            GROUP BY me.CourseID
            )
            ,
            Anzahl_Moodle_Daten as (
            SELECT mc.name, mc.id
                , COUNT(CASE WHEN cd.IsNew = 1 THEN 1 END) NeueDaten
                , COUNT(CASE WHEN cd.IsNew = 0 THEN 1 END) AlteDaten
            FROM CourseData cd
            INNER JOIN MoodleCourse mc ON cd.CourseID = mc.ID
            GROUP BY mc.name, mc.id
            )
            SELECT amd.Name
                , amd.NeueDaten
                , amd.AlteDaten
                , CASE WHEN afk.AnzahlFehler IS NULL THEN 0 ELSE afk.AnzahlFehler END AnzahlFeher
            FROM Anzahl_Moodle_Daten amd
            LEFT JOIN Anzahl_Fehler_Kurs afk ON amd.ID = afk.CourseID
            UNION ALL
            SELECT 'Unbekannt' as Name
                    , 0 NeueDaten
                    , 0 AlteDaten
                    , AnzahlFehler
            FROM Anzahl_Fehler_Kurs afk
            WHERE afk.CourseID IS NULL
                                                """)
        result2 = []
        for item in result:
            result2.append(MoodleSummary(courseName=item._row[0], countNewData=item._row[1], countOldData=item._row[2], countErrorData=item._row[3]))
        return result2