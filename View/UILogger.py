import logging
from PySide6.QtCore import Qt, QMetaObject, Q_ARG
from PySide6.QtWidgets import QWidget, QTextEdit, QLabel, QVBoxLayout, QPushButton
from PySide6.QtGui import QFont, QAction
from View import CustomStyleSheetApplier
from Utils import FileManager
import os


# Create a custom logger
logger = logging.getLogger("UILogger")
logger.setLevel(logging.DEBUG)

file_path = os.path.join(FileManager.get_local_path(), "debug.log")
# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(file_path)
c_handler.setLevel(logging.WARNING)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add them to the handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        QMetaObject.invokeMethod(self.text_edit, "append", Qt.QueuedConnection, Q_ARG(str, msg))

class CustomQTextEdit(QTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        return

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        clear_action = QAction("Clear Action", self)
        clear_action.triggered.connect(lambda: self.clear())

        menu.addSeparator()
        menu.addAction(clear_action)

        menu.exec(event.globalPos())


class LoggerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

        """Setup Logger"""
        self.logger = logging.getLogger("UILogger")
        self.logger.setLevel(logging.DEBUG)
        self.handler = QTextEditLogger(self.text_edit)
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(self.handler)

    def _build(self):
        """Text edit"""
        self.text_edit = CustomQTextEdit(self)
        self.text_edit.setReadOnly(True)
        CustomStyleSheetApplier.set_q_text_edit_style_and_colour(self.text_edit, "Black", textColour="White")

        """Layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_edit)

    def clear_log(self):
        self.text_edit.clear()

    def append_log_message(self, message):
        self.text_edit.append(message)
        self.text_edit.update()

