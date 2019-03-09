.. Moodle-HTW-DMS documentation master file, created by
   sphinx-quickstart on Tue Mar  5 12:15:43 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

   
Welcome to Moodle-HTW-DMS's documentation!
==========================================

This is the documentation of Moodle-HTW-DMS.


Explanation and motivation
==========================

Moodle is an E-Learning-Platform, which is widespread in the university and school context. The lecturers are using it for sharing lecture notes, make quizzes, to see how well the students perform etc. 

The problem with Moodle is that it has no search function for finding words in the documents, which provided for a student. That cause that the student has to open every data on his own and search his required theme to make his study. In addition, Moodle has not automatically download of all provided files. Therefore, the student has to download every file manually. In one semester, it is typically for a course to have at least 14 course files. If a student booked six courses, he has to download round about 84 files manually. That cost a lot of time, which the student should spend in learning and not in downloading the required data. In addition, this download process connected with the question how will the data saved on the computer? 
That are reasons why this tool was invent. The following table aggregates the problems of Moodle and with what function these difficulties shall be sort out.


+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------+
| Motivation                                                                                  | Goal                                                            |
+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------+
| High expenditure to search data, because the name is not clear => the themes are not clear  | - Enable to search data with words                              |
|                                                                                             | - Enable to search data by semester, course name or lecturer    |
|                                                                                             | - Summary the course data                                       |
+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------+
| No function for automatically download                                                      | - Automatically download                                        |
+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------+
| Own organization in folders is connected with high expenditure                              | - Saving the course data and the meta-information in a database |
+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------+
| Information deficit if the course after semester will be delete                             | - Automatically download                                        |
+---------------------------------------------------------------------------------------------+-----------------------------------------------------------------+


Used Python-Modules 
===================
#.  PyQt5 https://www.riverbankcomputing.com/software/pyqt/download5 author: Riverbank Computing Limited
#. nltk https://www.nltk.org/ author: Steven Bird
#. sqlalchemy https://www.sqlalchemy.org/ author: Mike Bayer
#. scrapy https://scrapy.org/ author: Scrapy developers 
#. langdetect https://pypi.org/project/langdetect/ author: Michal "Mimino" Danilak
#. pdfminer https://pypi.org/project/pdfminer.six/ author: Yusuke Shinyama + Philippe Guglielmetti
#. BeautifulSoup https://pypi.org/project/beautifulsoup4/ author: Leonard Richardson
#. docx https://python-docx.readthedocs.io/en/latest/ author: Steve Canny
#. pptx https://pypi.org/project/python-pptx/ author: Steve Canny


System architecture
===================

* The main program consist out of the modules “Controller.py”, “FileHandler.py”, “MoodleCrawlerHTWBerlin.py”, “DatabaseManager.py”, “TextProcessing.py”, “FileToText.py”, “TextCleaner.py”, “CheckLanguage.py” and “TextAbstraction.py”.
* The setup.py is for checking and downloading all required python modules and the required nltk-data.
* Controller.py is for loading the specific guis from the gui folder and give the window logic. It will also call the other modules.
* FileHandler.py is for opening, saving and deleting selected CourseData from the user.
* MoodleCrawlerHTWBerlin.py is for searching in the moodle side for courses and files and save them to the database.
* DatabaseManager.py is the connection to the database. It is for creating the required tables. Inserting, updating, deleting and loading object from the database.
* TextProcessing.py is the logic for the process to processing the CourseData.
* FileToText.py is for reading the text out of the CourseData.
* TextCleaner.py is for cleaning the read text from links etc.
* CheckLanguage.py is for checking the language of the text.
* TextAbstraction.py is for summarize the read CourseData.

.. image:: pictures/Systemarchitektur.png


Data structure
==============

* Lecturer: a Lecturer from the moodle side
* MoodleCourse: a course from the user
* LecturerHasCourse: The connection between Lecturer and MoodleCourse
* MoodleError: An error, which occur in the downloading process
* CourseData: The data, which is in a MoodleCourse
* DateOfCrawling: When was a download process was start
* User: The user with his login information for the moodle side
* Login Success: The information if a login was successfully, because the used framework scrapy has no opportunity to communicate directly with the calling process.

.. image:: pictures/DataStructure.png


Application logic
=================

.. toctree:: ApplicationLogic


Folder structure
================
* Benutzerhilfe: In this folder are videos how to start the application on windows and linux and how to use the different functions
* DB: In this folder is stored the interface IDatabaseManager and DatabaseManager. Also in this folder the database will be saved.
* Documentation: In this folder are the sphinx-documentation, the pictures of the data structure, system architecture and the activity diagrams
* Exceptions: In this folder are the own Excepions located.
* FileHandler: In this Folder is stored the interface IFileHandler and FileHandler.
* GUI: In this Folder are all GUIs saved, which will be loaded by the Controller. To see the GUIs layout and the name of the object, click on the following link.
.. toctree:: GUI_Folder
	
* Model: In this Folder are all classes which represent the data structure saved.
* MoodleCrawler: In this Folder is stored the interface IMoodleCrawler and MoodlCrawlerHTWBerlin.
* temp: In the temp folder will be saved all CourseData, which shall get an text processing or the user wants to open the file.
* Text_Processing: In this Folder all Interfaces and Classes are located for the text processing. The modules are ICheckLanguage, CheckLanguage, IFileToText, FileToText, ITextAbstraction, TextAbstraction, ITextCleaner, TextCleaner and TextProcessing.
* UnitTest: In this folder are the classes for the testing of the different units.
* venv: In this folder are the required python modules like scrapy or PyQt5 for using them on windows.


.. image:: pictures/FolderStructure.png



Python packages 
===============

.. toctree::
   :maxdepth: 4

   Controller
   DB
   Exceptions
   FileHandler
   GUI
   Model
   MoodleCrawler
   Text_Processing
   setup



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`






