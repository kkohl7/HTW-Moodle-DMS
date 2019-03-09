import re

from Text_Processing.ITextCleaner import ITextCleaner


class TextCleaner(ITextCleaner):
    def cleaningText(self, text):
        # delete links
        cleanText = re.sub(r'https?://[\w\./\-\_\?=&~+#;%]+', '', text)
        # delete multiple "." followed by multiples " "
        cleanText = re.sub(r'\.+ {0,}', '. ', cleanText)
        # delete multiple "\n"
        cleanText = re.sub(r'\n+', '\n', cleanText)
        return cleanText
