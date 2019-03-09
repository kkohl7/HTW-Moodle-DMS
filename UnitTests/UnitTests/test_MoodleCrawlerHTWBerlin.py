import datetime
import logging
import os
import re

from unittest.mock import Mock

import scrapy
from scrapy.crawler import CrawlerProcess

from scrapy.http import Request
import unittest

from DB.DatabaseManager import DatabaseManager
from Model.Model import LoginSuccess, DateOfCrawling, MoodleCourse, Lecturer, LecturerHasCourse, CourseData, MoodleError


class test_MoodleCrawlerHTWBerlin(unittest.TestCase):

    def test_find_all_courses_and_lecturers_and_alle_files_from_file_from_htmlfile(self):
        """
        check if the after_login function, which is for the searching process of the moodle courses, find all courses
        in the saved html page.
        check if the parse_course_site function, which is for the searching process of the CourseData in a moodle course, find all data
        in the saved html page.
        """
        class SpiderFindAllCourses(scrapy.Spider):
            logging.disable(logging.WARNING)
            name = 'example'
            pathTestFiles = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + "/TestFiles/"
            url = 'file:///' + pathTestFiles + 'SucessfullyLogin2.html'

            def start_requests(self):
                self.database = Mock(spec=DatabaseManager)
                self.database.doesCourseExist.side_effect = [True, False]
                self.database.doesLecturerExist.side_effect = [True, False, False, False]
                self.database.doesLecturerHasCourseExist.side_effect = [True, False, False, False]

                self.courseName1 = "M1.2 Management von IV-Projekten (SL) Z1 SoSe2016"
                self.courseSemester1 = "SoSe2016"
                self.lecturerName1 = 'Norman F'

                self.courseName2 = 'M1.4 Stochastik und Induktive Statistik (PCÜ) Z1G1, Z1G2 WiSe2016'
                self.courseSemester2 = 'WiSe2016'
                self.lecturerName2 = 'Michael H'
                self.lecturerName3 = 'Martin S'
                self.lecturerName4 = 'Thomas U'

                self.database.getCourse.return_value = MoodleCourse(id=1, name=self.courseName1, semester=self.courseSemester1)
                self.database.getLecturer.return_value = Lecturer(id=1, name=self.lecturerName1)
                yield Request(self.url, self.after_login)


            def after_login(self, response):
                self.logger.info('Prüfung: Erfolgreicher Login? Link= %s ', response.url)
                count_courses = 0
                # check login succeed before going on
                if b'Invalid login, please try again' in response.body:
                    # login Failed
                    self.logger.error("Login gescheitert")
                    self.logger.error("Username oder Passwort sind falsch! Bitte ändern Sie diese")

                    # write in the mock_database, that the login failed
                    loginSuccess = LoginSuccess(success=0)
                    self.database.insertObject(loginSuccess)
                    return 'Failed Login'

                # Login successfully
                self.logger.info('Login erfolgreich. Link= %s ', response.url)
                self.logger.info('Suche nach Moodlekursen Link= %s ', response.url)

                # write in the mock_database, that the login was successfully
                loginSuccess = LoginSuccess(success=1)
                self.database.insertObject(loginSuccess)

                # Insert in the mock_database the time of searching for Moodledata
                dateofcrawl = DateOfCrawling(dateCrawling=datetime.datetime.now())
                self.database.insertObject(dateofcrawl)

                # search on the Mainpage for all Moodlecourses
                for course in response.xpath('//div[@class="box coursebox"]'):
                    # get for a course section all informations:
                    # moodle-link of the course
                    # meta-informations of the course
                    # who is/are the lecturer of the course
                    (moodle_link, moodleCourse, courseLecturer) = self.get_course_informations(course)
                    count_courses += 1


                    self.logger.info('Gefunden %d. Kurs. Kursname: %s; Dozent: %s; Link: %s', count_courses
                                     , moodleCourse.name
                                     , courseLecturer[0].name
                                     , moodle_link)

                    # Does Course and Lecturer already exist in the mock_database?
                    moodleCourse = self.doesCourseAndLecturersAlreadyExist(moodleCourse, courseLecturer)

                self.logger.info("Sie haben %d Kurse insgesamt!", count_courses)
                assert count_courses == 2
                self.check_mocking()

            def get_course_informations(self, course):
                regex_semester = r'(WiSe\d+|SoSe\d+)'
                course_information = course.xpath('h3')

                # get the name and the semester of the Moodlecourse
                name = course_information.xpath('a/@title').extract_first()
                semester = re.findall(regex_semester, name)

                # if there is no semester information
                # set the semester on an empty String
                if not semester:
                    semester = ""
                else:
                    semester = semester[0]
                moodleCourse = MoodleCourse(name=name, semester=semester)

                # get the link of the Moodlecourse
                moodle_link = course_information.xpath('a/@href').extract_first()

                # get all lecturers of the course
                # the lecturers start behind the character "|"
                course_lecturers = course_information.css('span.coc-metainfo::text').extract_first()
                # [-1 because the last character is a ")"]
                course_lecturers = course_lecturers[re.search(r"\|", course_lecturers).end() + 1:-1]

                # the lecturer are separated with an ","
                list_course_lecturers = re.split(',', course_lecturers)

                courseLecturers = []
                for course_lecturer in list_course_lecturers:
                    courseLecturers.append(Lecturer(name=re.sub(r'^ +', '', course_lecturer)))
                return moodle_link, moodleCourse, courseLecturers

            def doesCourseAndLecturersAlreadyExist(self, moodleCourse: MoodleCourse, courseLecturer: list):
                # Does Course and Lecturer already exist in the mock_database?
                if (
                        self.database.doesCourseExist(moodleCourseName=moodleCourse.name,
                                                      moodleCourseSemester=moodleCourse.semester)):
                    # Moodlecourse does exist => Get all of the information from the mock_database
                    moodleCourse = self.database.getCourse(moodleCourseName=moodleCourse.name,
                                                           moodleCourseSemester=moodleCourse.semester)
                else:
                    # Moodlecourse doesn*t exist => Insert into the mock_database
                    self.database.insertObject(moodleCourse)

                # check for each lecturer of a course, if he or she is already in the mock_database
                # + check if the lecturer already has this course in the mock_database
                for i in range(len(courseLecturer)):
                    if self.database.doesLecturerExist(lecturername=courseLecturer[i].name):
                        # lecturer does exist => Get all of his informations.
                        courseLecturer[i] = self.database.getLecturer(lecturername=courseLecturer[i].name)
                    else:
                        # lecturer doesn't exist => Insert into the mock_database
                        self.database.insertObject(courseLecturer[i])

                    # Does lecturer already has the course in the mock_database?
                    if (
                            not self.database.doesLecturerHasCourseExist(idLecturer=courseLecturer[i].id,
                                                                         idCourse=moodleCourse.id)):
                        # the lectuer has not already this course in the mock_database
                        lecturerHasCourse = LecturerHasCourse(course=moodleCourse, lecturer=courseLecturer[i])
                        self.database.insertObject(lecturerHasCourse)
                return moodleCourse

            def check_mocking(self):
                # check if doesCourseExist was called with the right values
                assert self.database.doesCourseExist.call_count == 2
                list_course_names = [self.courseName1, self.courseName2]
                list_course_semester = [self.courseSemester1, self.courseSemester2]
                for mock_call in self.database.doesCourseExist.mock_calls:
                    call_dict = mock_call[2]
                    assert call_dict.get('moodleCourseName') in list_course_names
                    list_course_names.remove(call_dict.get('moodleCourseName'))
                    assert call_dict.get('moodleCourseSemester') in list_course_semester
                    list_course_semester.remove(call_dict.get('moodleCourseSemester'))
                    assert not 'Other Value' in call_dict.values()
                assert len(list_course_names) == 0
                assert len(list_course_semester) == 0
                # 9 calls of insertObject
                #   = 1 call LoginSuccess
                #   + 1 call dateOfCrawl
                #   + 1 call insert courseData of "Stockastik"
                #   + 3 call insert Lecturer of Lecturers from the course Stochastik
                #   + 3 call insert LecturerHasCourse from Stockastik
                assert self.database.insertObject.call_count == 9
                #   4 lecturers were found
                assert self.database.doesLecturerExist.call_count == 4
                list_of_lecturer = [self.lecturerName1, self.lecturerName2, self.lecturerName3, self.lecturerName4]
                for mock_call in self.database.doesLecturerExist.mock_calls:
                    call_dict = mock_call[2]
                    assert call_dict.get('lecturername') in list_of_lecturer
                    list_of_lecturer.remove(call_dict.get('lecturername'))
                    assert not 'Other Value' in call_dict.values()
                assert len(list_of_lecturer) == 0
                #   4 does lecturer has course exist
                assert self.database.doesLecturerHasCourseExist.call_count == 4

        class SpiderParseCoursSide(scrapy.Spider):
            logging.disable(logging.WARNING)
            name = 'example'

            pathTestFiles = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + "/TestFiles/"
            url = 'file:///' + pathTestFiles + 'CourseWebside.html'

            def start_requests(self):
                self.database = Mock(spec=DatabaseManager)
                self.database.doesCourseDataExist.side_effect = [False, True, True, False]
                self.database.doesCourseDataExistWithPositionAndHeader.side_effect = [True, False]
                self.moodleCourse = MoodleCourse(id=1, name="Stochastik", semester="WiSe2016")
                self.lecturer = [Lecturer(id=1, name="Kai K"), Lecturer(id=2,name='John D')]
                yield Request(self.url, self.parse_course_site, meta={'moodleCourse': self.moodleCourse, 'courseLecturer': self.lecturer})

            def parse_course_site(self, response):
                # take the metainformations from the previous function
                moodleCourse = response.meta['moodleCourse']
                courseLecturer = response.meta['courseLecturer']
                count_data = 0

                self.logger.info("Suche nach Daten im Kurs: %s; Dozent: %s; Link: %s", moodleCourse.name
                                 , courseLecturer[0].name
                                 , response.url)


                # search in each section in the Moodlecourse for Moodledata
                for section in response.xpath('//li[@class="section main clearfix"]'):


                    # Get the header of the section
                    moodleHeader = section.css('span::text').extract_first()

                    # for each data in this section:
                    # check if the data is already in the mock_database
                    # when not than download the data
                    for data in section.css('div.activityinstance'):

                        # get the type of the Moodledata. It could be data, link, wiki, forum etc.
                        type = data.css('span.accesshide ::text').extract_first()
                        # take only this items from the section, which are data or links
                        if " Datei" == type or " Link/URL" == type or " Verzeichnis" == type:
                            # get the data link of this item
                            # and store the information of the moodlecourse
                            # and the position in the moodlecourse in the coursedata item
                            # Furthermore iterate count_data with 1

                            (courseData, count_data) = self.get_data_link(data, count_data, moodleCourse,
                                                                          courseLecturer,
                                                                          response, moodleHeader)

                            # if the coursedata is hidden => Inform the user about this
                            if courseData.link == "Hidden Data":
                                # Hidden Content
                                self.logger.warning(
                                    'Gefunden %d. Datei ist verborgen: %s; Dozent: %s; Link: %s; Abschnitt: %s',
                                    count_data, moodleCourse.name
                                    , courseLecturer[0].name
                                    , response.url
                                    , courseData.moodleHeader)
                                moodleError = MoodleError(error="Es ist eine versteckte Datei gefunden wurden",
                                                          link=response.url, moodleCourse=moodleCourse)
                                self.database.insertObject(moodleError)
                                continue
                            # check if the Moodledata already exist in the mock_database
                            if self.database.doesCourseDataExist(idCourse=moodleCourse.id, link=courseData.link):
                                # Moodeldata already exists
                                self.logger.info(
                                    'Gefunden %d. Datei ist bereits in der Datenbank: %s; Dozent: %s; Link: %s',
                                    count_data
                                    , moodleCourse.name
                                    , courseLecturer[0].name
                                    , courseData.link)
                                if not self.database.doesCourseDataExistWithPositionAndHeader(idCourse=moodleCourse.id,
                                                                                              link=courseData.link,
                                                                                              pos=courseData.position,
                                                                                              header=courseData.moodleHeader):
                                    self.database.UpdateCourseDataWithPositionAndHeader(courseData)
                                    pass
                            else:
                                if " Verzeichnis" == type:
                                    pass
                                else:
                                    # Moodledata does not exist in the database
                                    self.logger.info('Gefunden %d. Datei: %s; Dozent: %s; Link: %s', count_data
                                                     , moodleCourse.name
                                                     , courseLecturer[0].name
                                                     , courseData.link)
                                    # Follow the link of the Moodledata with the metainformation of the Moodlecourse,
                                    # course lecturer, all information about the coursedata and the type of the section

                self.logger.info("Sie haben %d Dateien in dem Kurs: %s Dozent %s!", count_data
                                 , moodleCourse.name
                                 , courseLecturer[0].name)
                assert count_data == 5
                self.check_mocking()

            def get_data_link(self, data, count_data, moodleCourse, courseLecturer,
                              response, moodleHeader):
                data_link = data.xpath('a/@onclick').extract_first()
                data_link2 = data.xpath('a/@href').extract_first()

                if data_link is None:
                    data_link = ""
                if data_link2 is None:
                    data_link2 = "Hidden Data"
                # replace in the data link every call function for the browser
                data_link = data_link.replace("window.open(", "")
                data_link = data_link.replace("); return false;", "")
                data_link = data_link.replace("'", "")

                # check if at least one link contains characters
                if len(data_link) == 0:
                    if len(data_link2) == 0:
                        raise Exception(
                            "Die %d. Datei hat keinen Link für den Download. Bitte prüfe den Kurs: %s; Dozent: "
                            "%s; Link: %s", count_data
                            , moodleCourse.name
                            , courseLecturer[0].name
                            , response.url)
                    # if onclick does not exist => set the data link at the value of href
                    data_link = data_link2
                count_data += 1
                courseData = CourseData(link=data_link, course=moodleCourse, moodleHeader=moodleHeader,
                                        position=count_data,
                                        isNew=1)
                return courseData, count_data

            def check_mocking(self):
                assert self.database.insertObject.call_count == 1
                insertObject = self.database.insertObject.mock_calls[0][1][0]
                assert insertObject.error == 'Es ist eine versteckte Datei gefunden wurden'
                assert insertObject.moodleCourse == self.moodleCourse

                # checked if four course data are in the database
                assert self.database.doesCourseDataExist.call_count == 4
                list_of_links = ['https://moodle.htw-berlin.de/mod/resource/view.php?id=356188&redirect=1', 'https://moodle.htw-berlin.de/mod/resource/view.php?id=356186&redirect=1', 'https://moodle.htw-berlin.de/mod/url/view.php?id=355957&redirect=1', 'https://moodle.htw-berlin.de/mod/folder/view.php?id=270861']
                for mock_call in self.database.doesCourseDataExist.mock_calls:
                    call_dict = mock_call[2]
                    assert call_dict.get('idCourse') == self.moodleCourse.id
                    assert call_dict.get('link') in list_of_links
                    list_of_links.remove(call_dict.get('link'))
                    assert not 'Other Value' in call_dict.values()
                assert len(list_of_links) == 0

                # check database does course data exist with position and header
                assert self.database.doesCourseDataExistWithPositionAndHeader.call_count == 2
                list_of_links = ['https://moodle.htw-berlin.de/mod/resource/view.php?id=356186&redirect=1',
                                 'https://moodle.htw-berlin.de/mod/url/view.php?id=355957&redirect=1']
                for mock_call in self.database.doesCourseDataExistWithPositionAndHeader.mock_calls:
                    call_dict = mock_call[2]
                    assert call_dict.get('idCourse') == self.moodleCourse.id
                    assert call_dict.get('link') in list_of_links
                    list_of_links.remove(call_dict.get('link'))
                    assert not 'Other Value' in call_dict.values()
                assert len(list_of_links) == 0
                pass

        process = CrawlerProcess()
        process.crawl(SpiderFindAllCourses)
        process.crawl(SpiderParseCoursSide)
        process.start()

if __name__ == '__main__':
    unittest.main()
