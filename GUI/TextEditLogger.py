import logging
class QTextEditLogger(logging.Handler):
    """
    QTextEditLogger is for writing the log-information to plainTextEdit
    """
    def __init__(self, parent):
        super().__init__()
        self.widget = parent.plainTextEdit
        self.widget.setReadOnly(True)
        self.active = 1

    def deactivate(self):
        self.active = 0

    def emit(self, record):
        msg = self.format(record)
        if self.active == 1:
            self.widget.appendPlainText(msg)