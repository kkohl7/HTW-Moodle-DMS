from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest

from DB.IDatabaseManager import IDatabaseManager
from Exceptions.OwnExceptions import ExceptionTextAbstraction
from Text_Processing.ITextAbstraction import ITextAbstraction


class TextAbstraction(ITextAbstraction):
    def __init__(self, database: IDatabaseManager):
        """
        Attributes:
            - database (IDatabaseManager): The Connection to the database
            - stopwords (set): Set of words which shall be not counted
    """
        self.stopwords = set()
        self.database = database

    def _compute_frequencies(self, listOfLowerSentences: list) -> dict:
        """_compute_frequencies compute the relative frequency of each word

            :param listOfLowerSentences: a list of sentences already tokenized in sentences and words. All words are lowercase.
            :return A dictionary of relative frequency for each word in listOfLowerSentences
        """
        freq = defaultdict(int)
        # iterate through each sentence in listOfLowerSentences
        for sentence in listOfLowerSentences:
            # iterate through each word in sentence
            for word in sentence:
                # if word is not in stopwords and is a real word
                # increase the occurs of word in freq by 1
                if word not in self.stopwords and word.isalpha():
                    freq[word] += 1
        # m is the number of words which occurs in listOfLowerSentences
        m = float(sum(freq.values()))
        # calculate for each word in freq the relative occurrence
        for w in list(freq):
            freq[w] = freq[w] / m
        return freq

    def summarize_Text(self, text, n, language='english'):
        self.language = language
        # fill the stop word set
        self._fillStopwords()

        # sentences is the list of sentence from the input text
        sentences = sent_tokenize(text, language=self.language)

        # if n is smaller then the number of sentences, then raise ExceptionTextAbstraction
        if n > len(sentences):
            raise ExceptionTextAbstraction("Der Text hat weniger Sätze als benötigt!")

        # pickedSentences display the actual number of picked sentences for the abstract
        pickedSentences = 0
        abstract = ""

        # While not enough sentences are picked repeat
        while pickedSentences < n:
            # in listOfLowerSentences are all sentences from the input sentences and all words are lowercase
            listOfLowerSentences = [word_tokenize(s.lower()) for s in sentences]
            # usedWords is the list of words, which are in the picked summary sentence
            usedWords = []
            # in ranking for each sentence the weight will be saved
            ranking = defaultdict(int)
            # calculate the frequency for all words
            # freq is a dictionary with words as key
            freq = self._compute_frequencies(listOfLowerSentences)
            # iterate through the list of sentences
            for i, sentence in enumerate(listOfLowerSentences):
                ranking[i] = 0
                # iterate through every word in in sentence
                for word in sentence:
                    # if word is in dictionary freq, than add the frequency of the word to the ranking of sentence[i]
                    if word in freq:
                        ranking[i] += freq[word]
            # get the index of the the sentence with the highest score
            # the result is a list
            sentenceIndex = self.__rank(ranking, 1)
            # go for the indexes in sentenceIndex
            for j in sentenceIndex:
                # add to the abstract result the sentence with the actual highest score
                abstract += "-> " + sentences[j] + "\n"
                # usedWords are all words in lower case from the picked sentence
                usedWords = word_tokenize(sentences[j].lower())
                # add all words from usedWords to stopwords
                for word in usedWords:
                    self.stopwords.add(word)
                # remove the picked sentence from the list of sentences
                sentences.pop(j)
                pickedSentences += 1
        return abstract

    def __rank(self, ranking: dict, n: int) -> list:
        """ return the first n elements with highest ranking

            :param ranking: the dictionary which contains the score of each element
            :param n: the number of sentence which shall be extracted"""
        return nlargest(n, ranking, key=ranking.get)

    def frequency_Words(self, text, n, language='english'):
        self.language = language
        # fill the stop word set
        self._fillStopwords()
        # sentences is the list of sentences from the input text
        sentences = sent_tokenize(text, language=self.language)
        # listOfLowerSentences is the list of sentences from the input in lowercase
        listOfLowerSentences = [word_tokenize(s.lower()) for s in sentences]

        # in ranking for each sentence the weight will be saved
        ranking = defaultdict(int)
        # iterate through each sentence in listOfLowerSentences
        for i, sentence in enumerate(listOfLowerSentences):
            # iterate through every word in sentence
            for word in sentence:
                # if the word is not in stopwords + is a real word + has more than 2 characters
                # increase the frequency of the word
                # The word must have more than 2 characters,
                # because mathematical scripts often contain "f", "x" etc.
                if word not in self.stopwords and word.isalpha() and len(word) > 2:
                    ranking[word] += 1
        # if the text contains less words than n, than ExceptionTextAbstraction
        if n > len(ranking):
            raise ExceptionTextAbstraction("Der Text hat weniger Wörter als benötigt!")

        # get the n indexes, which are the words, of the words with the highest scores
        sentences_indexes = self.__rank(ranking, n)
        abstract = ""
        # iterate through all indexes
        for word in sentences_indexes:
            # write in each line the word and the time of occurence in the string
            abstract += "-> " + word + ": " + str(ranking[word]) + "\n"
        return abstract

    def _fillStopwords(self):
        """
        _fillStopwords fill the set of stopwords. With stopwords from nltk and university specific
        words like dr. prof. university etc.
        """
        # Create set of Stopwords, which has no influence on the summary
        # the words are from nltk stopwords, for the language of the text and all punctiation
        self.stopwords = set(stopwords.words(self.language) + list(punctuation))
        # stop words, which shall be stop words but are not in the set of stop words from nltk
        self.stopwords = self.stopwords | set(['dass'])

        # get specific university stopwords, like "dr.", "prof." etc.
        # stopwords university graduation
        self.stopwords = self.stopwords | set(['bachelor', 'master'])
        # stopwords title of the lecturer
        self.stopwords = self.stopwords | set(['prof', 'prof.', 'dr', 'dr.', 'professor', 'doktor', 'doctor'])
        # stopwords university words
        self.stopwords = self.stopwords | set(
            ['hochschule', 'fachbereich', 'studiengang', 'bachelorstudiengang', 'masterstudiengang', 'uni',
             'universität', 'university', 'vorlesung', 'lecture', 'course', 'wintersemester', 'sommersemester', 'wise',
             'sose'])
        # stopwords for the HTW
        # TODO for other universities change the words
        self.stopwords = self.stopwords | set(['htw', 'berlin', 'technik', 'wirtschaft'])
        # stopwords from lecturer slides
        self.stopwords = self.stopwords | set(['seite', 'folie', 'side', 'page'])

        # stopwords the names of the lecturer
        lecturers = self.database.getAllLecturer()
        # iterate through lecturers
        for lecturer in lecturers:
            # split the name at every space character
            firstAndFamilyName = lecturer.name.split(" ")
            # add every name to the set of stopwords
            for names in firstAndFamilyName:
                self.stopwords.add(names.lower())
