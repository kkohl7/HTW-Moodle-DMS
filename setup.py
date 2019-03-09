import importlib
import subprocess
import os


def install(listOfRequirkePackagesNameImport: list, listOfRequirePackagesNameDownload: list):
    """
    install check if the required packages are already installed. If not it will install them.
    :param listOfRequirkePackagesNameImport: The names for required imports
    :param listOfRequirePackagesNameDownload: The names for the required installs
    """
    length = len(listOfRequirkePackagesNameImport)
    for i in range(length):
        try:
            importlib.import_module(listOfRequirkePackagesNameImport[i])
            print(listOfRequirkePackagesNameImport[i] + " ist bereits installiert!")
        except ImportError as e:
            print(listOfRequirkePackagesNameImport[i] + " ist nicht installiert und muss nach installiert werden!")
            if os.name == 'nt':
                subprocess.call(['pip', 'install', listOfRequirePackagesNameDownload[i]])
            else:
                subprocess.call(['pip3', 'install', listOfRequirePackagesNameDownload[i]])

    import nltk

    try:
        path = nltk.data.find('corpora/stopwords')
        print("Stopwords gefunden")
    except LookupError as e:
        print("Stopwords nicht gefunden. Diese müssen nach installiert werden.")
        nltk.download('stopwords')
    try:
        path = nltk.data.find('tokenizers/punkt')
        print("Tokenizer gefunden")
    except LookupError as e:
        print("Tokenizer nicht gefunden. Diese müssen nach installiert werden.")
        nltk.download('punkt')


if __name__ == '__main__':
    listOfRequirkePackagesNameImport = ["PyQt5", "nltk", "sqlalchemy", "scrapy", "langdetect", "pdfminer", "bs4", "docx", "pptx"]
    listOfRequirePackagesNameDownload = ["PyQt5", "NLTK", "sqlalchemy", "scrapy", "langdetect", "pdfminer.six", "bs4", "python-docx", "python-pptx"]
    install(listOfRequirkePackagesNameImport, listOfRequirePackagesNameDownload)
