import logging
from multiprocessing import Pool, TimeoutError

from PyQt5 import QtWidgets

from DB import IDatabaseManager

from Exceptions.OwnExceptions import ExceptionReadDataToText, ExceptionCheckLanguage, ExceptionTextAbstraction
from FileHandler.FileHandler import FileHandler
from Model.Model import CourseData
from Text_Processing import ITextAbstraction
from Text_Processing.FileToText import FileToText

from Text_Processing.TextCleaner import TextCleaner
from Text_Processing.CheckLanguage import CheckLanguage


class TextProcessing:
    """
       TextProcessing is the control logic for the text processing of the CourseData.
         The functions are:
                  - Textprocessing the logic of the process
          Attributes:
              - database (IDatabaseManager): The Connection to the database
              - tempPath (str): The path where the coursedata shall be stored temporary
              - fileHandler (IFileHandler) to save courseData to the device
              - fileToText (IFileToText) to read the text from a file
              - textSummarizer (ITextAbstraction) to summarize the text
              - textCleaner (ITextCleaner) for cleaning the text
              - checkLanguage (ICheckLanguage) to get the language of the text
              - timeout (int): The limit of time a file has to be read out
              - error (str): The message of an error, which pop up
      """
    def __init__(self, database: IDatabaseManager, path: str, textSummarizer: ITextAbstraction, fileToText=FileToText(), checkLanguage=CheckLanguage(), fileHandler=FileHandler(), textCleaner=TextCleaner(), timeout: int=60):
        """The timeout is by default 60 seconds"""
        # the database connection to update the CourseData
        self.database = database
        # the fileHandler to write the courseData temporary to a device
        self.fileHandler = fileHandler
        # the path where the files shall be temporary stored
        self.tempPath = path
        # fileToText a IFileToText to read the text from a file
        self.fileToText = fileToText
        # the ITextAbstraction for the summarization of the text from a file
        self.textSummarizer = textSummarizer
        # a ITextCleaner for cleaning the text
        self.textCleaner = textCleaner
        # timeout when the read text from file process shall be get quit
        self.timeout = timeout
        # The ICheckLanguage to get the language from a text
        self.checkLanguage = checkLanguage
        # The error text, for which problem pop up
        self.error = ""

    def textProcessing(self, courseData: CourseData):
        """
        textProcessing the control logic of the processing. The logic will try to read out the text from the
        CourseData and try to summarize the text in the main sentences and the words main words.

        :param courseData: The CourseData which shall be processed
        """
        self.error = ""
        # update the View, because the function runs is in the same process like
        # the GUI
        QtWidgets.QApplication.processEvents()
        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

        logging.info("Beginn der Textaufbereitung Datei: %s", courseData.name)
        # save the CourseData to the tempPath and get the dataLocation back
        dataLocation = self.fileHandler.saveFile(courseData, self.tempPath)

        # read the text from the file
        text = self._readTextFromFile(courseData, dataLocation)
        # update the View, because the function runs is in the same process like
        # the GUI
        QtWidgets.QApplication.processEvents()

        # If a text was return
        if len(text) > 0:
            # set the full text of the CourseData to the read text
            courseData.fullText = text

            # clean the read text
            cleanText = self.textCleaner.cleaningText(text)
            # summarize the clean text
            courseData = self._summarizeText(courseData, cleanText)

        # If no text was return
        else:
            # if no error pop up, write an error
            if self.error == "":
                self.error = "Die Datei besteht wahrscheinlich nur aus Bildern. Es gibt keinen Text"
        # if in the process pop up an error
        # set the attribute error of the CourseData to the poped up error
        if len(self.error) > 0:
            courseData.error = self.error
        # update the CourseData in the database
        self.database.UpdateCourseDataTextFields(courseData)
        # remove the temporary file
        self.fileHandler.deleteFile(dataLocation)


    def _readTextFromFile(self, courseData: CourseData, dataLocation: str) -> str:
        """
        readTextFromFile tries to read the text out of a courseData.

        :param courseData The CourseData which shall be read out
        :param dataLocation:  The location where the CourseData is stored on device
        :return: text from the file. An empty file if the read out process pop up an error
        """
        try:
            logging.info("Datei %s zu Text: %s", courseData.dataType, courseData.name)
            QtWidgets.QApplication.processEvents()
            # create a subprocess, because the read process can get in
            # an infinite loop. The subprocess will be killed after self.timeout
            pool = Pool(processes=1)
            # start the subprocess
            res2 = pool.apply_async(func=self.fileToText.fileToText, args=(dataLocation, courseData.dataType))
            # try to get the result of the subprocess
            # kill the subprocesss after timeout
            text = res2.get(timeout=self.timeout)
        except TimeoutError:
            logging.warning("Die Datei: %s braucht zu lange. Der Aufbereitungsprozess wird für diese Datei abgebrochen",
                            courseData.name)
            text = ""
            self.error = "Datei braucht zu lange zum parsen."
            pool.terminate()
        except ExceptionReadDataToText as e:
            logging.warning(
                "Die Datei: %s %s",
                courseData.name, str(e))
            text = ""
            self.error = str(e)
        finally:
            # finally close the subprocess
            pool.close()

        try:
            # try to decode the text in utf-8
            text = text.decode('utf-8')
        except:
            # otherwise text keeps normal
            text = text
        return text

    def _summarizeText(self, courseData: CourseData, cleanText: str) -> CourseData:
        """
        summarizeText summarize the cleanText from the courseData

        :param courseData: The data which shall get an abstract
        :param cleanText: The clean text from the data
        :return: The updated CourseData object. The fileds which will be updated are abstract
        and the abstractWordFrequency.
        """
        try:
            # check the language of the clean text
            language = self.checkLanguage.checkLanguage(cleanText)
            # if the language is not uncertain
            if (language != 'uncertain'):
                logging.info("Versuch der Textzusammenfassung der Datei %s", courseData.name)
                # calculate the abstract
                courseData.abstract = self.textSummarizer.summarize_Text(cleanText, 5, language=language)
                # calculate the frequency of the n words, which pop up most
                courseData.abstractWordFrequency = self.textSummarizer.frequency_Words(cleanText, 10, language=language)
            # if the language is uncertain
            # create an error text, that the language is not supported
            else:
                self.error = "Die Sprache der Datei wird nicht unterstuetzt."
            QtWidgets.QApplication.processEvents()
            # if the language Detection produced an error
            # set the error on the error text
        except ExceptionCheckLanguage as e:
            logging.warning(
                "Die Datei: %s %s",
                courseData.name, str(e))
            self.error = str(e)
            # if the summarizer produced an error
            # set the error on the error text
        except ExceptionTextAbstraction as e:
            error = "Die Datei besitzt weniger Sätze oder Wörter, als die Zusammenfassung benötigt."
            logging.warning(
                "Die Datei: %s %s",
                courseData.name, error)
            self.error = error
        return courseData