import os
from os import name as os_name
import subprocess
import webbrowser

from FileHandler.IFileHandler import IFileHandler


class FileHandler(IFileHandler):

    def openFile(self, courseData, path):
        # if the dataType is an html
        # than open the link of the file in the browser
        if courseData.dataType == 'html':
            webbrowser.open(courseData.name)
        # otherwise create the file in the path folder
        # and open it in dependency on the operating system
        else:
            path = path + courseData.name
            try:
                with open(path, "wb") as output_file:
                    output_file.write(courseData.dataContent)
                if os_name == 'nt':
                    # if windows system open per subprocess
                    subprocess.Popen(path, shell=True)
                else:
                    # if other system open per webbrowser
                    webbrowser.open_new('file://' + path)
            except:
                pass

    def saveFile(self, courseData, path):
        if courseData.dataType == 'html':
            path = path + str(courseData.id) + str(courseData.position) + '.html'
        else:
            path = path + courseData.name
        try:
            with open(path, "wb") as output_file:
                output_file.write(courseData.dataContent)
        except:
            pass
        return path

    def deleteFile(self, path):
        try:
            os.remove(path)
        except Exception:
            pass

    def deleteAllFilesInFolder(self, path):
        # try to delete every file in the folder
        for the_file in os.listdir(path):
            file_path = os.path.join(path, the_file)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    pass
