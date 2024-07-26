from PySide6.QtWidgets import QListWidget, QMenu
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction


class AdminUserList(QListWidget):
    remove_user = Signal(str)

    def __init__(self, parent=None):
        super(AdminUserList, self).__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        context_menu = QMenu(self)

        remove_action = QAction("Remove user", self)
        remove_action.triggered.connect(lambda: self.remove_user.emit())
        context_menu.addAction(remove_action)

        context_menu.exec_(self.mapToGlobal(pos))

