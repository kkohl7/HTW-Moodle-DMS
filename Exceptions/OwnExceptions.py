class ExceptionReadDataToText(Exception):
    """
    Exception when an error pop up while reading text from data
    """
    def __init___(self, problem):
        Exception.__init__(self,"my exception was raised with arguments {0}".format(problem))
        self.problem = problem
        super(ExceptionReadDataToText, self).__init__(problem)

class ExceptionCheckLanguage(Exception):
    """
    Exception when an error pop up while checking the language of a text
    """
    def __init___(self, problem):
        Exception.__init__(self,"my exception was raised with arguments {0}".format(problem))
        self.problem = problem
        super(ExceptionCheckLanguage, self).__init__(problem)

class ExceptionTextAbstraction(Exception):
    """
    Exception when an error pop up while abstract a text
    """
    def __init___(self, problem):
        Exception.__init__(self,"my exception was raised with arguments {0}".format(problem))
        self.problem = problem
        super(ExceptionCheckLanguage, self).__init__(problem)