import scrapy
from scrapy import Selector
from scrapy.crawler import CrawlerProcess
import re
import datetime

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from Model.Model import MoodleCourse, LecturerHasCourse, Lecturer, DateOfCrawling, LoginSuccess, \
    MoodleError, CourseData

from PyQt5 import QtWidgets

from MoodleCrawler.IMoodleCrawler import IMoodleCrawler


class MoodleCrawlerHTWBerlin(scrapy.Spider, IMoodleCrawler):

    def __init__(self, *args, **kwargs):

        self.name = 'Moodle-Crawler'
        if len(args) > 0:
            self.database = args[0]
            self.username = args[1]
            self.password = args[2]
            args = ()
        super(MoodleCrawlerHTWBerlin, self).__init__(*args, **kwargs)
        self.start_urls = [
            'https://moodle.htw-berlin.de/login/index.php']
        QtWidgets.QApplication.processEvents()

    def startCrawler(self, database, username, password):
        self.database = database
        self.username = username
        self.password = password
        process = CrawlerProcess()
        process.crawl(MoodleCrawlerHTWBerlin, self.database, self.username, self.password)
        process.start()

    def parse(self, response):
        """
        start to crawl the self.start_urls
        try to login to the moodle side
        If an error pop up go to function errback_httpbin, otherwise to after_login
        """
        self.logger.info('Starting Crawler and want to log in on: %s', response.url)
        self.database.deleteloginSuccess()
        self.database.deleteMoodleError()
        self.database.setCourseDataOnOld()
        QtWidgets.QApplication.processEvents()

        yield scrapy.FormRequest.from_response(
            response,
            formdata={'username': self.username, 'password': self.password},
            callback=self.after_login,
            errback=self.errback_httpbin
        )

    def after_login(self, response):
        """
        Search for all MoodleCourse of the user
        Check if the login was successfully:
            - not successfully -> write the information in the database and quit the crawler
            - successfully -> write the information in the database and start to search for courses
        """
        self.logger.info('Prüfung: Erfolgreicher Login? Link= %s ', response.url)
        QtWidgets.QApplication.processEvents()
        count_courses = 0

        # check login succeed before going on
        if b'Invalid login, please try again' in response.body:
            # login Failed
            self.logger.error("Login gescheitert")
            self.logger.error("Username oder Passwort sind falsch! Bitte ändern Sie diese")

            # write in the database, that the login failed
            loginSuccess = LoginSuccess(success=0)
            self.database.insertObject(loginSuccess)
            return 'Failed Login'

        # Login successfully
        self.logger.info('Login erfolgreich. Link= %s ', response.url)
        self.logger.info('Suche nach Moodlekursen Link= %s ', response.url)

        # write in the database, that the login was successfully
        loginSuccess = LoginSuccess(success=1)
        self.database.insertObject(loginSuccess)

        # Insert in the database the time of searching for Moodledata
        dateofcrawl = DateOfCrawling(dateCrawling=datetime.datetime.now())
        self.database.insertObject(dateofcrawl)

        # search on the Mainpage for all MoodleCourse
        for course in response.xpath('//div[@class="box coursebox"]'):
            # get for a course section all informations:
            # moodle-link of the course
            # meta-informations of the course
            # who is/are the lecturer of the course
            (moodle_link, moodleCourse, courseLecturer) = self.get_course_informations(course)
            count_courses += 1

            QtWidgets.QApplication.processEvents()

            self.logger.info('Gefunden %d. Kurs. Kursname: %s; Dozent: %s; Link: %s', count_courses
                             , moodleCourse.name
                             , courseLecturer[0].name
                             , moodle_link)

            # Does Course and Lecturer already exist in the database?
            moodleCourse = self.doesCourseAndLecturersAlreadyExist(moodleCourse, courseLecturer)

            QtWidgets.QApplication.processEvents()

            # follow the link of the MoodleCourse
            # use for the next side parse_course_site logic
            # hand over as metainformation the course and the course lecturers
            yield scrapy.Request(moodle_link, self.parse_course_site,
                                 meta={'moodleCourse': moodleCourse, 'courseLecturer': courseLecturer})
        self.logger.info("Sie haben %d Kurse insgesamt!", count_courses)
        QtWidgets.QApplication.processEvents()

    def parse_course_site(self, response):
        """
        Search for CourseData in the course side
        Check for every found data if it is already in the database:
            - if it is in the database:
                - update it, when informations changed, otherwise do nothing
            - if it is not in the database:
                - start to download the data
        """
        # take the metainformations from the previous function
        moodleCourse = response.meta['moodleCourse']
        courseLecturer = response.meta['courseLecturer']
        count_data = 0

        self.logger.info("Suche nach Daten im Kurs: %s; Dozent: %s; Link: %s", moodleCourse.name
                         , courseLecturer[0].name
                         , response.url)

        QtWidgets.QApplication.processEvents()

        # search in each section in the Moodlecourse for Moodledata
        for section in response.xpath('//li[@class="section main clearfix"]'):

            QtWidgets.QApplication.processEvents()

            # Get the header of the section
            moodleHeader = section.css('span::text').extract_first()

            # for each data in this section:
            # check if the data is already in the database
            # when not than download the data
            for data in section.css('div.activityinstance'):

                # get the type of the found element. It could be data, link, wiki, forum etc.
                type = data.css('span.accesshide ::text').extract_first()
                # take only these items from the section, which are data, folder or link
                if " Datei" == type or " Link/URL" == type or " Verzeichnis" == type:
                    # get the data link of this item
                    (courseData, count_data) = self.get_data_link(data, count_data, moodleCourse, courseLecturer,
                                                                  response, moodleHeader)

                    # if the coursedata is hidden => Inform the user about this and write an error to the database
                    if courseData.link == "Hidden Data":
                        # Hidden Content
                        self.logger.warning('Gefunden %d. Datei ist verborgen: %s; Dozent: %s; Link: %s; Abschnitt: %s',
                                            count_data, moodleCourse.name
                                            , courseLecturer[0].name
                                            , response.url
                                            , courseData.moodleHeader)
                        moodleError = MoodleError(error="Es wurde eine versteckte Datei gefunden", link=response.url, moodleCourse=moodleCourse)
                        self.database.insertObject(moodleError)
                        continue
                    # check if the Moodledata already exist in the database
                    if self.database.doesCourseDataExist(idCourse=moodleCourse.id, link=courseData.link):
                        # Moodeldata already exists
                        self.logger.info('Gefunden %d. Datei ist bereits in der Datenbank: %s; Dozent: %s; Link: %s',
                                         count_data
                                         , moodleCourse.name
                                         , courseLecturer[0].name
                                         , courseData.link)
                        if not self.database.doesCourseDataExistWithPositionAndHeader(idCourse=moodleCourse.id,
                                                                                      link=courseData.link,
                                                                                      pos=courseData.position,
                                                                                      header=courseData.moodleHeader):
                            self.database.UpdateCourseDataWithPositionAndHeader(courseData)
                    else:
                        if " Verzeichnis" == type:
                            yield scrapy.Request(courseData.link, self.parse_download_folder,
                                                 meta={'moodleCourse': moodleCourse, 'courseLecturer': courseLecturer,
                                                       'courseData': courseData, 'itemType': type},
                                                 errback=self.errback_httpbin)
                        else:
                            # CourseData does not exist in the database
                            self.logger.info('Gefunden %d. Datei: %s; Dozent: %s; Link: %s', count_data
                                             , moodleCourse.name
                                             , courseLecturer[0].name
                                             , courseData.link)
                            # Follow the link of the CourseData with the metainformation of the MoodleCourse,
                            # lecturer, all information about the CourseData and the type of the element
                            yield scrapy.Request(courseData.link, self.parse_download_data,
                                                 meta={'moodleCourse': moodleCourse, 'courseLecturer': courseLecturer,
                                                       'courseData': courseData, 'itemType': type},
                                                 errback=self.errback_httpbin)
        self.logger.info("Sie haben %d Dateien in dem Kurs: %s Dozent %s!", count_data
                         , moodleCourse.name
                         , courseLecturer[0].name)

    def parse_download_folder(self, response):
        """
        Get all informations from the folder, which is to download, after this go to parse_download_data
        """
        moodleCourse = response.meta['moodleCourse']
        courseData = response.meta['courseData']
        courseLecturer = response.meta['courseLecturer']
        type = response.meta['itemType']

        id = response.css('input[name="id"]::attr(value)').extract_first()
        sesskey = response.css('input[name="sesskey"]::attr(value)').extract_first()
        data = {'id': id,
                'sesskey': sesskey}

        link = response.css('form[method=post]::attr(action)').extract_first()

        if id is not None:
            yield scrapy.FormRequest(url=link, formdata=data, callback=self.parse_download_data,
                                     meta={'moodleCourse': moodleCourse, 'courseLecturer': courseLecturer,
                                           'courseData': courseData, 'itemType': type},
                                     errback=self.errback_httpbin
                                     )
        else:
            self.logger.warning('Verzeichnis hat keinen Inhalt: %s; Dozent: %s', courseData.link,
                                courseLecturer[0].name)

    def parse_download_data(self, response):
        """
        download the data from the resposne and write it to the database
        """
        # fill all metainformation
        moodleCourse = response.meta['moodleCourse']
        courseData = response.meta['courseData']
        courseLecturer = response.meta['courseLecturer']
        itemType = response.meta['itemType']

        # if the item type is a link to an other website
        # than set the name of the coursedata on the link and the datatype on html
        if itemType == ' Link/URL':
            courseData.name = response.url
            courseData.dataType = "html"
        # elif the datatype is a folder
        # than set the name on the moodleheader+position of the courseData and end with zip
        elif itemType == " Verzeichnis":
            courseData.name = courseData.moodleHeader + str(courseData.position) + ".zip"
            courseData.dataType = "zip"
        # else it is a normal file
        else:
            # set the data name on the part of the url behind the last "/"
            # it could be, that the link ends on "?forcedownload=1". This part has to replace with an empty String
            courseData.name = response.url.split('/')[-1].replace("?forcedownload=1", "")
            # the datatype is the coursedata name behind the last "."
            courseData.dataType = courseData.name.split('.')[-1].lower()

        # fill the content of the moodledata with the body of the response
        courseData.dataContent = response.body

        # insert the data in the database
        self.database.insertObject(courseData)
        self.logger.info('Speichern der Datei: %s ; Kurs: %s; Dozent: %s;    Link: %s',
                         courseData.name
                         , moodleCourse.name
                         , courseLecturer[0].name
                         , response.url)
        QtWidgets.QApplication.processEvents()

    def errback_httpbin(self, failure):
        """
        If an error pop up, while scraping, write the error to the database
        """
        # log all errback failures
        try:
            self.logger.error(repr(failure))
            if 'moodleCourse' in failure.request.meta:
                moodleCourse = failure.request.meta['moodleCourse']
            else:
                moodleCourse = None
            # if isinstance(failure.value, HttpError):
            if failure.check(HttpError):
                if hasattr(failure, 'request'):
                    if failure.request.url == 'https://moodle.htw-berlin.de/login/index.php':
                        # login Failed
                        self.logger.error("Login gescheitert")
                        self.logger.error("Username oder Passwort sind falsch! Bitte ändern Sie diese")

                        # write in the database, that the login failed
                        loginSuccess = LoginSuccess(success=0)
                        self.database.insertObject(loginSuccess)
                        return 'Failed Login'
                    else:
                        response = failure.value.response
                        error = 'HttpError ' + str(response.status) + ' on ' + response.url
                        errorLink = response.url
                        self.logger.error(error)

                # you can get the response
                else:
                    response = failure.value.response
                    error = 'HttpError ' + str(response.status) + ' on ' + response.url
                    errorLink = response.url
                    self.logger.error(error)

            # elif isinstance(failure.value, DNSLookupError):
            elif failure.check(DNSLookupError):
                # this is the original request
                request = failure.request
                error = 'DNSLookupError ' + ' on ' + request.url
                errorLink = request.url
                self.logger.error(error)

            # elif isinstance(failure.value, TimeoutError):
            elif failure.check(TimeoutError):
                request = failure.request
                error = 'TimeoutError ' + ' on ' + request.url
                errorLink = request.url
                self.logger.error(error)
            elif failure.check(TCPTimedOutError):
                request = failure.request
                error = 'TCPTimedOutError ' + ' on ' + request.url
                errorLink = request.url
                self.logger.error(error)
            else:
                request = failure.request
                error = 'Sonstiger Fehler' + ' on ' + request.url
                errorLink = request.url
                self.logger.error(error)
            if error:
                moodleError = MoodleError(error=error, link=errorLink, moodleCourse=moodleCourse)
                self.database.insertObject(moodleError)
            QtWidgets.QApplication.processEvents()
        except UnboundLocalError as e:
            pass

    # Functions for parsing informations from specific section or pages
    def get_course_informations(self, course: Selector) -> (str, MoodleCourse, list):
        """
        Extract from the selector the link to the MoodleCourse and all the lecturers for the course

        :param course: The Selector, which contains the course information
        :return: link to the moodle course side; the MoodleCourse; and a list of Lecturer, who are responsible for the course
        """
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

    def get_data_link(self, data: Selector, count_data: int, moodleCourse: MoodleCourse, courseLecturer: list, response, moodleHeader: str) -> (CourseData, int):
        """
        search in the data Selector for the data link and iterate the count_data with 1

        :param data: the selector, which contain the data link
        :param count_data: the position of the data in the course
        :param moodleCourse: the moodleCourse, which was found
        :param courseLecturer: the list of lecturer
        :param response:
        :param moodleHeader: the header of the moodle section
        :return: Return the CourseData with the link and the postion of the course data
        """
        # for one data can be stored 2 different links
        # one link can be in "onclick"
        # another one in "href" in "href" has to bee something
        # otherwise it is an hidden data for the user
        # "onclick" is to prefer, because this opens directly the CourseData
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
                raise Exception("Die %d. Datei hat keinen Link für den Download. Bitte prüfe den Kurs: %s; Dozent: "
                                "%s; Link: %s", count_data
                                , moodleCourse.name
                                , courseLecturer[0].name
                                , response.url)
            # if onclick does not exist => set the data link at the value of href
            data_link = data_link2
        count_data += 1
        courseData = CourseData(link=data_link, course=moodleCourse, moodleHeader=moodleHeader, position=count_data,
                                isNew=1)
        return courseData, count_data

    def doesCourseAndLecturersAlreadyExist(self, moodleCourse: MoodleCourse, courseLecturer: list) -> MoodleCourse:
        """
        Check if the moodleCourse and the Lecturer already exist in the database.
            - If they already exist do noting
            - if something do not exist; insert it into the database

        :param moodleCourse: the MoodleCourse which was found
        :param courseLecturer: the list of Lecturer who were found
        :return: the updated moodleCourse (with the new primary key)
        """
        # Does Course and Lecturer already exist in the database?
        if (
                self.database.doesCourseExist(moodleCourseName=moodleCourse.name,
                                              moodleCourseSemester=moodleCourse.semester)):
            # Moodlecourse does exist => Get all of the information from the database
            moodleCourse = self.database.getCourse(moodleCourseName=moodleCourse.name,
                                                   moodleCourseSemester=moodleCourse.semester)
        else:
            # Moodlecourse doesn*t exist => Insert into the database
            self.database.insertObject(moodleCourse)

        # check for each lecturer of a course, if he or she is already in the database
        # + check if the lecturer already has this course in the database
        for i in range(len(courseLecturer)):
            if self.database.doesLecturerExist(lecturername=courseLecturer[i].name):
                # lecturer does exist => Get all of his information
                courseLecturer[i] = self.database.getLecturer(lecturername=courseLecturer[i].name)
            else:
                # lecturer doesn't exist => Insert into the database
                self.database.insertObject(courseLecturer[i])

            # Does lecturer already has the course in the database?
            if (
                    not self.database.doesLecturerHasCourseExist(idLecturer=courseLecturer[i].id,
                                                                 idCourse=moodleCourse.id)):
                # the lectuer has not already this course in the database insert the connection to the database
                lecturerHasCourse = LecturerHasCourse(course=moodleCourse, lecturer=courseLecturer[i])
                self.database.insertObject(lecturerHasCourse)

        return moodleCourse
