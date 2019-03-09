from unittest import mock
from unittest.mock import call

from twisted.trial import unittest

from FileHandler.FileHandler import FileHandler
from Model.Model import CourseData


class TestFileHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fileHandler = FileHandler()
        cls.courseDataText = CourseData(id=1, position=1, name="test.txt", dataType="txt", dataContent="Hallo")
        cls.courseDataHtml = CourseData(id=1, position=1, name="www.test.de", dataType="html", dataContent="Hallo")

    @mock.patch("FileHandler.FileHandler.os_name", 'nt')
    @mock.patch('subprocess.Popen')
    @mock.patch("builtins.open", read_data="data")
    def test_openFileText_Success_Windows(self, mock_open, mock_subproc_popen):
        """
        Test if the openFile will open the text courseData and open it with subprocess
        Procedure:
            1. call open File
            ---------
            Verification:
            2. the open file process open the file in path
            3. the expected dataContent was wrote in the file
            4. the open file process was called
            5. the subprocess was called with the right arguments
            6. the subprocess was called
        """
        self.fileHandler.openFile(self.courseDataText, "C:/")

        # check if the data Content was print to the file
        expectedWriteCall = call().__enter__().write('Hallo')
        mock_calls = mock_open.mock_calls
        found = False
        for calls in mock_calls:
            if calls == expectedWriteCall:
                found = True
        self.assertTrue(found)

        self.assertTrue(mock_open.called)
        # test if subprocess was called with the rigt values
        mock_subproc_popen.assert_called_with('C:/test.txt', shell=True)
        self.assertTrue(mock_subproc_popen.called)

    @mock.patch("FileHandler.FileHandler.os_name", 'posix')
    @mock.patch('webbrowser.open_new')
    @mock.patch("builtins.open", read_data="data")
    def test_openFileText_Success_Linux(self, mock_open, mock_webbrowser):
        """
        Test if the openFile will open the text courseData and open it with webbrowser_open_new
        Procedure:
            1. call open File
            ---------
            Verification:
            2. the open file process open the file in path
            3. the expected dataContent was wrote in the file
            4. the open file process was called
            5. the subprocess was called with the right arguments
            6. the subprocess was called
        """
        self.fileHandler.openFile(self.courseDataText, "C:/")

        # check if the data Content was print to the file
        expectedWriteCall = call().__enter__().write('Hallo')
        mock_calls = mock_open.mock_calls
        found = False
        for calls in mock_calls:
            if calls == expectedWriteCall:
                found = True
        self.assertTrue(found)

        self.assertTrue(mock_open.called)
        # test if open webbrowser was called with the right values
        mock_webbrowser.assert_called_with("C:/test.txt")
        self.assertTrue(mock_webbrowser.called)

    @mock.patch('webbrowser.open')
    def test_openFileHtml_Success(self, mock_webbrowser):
        """
        Test if the openFile will open the html courseData and open it with webbrowser
        Procedure:
            1. call open File
            ---------
            Verification:
            2. the open webbrowser process open the file in path
            3. the open webbrowser process was called
        """
        self.fileHandler.openFile(self.courseDataHtml, "C:/")

        # test if open webbrowser was called with the right values
        mock_webbrowser.assert_called_with("www.test.de")
        self.assertTrue(mock_webbrowser.called)

    @mock.patch('subprocess.Popen')
    @mock.patch("builtins.open", read_data="data")
    def test_openFileText_FileWithThisNameIsAlreadyStored(self, mock_open, mock_subproc_popen):
        """
        Test if the openFile will not open the CourseData, if the same data is already in use.
        Procedure:
            0. set the side effect
            1. call open File
            ---------
            Verification:
            2. the open file process open the file in path
            3. the open file process was called
            4. the subprocess for opening was not called
        """
        def side_effect()-> Exception:
            raise Exception

        mock_open.side_effect = side_effect
        self.fileHandler.openFile(self.courseDataText, "C:/")

        # test if open file was called with the right values
        mock_open.assert_called_with("C:/test.txt", 'wb')
        self.assertTrue(mock_open.called)
        # test if subprocess was not called
        self.assertFalse(mock_subproc_popen.called)

    @mock.patch("builtins.open")
    def test_saveFileText_Success(self, mock_open):
        """
        Test if the saveFile will save the text CourseData to the path
        Procedure:
            0. set the expected path
            1. call save File
            ---------
            Verification:
            2. the file will open with the path
            3. in the file will print the expected dataContent
            4. the open file command was called
            5. expected path = path from save file
        """
        expectedPath = "C:/test.txt"
        path = self.fileHandler.saveFile(self.courseDataText, "C:/")
        # test if open file was called with the right values
        mock_open.assert_called_with("C:/test.txt", 'wb')

        # check if the data Content was print to the file
        expectedWriteCall = call().__enter__().write('Hallo')
        mock_calls = mock_open.mock_calls
        found = False
        for calls in mock_calls:
            if calls == expectedWriteCall:
                found = True
        self.assertTrue(found)

        self.assertTrue(mock_open.called)
        self.assertEqual(path, expectedPath)

    @mock.patch("builtins.open")
    def test_saveFilehtml_Success(self, mock_open):
        """
        Test if the saveFile will save the text courseData to the path
        Procedure:
            0. set the expected path
            1. call save File
            ---------
            Verification:
            2. the file will open with the path
            3. in the file will print the expected dataContent
            4. the open file command was called
            5. expected path = path from save file
        """
        expectedPath = "C:/11.html"
        path = self.fileHandler.saveFile(self.courseDataHtml, "C:/")
        # test if open file was called with the right values
        mock_open.assert_called_with("C:/11.html", 'wb')

        # check if the data Content was print to the file
        expectedWriteCall = call().__enter__().write('Hallo')
        mock_calls = mock_open.mock_calls
        found = False
        for calls in mock_calls:
            if calls == expectedWriteCall:
                found = True
        self.assertTrue(found)

        self.assertTrue(mock_open.called)
        self.assertEqual(path, expectedPath)

    @mock.patch("builtins.open", read_data="data")
    def test_saveFileText_FileWithThisNameIsAlreadyStored(self, mock_open):
        """
        Test if the SaveFile will not save the courseData, when the file is still in use.
        Procedure:
            0. set the side effect
            1. call save File
            ---------
            Verification:
            2. the save file process open the file in path
            3. the open file was called
        """
        def side_effect(path)-> Exception:
            raise Exception

        mock_open.side_effect = side_effect
        self.fileHandler.saveFile(self.courseDataText, "C:/")

        # test if open file was called with the right values
        mock_open.assert_called_with("C:/test.txt", 'wb')
        self.assertTrue(mock_open.called)


    @mock.patch("os.remove")
    def test_deleteFile_Success(self, mock_remove):
        """
        Test if the deleteFile will delete the CourseData from the path
        Procedure:
            1. call delete File
            ---------
            Verification:
            2. the file will deleted in the path
            3. the remove command was called
        """
        self.fileHandler.deleteFile("C:/test.html")
        mock_remove.assert_called_with("C:/test.html")
        self.assertTrue(mock_remove.called)

    @mock.patch("os.remove")
    def test_deleteFile_FileStillOpen(self, mock_remove):
        """
        Test if the deleteFile will not delete the course data which is open
        Procedure:
            0. set the side effect, that the course data is still open
            1. call delete File
            ---------
            Verification:
            2. the file will deleted in the path
            3. the remove command was called
        """
        def side_effect(path: str)-> str:
            """
            :param path:
            :return: return the path
            :raise Exception when the path C:/test.pdf ist
            """
            if path == "C:/test.pdf":
                raise Exception
            else:
                path

        mock_remove.side_effect = side_effect

        self.fileHandler.deleteFile("C:/test.pdf")
        mock_remove.assert_called_with("C:/test.pdf")
        self.assertTrue(mock_remove.called)

    @mock.patch("os.path.isfile")
    @mock.patch("os.listdir")
    @mock.patch("os.remove")
    def test_deleteAllFilesInFolder_Success(self, mock_remove, mock_listDirectory, mock_os_isFile):
        """
        Test if the deleteAllFilesInFolder will delete all the courseData from the path
        Procedure:
            1. set the listDir (list of items in directory) on the files, which are in the directory
            2. set that all the files are files
            3. call delete all Files
            ---------
            Verification:
            4. both of the expected files were removed
            5. the removed command was called
        """
        listDir = ["test.html", "test.pdf"]
        mock_listDirectory.return_value = listDir
        mock_os_isFile.return_value = True

        self.fileHandler.deleteAllFilesInFolder("C:/")

        mock_remove.assert_any_call("C:/test.html")
        mock_remove.assert_any_call("C:/test.pdf")
        self.assertTrue(mock_remove.called)

    @mock.patch("os.path.isfile")
    @mock.patch("os.listdir")
    @mock.patch("os.remove")
    def test_deleteAllFilesInFolder_OneFileIsStillOpen(self, mock_remove, mock_listDirectory, mock_os_isFile):
        """
        Test if the deleteAllFilesInFolder will delete all the CourseData from the path except from course data which is still open
        Procedure:
            1. set the listDir (list of items in directory) on the files, which are in the directory
            2. set that all the files are files + define the side effects of remove
            3. call delete all Files
            ---------
            Verification:
            4. both of the expected files were called for remove
            5. the removed command was called
        """
        def side_effect(path: str)-> str:
            """
            :param path:
            :return: return the path
            :raise Exception when the path C:/test.pdf ist
            """
            if path == "C:/test.pdf":
                raise Exception
            else:
                path
        listDir = ["test.html", "test.pdf"]
        mock_listDirectory.return_value = listDir
        mock_os_isFile.return_value = True
        mock_remove.side_effect = side_effect

        self.fileHandler.deleteAllFilesInFolder("C:/")

        mock_remove.assert_any_call("C:/test.pdf")
        mock_remove.assert_any_call("C:/test.html")

        self.assertTrue(mock_remove.called)

if __name__ == '__main__':
    unittest.main()