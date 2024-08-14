from PySide6.QtWidgets import QApplication, QListWidget, QMenu, QVBoxLayout, QWidget
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
import sys


class ChangesList(QListWidget):
    restore_file_clicked = Signal()
    upload_file_clicked = Signal()

    def __init__(self, parent=None):
        super(ChangesList, self).__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        context_menu = QMenu(self)

        restore_file_action = QAction("Restore file", self)
        restore_file_action.triggered.connect(lambda: self.restore_file_clicked.emit())
        context_menu.addAction(restore_file_action)

        upload_action = QAction("Upload file", self)
        upload_action.triggered.connect(lambda: self.upload_file_clicked.emit())
        context_menu.addAction(upload_action)

        context_menu.exec_(self.mapToGlobal(pos))
