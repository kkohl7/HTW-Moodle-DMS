import sys

from PyQt5.QtCore import Qt
import logging

from FileHandler.FileHandler import FileHandler as FileHandler
from GUI.TextEditLogger import QTextEditLogger
from Model.Model import User, GeneralCourseInformation, CourseDataWithInformation, MoodleSummary, MoodleErrorSummary
from MoodleCrawler.MoodleCrawlerHTWBerlin import MoodleCrawlerHTWBerlin

from Text_Processing.TextAbstraction import TextAbstraction as TextAbstraction
from Text_Processing.TextProcessing import TextProcessing as TextProcessing

from PyQt5.QtWidgets import *

from PyQt5.QtGui import QStandardItem, QStandardItemModel, QTextCursor
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets

from DB.DatabaseManager import DatabaseManager as DatabaseManager


class Controller(object):
    """
    The Controller class is for loading the specific guis from the GUI folder.
    It also implements and fill the required GUI with logic.
    """

    def __init__(self, path: str):
        # the actual path
        self.actualPath = path
        # A IDatabaseManager to communicate with the database
        self.database = DatabaseManager()
        # Tries to create the required tables
        self.database.createTables()

        # The path to the different GUIs
        self.pathMainGui = self.actualPath + '/GUI' + '/MainGui.ui'
        self.pathStartDownload = self.actualPath + '/GUI' + '/StartDownload.ui'
        self.pathCurrentDownload = self.actualPath + '/GUI' + '/CurrentDownload.ui'
        self.pathSettings = self.actualPath + '/GUI' + '/Settings.ui'
        self.pathError = self.actualPath + '/GUI' + '/ErrorMessage.ui'
        self.pathHelp = self.actualPath + '/GUI' + '/Help.ui'
        self.pathMoodleSummary = self.actualPath + '/GUI' + '/MoodleSummary.ui'

        # path to the folder, where temporary files shall be stored
        self.pathTempFolder = self.actualPath + '/temp/'

        app = QtWidgets.QApplication(sys.argv)

        # the main and error window
        self.MainWindow = None
        self.ErrorWindow = None
        # courseData, which was selected from the user
        self.selectedCourseData = None
        # The filter (lecturer name, semester, course name) which is selected
        self.selectedFilter = None
        # The model of the courseData which is selected
        self.modelCourseData = None
        # Will set on True, when the moodle download was started, because
        #    scrapy can only run one time per program run
        self.startedMoodleCrawler = False

        # The IFileHandler to handle the CourseData
        self.fileHandler = FileHandler()
        # The used ITextAbstraction
        self.textSummarizer = TextAbstraction(database=self.database)

        user = self.database.getUser()
        # check if the program has already a user
        if user is None:
            # no user in the database
            # go to settings
            self.openSettings()
        else:
            # go to main page
            self.goBackMainPage()
        sys.exit(app.exec_())

    # Guis
    # Open MainPage
    def goBackMainPage(self):
        """
        goBackMainPage will start the MainPage and will connect everything with
        the required functions and print the required information to the gui.
        """
        # close and clean up the old Main Window
        self.cleanMainWindow()

        # Load and show the new Main Window
        self.MainWindow = loadUi(self.pathMainGui)
        self.MainWindow.showMaximized()
        self.MainWindow.show()

        # disable that the user can edit the entries from table for general course information
        self.MainWindow.tab_courses.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.MainWindow.tab_courses.setSortingEnabled(True)
        # Fill the table for the general course information with data
        self.printGeneralCourseInformation()
        # if some data from the general course information is clicked, show all data for this filter
        # in tab_data
        self.MainWindow.tab_courses.clicked.connect(self.selectGeneralCourseInformation)

        # disable that the user can edit the entries from table for course data
        self.MainWindow.tab_data.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.MainWindow.tab_data.setSortingEnabled(True)
        # if an cell was selected in table for course data, mark the whole row
        self.MainWindow.tab_data.setSelectionBehavior(QAbstractItemView.SelectRows)
        # if some data from the CourseData is clicked, load the summary to the field text_Abstract
        self.MainWindow.tab_data.clicked.connect(self.selectCourseData)

        # Connect the Buttons with functionality

        # open Window for checking, if it is necessary to download moodle-data
        self.MainWindow.but_downloadMoodle.clicked.connect(self.openWindowStartDownload)
        # open Window for storing username and password
        self.MainWindow.but_settings.clicked.connect(self.openSettings)
        # open Window for help
        self.MainWindow.but_help.clicked.connect(self.openHelp)
        # open Window for get the summary from the last moodle download
        self.MainWindow.but_moodleSummary.clicked.connect(
            lambda: self.openMoodleSummary(destination="Main Page"))

        # search functions
        self.MainWindow.but_searchAll.clicked.connect(
            lambda: self.searchData(filter="All"))
        self.MainWindow.but_searchCell.clicked.connect(
            lambda: self.searchData(filter="Cell"))
        # show Text without Text-Mining
        self.MainWindow.but_withoutTextMiningAll.clicked.connect(
            lambda: self.showDataWithoutTextMining(filter="All"))
        self.MainWindow.but_withoutTextMiningCell.clicked.connect(
            lambda: self.showDataWithoutTextMining(filter="Cell"))

        # open Data
        self.MainWindow.but_openData.clicked.connect(self.openData)
        self.MainWindow.but_openAllData.clicked.connect(self.openAllData)

        # save Data
        self.MainWindow.but_saveData.clicked.connect(self.saveData)
        self.MainWindow.but_saveAllData.clicked.connect(self.saveAllData)

        # close program
        self.MainWindow.but_close.clicked.connect(self.quitProgram)

    # StartDownloadPage
    def openWindowStartDownload(self):
        """
        open the gui to ask the user, if he really wants to download the moodle data.
        It will connect everything with the required functions and print the required information to the gui.
        """
        self.cleanMainWindow()
        self.MainWindow = loadUi(self.pathStartDownload)

        # Check if the Crawler was executed, because you can´t start again a Crawler
        if (self.startedMoodleCrawler):
            # Crawler was executed
            # deactivate the Button for starting the Crawler
            self.MainWindow.but_startDownload.setEnabled(False)
            # inform the user that he can not start again the crawler
            self.MainWindow.label_info.setText("""<html><head/><body><p align="center">Achtung:</p><p align="center">Es ist nur möglich einen Moodledownload pro </p><p align="center">Programmstart auszuführen.</p><p align="center">Falls Sie erneut den Download starten wollen, starten Sie das Porgramm neu!<br/></p></body></html>""")
        else:
            # Crawler was not executed

            # get the las date of Crawling
            lastDateOfCrawling = self.database.getMaxDateOfCrawling()
            if lastDateOfCrawling is None:
                # inform the user, that he never start a download process from moodle
                self.MainWindow.label_info.setText(
                    self.MainWindow.label_info.text().replace('%String', 'Sie haben noch keinen Download gestartet!'))
            else:
                # inform the user, when his last download was
                self.MainWindow.label_info.setText(
                    self.MainWindow.label_info.text().replace('%String', lastDateOfCrawling.dateCrawling.strftime(
                        "%H:%M:%S %d.%m.%Y ")))
        self.MainWindow.show()

        # connect button to go back to Main Page
        self.MainWindow.but_abortDownload.clicked.connect(self.goBackMainPage)
        # connect button to start moodle download
        self.MainWindow.but_startDownload.clicked.connect(self.openCurrentDownload)

    def openCurrentDownload(self):
        """
        Will open the current download gui and connect the scrapy logger to the gui.
        It start also the Crawler, if the user stored all required information.
        """
        self.cleanMainWindow()
        self.MainWindow = loadUi(self.pathCurrentDownload)
        self.MainWindow.showMaximized()

        # Activate logger to textbox
        logTextBox = QTextEditLogger(self.MainWindow)
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.INFO)

        # disable button done until the crawler finished
        self.MainWindow.but_done.setEnabled(False)
        # the log output is only readable
        self.MainWindow.plainTextEdit.setReadOnly(True)
        self.MainWindow.show()

        # get the moodle user
        user = self.database.getUser()

        # Check if a user is in the database or none of his attributes is null
        if (user is None or not user.username or not user.password):
            logTextBox.deactivate()
            self.goBackMainPage()
            self.errorMessage(e="""Sie haben noch keinen Nutzer angelegt. \n
                                Bitte legen Sie bei \"Einstellungen\" auf dem Startbildschirm, einen Nutzer an!""")

        else:
            # the user has all attributes
            # start the moodle crawler
            crawler = MoodleCrawlerHTWBerlin()
            crawler.startCrawler(self.database, user.username, user.password)

            # set the information, that the crawler was started on true
            self.startedMoodleCrawler = True

            # move the cursor to the end of the text field
            self.MainWindow.plainTextEdit.moveCursor(QTextCursor.End)
            logTextBox.deactivate()
            # check if the login was sucessfully
            if not self.database.loginSuccessfully():
                self.errorMessage(e="""
                Das Passwort oder der Nutzername sind falsch. \n
                Bitte ändern Sie bei \"Einstellungen\" auf dem Startbildschirm den Nutzer!""")
                self.MainWindow.but_done.setEnabled(True)
                self.MainWindow.but_done.clicked.connect(self.goBackMainPage)
            else:
                # login was a success
                self.MainWindow.but_done.setEnabled(True)
                self.MainWindow.but_done.clicked.connect(
                    lambda: self.openMoodleSummary(destination="Text Process"))

    def openMoodleSummary(self, destination: str="Main Page"):
        """
        Open the GUI for the getMoodleSummary. And print all informations to the gui. This GUI is
        for informing the user about what data per course is new, old  and could not be downloaded.
        Also every specific error in the download process will be shown.

        :param destination: Which GUI shall load after this gui.
        """
        self.cleanMainWindow()
        self.MainWindow = loadUi(self.pathMoodleSummary)

        # Fill the moodle data summary with data
        modelMoodleSummaryData = QStandardItemModel()
        self.MainWindow.tab_numberOfData.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.MainWindow.tab_numberOfData.setSortingEnabled(True)
        self.MainWindow.tab_numberOfData.setModel(modelMoodleSummaryData)
        # get the summary from the database
        moodleSummaryData = self.database.getMoodleSummary()
        # get the header from the table
        header = MoodleSummary.getHeader()

        modelMoodleSummaryData.setHorizontalHeaderLabels(header)
        for moodleSummaryItem in moodleSummaryData:
            listOfValues = moodleSummaryItem.getListForPrinting()
            row = []
            for value in listOfValues:
                cell = QStandardItem()
                cell.setData(value, Qt.DisplayRole)
                row.append(cell)
            modelMoodleSummaryData.appendRow(row)

        # Fill the moodle error data summary with data
        modelMoodleError = QStandardItemModel()
        self.MainWindow.tab_errorData.setModel(modelMoodleError)
        self.MainWindow.tab_errorData.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.MainWindow.tab_errorData.setSortingEnabled(True)
        # get the error summary from the database
        moodleErrorData = self.database.getMoodleErrorSummary()
        # get the header from the table
        header = MoodleErrorSummary.getHeader()

        modelMoodleError.setHorizontalHeaderLabels(header)
        for moodleErrorItem in moodleErrorData:
            listOfValues = moodleErrorItem.getListForPrinting()
            row = []
            for value in listOfValues:
                cell = QStandardItem()
                cell.setData(value, Qt.DisplayRole)
                row.append(cell)
            modelMoodleError.appendRow(row)

        self.MainWindow.showMaximized()
        self.MainWindow.show()

        if destination == "Main Page":
            self.MainWindow.but_back.setText("Zurück zur Hauptseite")
            self.MainWindow.but_back.clicked.connect(self.goBackMainPage)
        elif destination == "Text Process":
            self.MainWindow.but_back.clicked.connect(self.openTextProcessing)

    def openSettings(self):
        """
        open the GUI for settings. It is for saving the user information password
        and username from moodle.
        """
        self.cleanMainWindow()
        self.MainWindow = loadUi(self.pathSettings)
        self.MainWindow.show()

        # get the user from the database
        user = self.database.getUser()

        # set passwordline on password, that the password is not readable for the user
        self.MainWindow.linePassword.setEchoMode(QLineEdit.Password)

        # check if in the database is an user
        if user is not None:
            # in the database is an user
            # fill the text fields with his information
            self.MainWindow.lineUsername.setText(user.username)
            self.MainWindow.linePassword.setText(user.password)
        else:
            self.MainWindow.lineUsername.setPlaceholderText('s0111111')
            self.MainWindow.linePassword.setPlaceholderText('Hier dein Passwort')
        # go back to main page, without saving
        self.MainWindow.but_abortSettings.clicked.connect(self.goBackMainPage)
        # go back to main page, with saving
        self.MainWindow.but_save.clicked.connect(self.saveSettings)

    def openHelp(self):
        """ open the help GUI. This is for helping the user to work with the application
        """
        self.cleanMainWindow()
        self.MainWindow = loadUi(self.pathHelp)
        self.MainWindow.showMaximized()
        self.MainWindow.show()

        # the user can not edit the help text
        self.MainWindow.helpText.setReadOnly(True)

        # go back to main page
        self.MainWindow.but_back.clicked.connect(self.goBackMainPage)

    # open textProcessing Page
    def openTextProcessing(self):
        """
        open the GUI CurrentDownload and start the text processing. Also it connects the logger
        to the edit line. This Gui informs the user about which CourseData will be textually
        processed.
        """
        self.cleanMainWindow()
        self.MainWindow = loadUi(self.pathCurrentDownload)
        self.MainWindow.showMaximized()

        # Activate logger to textbox
        logTextBox = QTextEditLogger(self.MainWindow)
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.INFO)

        # disable button until the text process is finished
        self.MainWindow.but_done.setEnabled(False)
        self.MainWindow.plainTextEdit.setReadOnly(True)
        self.MainWindow.show()

        # create the text mining logic
        textProcessing = TextProcessing(database=self.database, path=self.pathTempFolder,
                                        textSummarizer=self.textSummarizer)
        # get the CourseData from the database, which do not have a text abstraction and not raised an error in a past process
        fileTypes = [
            'pdf'
            , 'docx'
            , 'pptx'
            , 'html'
        ]
        dataWithoutTextMining = self.database.getCourseDataWithoutTextMiningForParsing(fileTypes)

        # i is the position of the course data in the list
        i = 1
        countDataWithoutTextMining = len(dataWithoutTextMining)
        self.MainWindow.plainTextEdit.appendPlainText(
            "Es sind insgesamt %d Dateien textuell aufzuarbeiten!".replace("%d", str(countDataWithoutTextMining)))
        # start for each data the text mining process
        for data in dataWithoutTextMining:
            self.MainWindow.plainTextEdit.appendPlainText(
                "Beginn mit der %d1. Datei von %d2!".replace("%d1", str(i)).replace("%d2",
                                                                                    str(countDataWithoutTextMining)))
            textProcessing.textProcessing(data)
            self.MainWindow.plainTextEdit.appendPlainText(
                "Fertig mit der %d1. Datei von %d2!".replace("%d1", str(i)).replace("%d2",
                                                                                    str(countDataWithoutTextMining)))
            i += 1
            QtWidgets.QApplication.processEvents()

        # enable the button for finish this
        self.MainWindow.but_done.setEnabled(True)

        # deactivate the logger
        logTextBox.deactivate()
        # go back to main page
        self.MainWindow.but_done.clicked.connect(self.goBackMainPage)

    def saveSettings(self):
        """
        It tries to save the informations from the settings to the database.
        If every field is filled save the information to the database and go back to the
        main page.
        Otherwise print an error message and do nothing.
        """
        # read the arguments of the user
        username = self.MainWindow.lineUsername.text()
        password = self.MainWindow.linePassword.text()
        if username == "" or password == "":
            self.errorMessage(e="""Der Nuzername oder das Passwort sind leer.
            Bitte füllen Sie die Felder aus!""")
        else:
            user = User(username=username,
                        password=password)
            # delete the current user from the database
            self.database.deleteUsers()
            # insert the new user
            self.database.insertObject(user)
            # go back to main page
            self.goBackMainPage()

    def quitProgram(self):
        """
        Tries to delete every file in the temp folder. Only the files, which are not any more
        in use will be deleted.
        After this quit the program.
        """
        self.fileHandler.deleteAllFilesInFolder(self.pathTempFolder)
        sys.exit()

    def printGeneralCourseInformation(self):
        """
        print the generalCourseInformation to the table tab_courses
        """
        self.modelGeneralCourseInformation = QStandardItemModel()
        self.MainWindow.tab_courses.setModel(self.modelGeneralCourseInformation)

        courses = self.database.getGeneralCourseInformation()

        header = GeneralCourseInformation.getHeader()

        self.modelGeneralCourseInformation.setHorizontalHeaderLabels(header)
        # fill the table with the information
        for course in courses:
            listOfValues = course.getListForPrinting()
            row = []
            for value in listOfValues:
                cell = QStandardItem()
                cell.setData(value, Qt.DisplayRole)
                row.append(cell)
            self.modelGeneralCourseInformation.appendRow(row)

    def printCourseData(self, table=""):
        """
        print all CourseData from the table to the table tab_data.

        :param table: the table which shall be printed
        """
        self.modelCourseData = QStandardItemModel()
        self.MainWindow.tab_data.setModel(self.modelCourseData)
        header = CourseDataWithInformation.getHeader()

        self.modelCourseData.setHorizontalHeaderLabels(header)
        for course in table:
            listOfValues = course.getListForPrinting()
            row = []
            for value in listOfValues:
                cell = QStandardItem()
                cell.setData(value, Qt.DisplayRole)
                row.append(cell)
            self.modelCourseData.appendRow(row)

    def searchData(self, filter: str):
        """
        search for data if filter is all search for all data for search string otherwise for the selected filter
        after this print the searched data to table tab_data

        :param filter: filter = "All" if all data shall be searched; filter = "Cell" if only for the specific
        selected filter data shall be searched
        """
        searchString = self.MainWindow.line_search.text()
        table = None
        if filter == 'All':
            table = self.database.getCourseDataByText(searchString=searchString, filter="")
        elif filter == 'Cell':
            if self.selectedFilter:
                table = self.database.getCourseDataByText(searchString=searchString, filter=self.selectedFilter)
            else:
                self.errorMessage(e="""Sie haben keine Zelle ausgewählt. \n Bitte drücken Sie in der linken Tabelle 
                auf Ihren gewünschten Suchbegriff""")
        if table:
            self.printCourseData(table)

    def showDataWithoutTextMining(self, filter: str):
        """
        Search for data without text mining and print them to the table tab_data.

        :param filter: filter = "All" if all data without text-mining shall be searched; filter = "Cell" if only for the specific
        selected filter data without text-mining shall be searched
        """
        table = None
        if filter == 'All':
            table = self.database.getCourseDataWithoutTextMining(filter="")
        elif filter == 'Cell':
            if self.selectedFilter:
                table = self.database.getCourseDataWithoutTextMining(filter=self.selectedFilter)
            else:
                self.errorMessage(e="""Sie haben keine Zelle ausgewählt. \n
                                                            Bitte drücken Sie in der linken Tabelle auf Ihren gewünschten Suchbegriff""")
        if table:
            self.printCourseData(table)


    def openData(self):
        """
        open the the selected CourseData
        if None is selected inform the user that he has to select a CourseData in the table
        """
        if self.selectedCourseData is not None:
            self.fileHandler.openFile(courseData=self.selectedCourseData, path=self.pathTempFolder)
        else:
            self.errorMessage(e="""Sie haben keine Datei ausgewählt. \n
                                                        Bitte drücken Sie in der mittleren Tabelle auf Ihren gewünschte Datei.""")

    def openAllData(self):
        """
        open all Data which are in the tab_data(modle = modelCourseData) printed
        If no data is printed inform the user that he has to search for CourseData to open a data
        """
        if self.modelCourseData is not None:
            courseDataID_list = []
            self.modelCourseData.columnCount()
            for y in range(self.modelCourseData.columnCount()):
                header = self.modelCourseData.horizontalHeaderItem(y).text()
                if header == "DataID":
                    column = y
                    continue
            for x in range(self.modelCourseData.rowCount()):
                index = self.modelCourseData.index(x, column)
                courseDataID_list.append(self.modelCourseData.itemData(index).get(0))
            for courseDataId in courseDataID_list:
                courseData = self.database.getCourseDataByID(int(courseDataId))
                self.fileHandler.openFile(courseData=courseData, path=self.pathTempFolder)
        else:
            self.errorMessage(e="""Sie haben keine Dateien gesucht, die Sie auswählen können. \n
                                                        Bitte drücken Sie in der linken Tabelle auf Ihren gewünschten Suchbegriff, um die zugehörigen Dateien anzuzeigen.""")

    def selectGeneralCourseInformation(self, signal):
        """
        Set the selectedFilter on the selected Value, which the user selected.
        And print all Data for the specific filter to the tab_data
        """
        cell_dict = self.modelGeneralCourseInformation.itemData(signal)
        self.selectedFilter = cell_dict.get(0)

        result = self.database.getAllCourseData(filter=self.selectedFilter)
        self.printCourseData(table=result)

    def errorMessage(self, e: str):
        """
        open the error Gui and print the error message

        :param e: the error message
        """
        if self.ErrorWindow is not None:
            self.ErrorWindow.close()
        self.ErrorWindow = loadUi(self.pathError)
        self.ErrorWindow.label_info.setText(self.ErrorWindow.label_info.text().replace('%String', str(e)))
        self.ErrorWindow.but_ok.clicked.connect(self.ErrorWindow.close)
        self.ErrorWindow.show()

    def saveData(self):
        """
        save the selected data to a folder, which the user select.
        if None is selected inform the user that he has to select a CourseData in the table
        """
        if self.selectedCourseData is not None:
            saveFolder = QFileDialog.getExistingDirectory(self.MainWindow, "Select Directory")
            saveFolder += '/'
            if len(saveFolder) > 0:
                self.fileHandler.saveFile(courseData=self.selectedCourseData, path=saveFolder)
        else:
            self.errorMessage(e="""Sie haben keine Datei ausgewählt. \n
                                                        Bitte drücken Sie in der mittleren Tabelle auf Ihren gewünschte Datei.""")

    def saveAllData(self):
        """
        save all CourseData which are printed in the tab_data(modle = modelCourseData)
        If no data is printed inform the user that he has to search for CourseData to open a data
        """
        if self.modelCourseData is not None:
            saveFolder = str(QFileDialog.getExistingDirectory(self.MainWindow, "Select Directory"))
            if len(saveFolder) > 0:
                saveFolder += '/'
                courseDataID_list = []
                self.modelCourseData.columnCount()
                for y in range(self.modelCourseData.columnCount()):
                    header = self.modelCourseData.horizontalHeaderItem(y).text()
                    if header == "DataID":
                        column = y
                        continue
                for row in range(self.modelCourseData.rowCount()):
                    index = self.modelCourseData.index(row, column)
                    courseDataID_list.append(self.modelCourseData.itemData(index).get(0))
                for courseDataId in courseDataID_list:
                    courseData = self.database.getCourseDataByID(int(courseDataId))
                    self.fileHandler.saveFile(courseData=courseData, path=saveFolder)
        else:
            self.errorMessage(e="""Sie haben keine Dateien gesucht, die Sie auswählen können. \n
                                                                        Bitte drücken Sie in der linken Tabelle auf Ihren gewünschten Suchbegriff, um die zugehörigen Dateien anzuzeigen.""")

    def selectCourseData(self, signal):
        """
        set the  selectedCourseData on the data which was selected.
        Print the abstract, the frequency of words and the errors from the data to the text field "text_Abstract"
        """
        row = signal.row()
        for y in range(self.modelCourseData.columnCount()):
            header = self.modelCourseData.horizontalHeaderItem(y).text()
            if header == "DataID":
                column = y
                break

        index = self.modelCourseData.index(row, column)
        courseDataID = self.modelCourseData.itemData(index).get(0)
        self.selectedCourseData = self.database.getCourseDataByID(idCourseData=courseDataID)

        self.MainWindow.text_Abstract.clear()

        if self.selectedCourseData.abstract is not None:
            self.MainWindow.text_Abstract.appendPlainText(
                self.selectedCourseData.abstract
            )
        if self.selectedCourseData.abstractWordFrequency is not None:
            self.MainWindow.text_Abstract.appendPlainText(
                self.selectedCourseData.abstractWordFrequency
            )
        if self.selectedCourseData.error is not None:
            self.MainWindow.text_Abstract.appendPlainText(
                self.selectedCourseData.error
            )
        self.MainWindow.text_Abstract.setReadOnly(True)

    def cleanMainWindow(self):
        """
        reset all fields
        """
        if self.MainWindow is not None:
            self.selectedCourseData = None
            self.selectedFilter = None
            self.modelCourseData = None


if __name__ == "__main__":
    import os
    path = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    c = Controller(path=path)
