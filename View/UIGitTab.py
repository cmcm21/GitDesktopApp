from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QListWidget,
    QTabWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QToolBar,
)
from PySide6 import QtGui
from PySide6.QtGui import QPixmap, QIcon, QAction, QFont
from PySide6.QtCore import Signal, Qt, QSize
from View.UIRepViewer import RepositoryViewerWidget
from View.BaseWindow import BaseWindow
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
import os


def _get_item_obj(item: str) -> QListWidgetItem:
    list_item = QListWidgetItem(item)
    list_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return list_item


class GitSnifferWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.history = QListWidget(self)
        self.history.setFont(QtGui.QFont("Courier New", 10))
        self.history.setSpacing(2)
        self.history_tab = QWidget(self)
        self.history_tab.setObjectName("History_tab")

        self.changes_list = QListWidget(self)
        self.changes_list.setFont(QtGui.QFont("Courier New", 10))
        self.changes_list.setSpacing(2)
        self.changes_list_tab = QWidget(self)
        self.changes_list_tab.setObjectName("Changes_list")

        self.tabs = QTabWidget(self)
        self.layout = QVBoxLayout(self)
        self.build()

    def build(self):
        """ History layout """
        history_layout = QVBoxLayout()
        history_label = QLabel("Commits History")
        history_label.setFont(QFont("Courier New", 10))
        history_label.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #000000, "
                                    "stop: 1 #333333);")
        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history)
        self.history_tab.setLayout(history_layout)
        """ Change list layout """
        changes_list_layout = QVBoxLayout()
        changes_list_label = QLabel("Changes List")
        changes_list_label.setFont(QFont("Courier New", 10))
        changes_list_label.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #000000, "
                                         "stop: 1 #333333);")
        changes_list_layout.addWidget(changes_list_label)
        changes_list_layout.addWidget(self.changes_list)
        self.changes_list_tab.setLayout(changes_list_layout)

        self.tabs.setFont(QtGui.QFont("Courier New", 10))
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.changes_list_tab, "Change list")
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def fill_changed_list(self):
        for entry in ["file 1", "file 2", "file 3", "file 4", "file 5"]:
            self.add_change_item(entry)

    def fill_history(self):
        for entry in ["commit 1", "commit 2", "commit 3", "commit 4", "commit 5"]:
            self.add_history_item(entry)

    def add_change_item(self, item: str):
        self.changes_list.addItem(_get_item_obj(item))
        return

    def add_history_item(self, item: str):
        self.history.addItem(_get_item_obj(item))
        return


class UIGitTab(QWidget):
    """ This widget is show when the Git tab is pressed in the LauncherWindow """
    upload_signal = Signal()
    get_latest_signal = Signal()

    def __init__(self, working_path: str):
        super().__init__()
        self.repository_path = working_path
        """ Toolbar build """
        self.header = QHBoxLayout()
        self.upload_btn: QPushButton = BaseWindow.create_button(self, "arrowUp.png")
        self.download_btn: QPushButton = BaseWindow.create_button(self, "arrowDown.png")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.upload_btn, "Blue")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.download_btn,  "Blue")
        """ Connect action triggers """
        self.upload_btn.clicked.connect(lambda: self.upload_signal.emit())
        self.download_btn.clicked.connect(lambda: self.get_latest_signal.emit())
        """ Layouts """
        self.main_layout = QVBoxLayout()
        self.body_layout = QHBoxLayout()
        """ Custom Widgets """
        self.repository_viewer = RepositoryViewerWidget(working_path)
        self.git_sniffer = GitSnifferWidget()
        #TODO: Remove this after
        self.git_sniffer.fill_history()
        self.git_sniffer.fill_changed_list()
        self.build()

    def build(self):
        """Buttons"""
        self.upload_btn.setFixedSize(QSize(120, 35))
        self.download_btn.setFixedSize(QSize(120, 35))
        """ Header Layout """
        self.header.addWidget(self.upload_btn)
        self.header.addWidget(self.download_btn)
        self.header.addSpacing(500)
        """ Body layout """
        self.body_layout.addWidget(self.repository_viewer)
        self.body_layout.addWidget(self.git_sniffer)
        """ Main layout """
        self.main_layout.addLayout(self.header)
        self.main_layout.addLayout(self.body_layout)
        self.setLayout(self.main_layout)

    def create_action(self, img_name: str, button_tip: str) -> QAction:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "../Resources/Img/", img_name)
        pixmap = QPixmap(icon_path)
        action = QAction(QIcon(pixmap), "", self)
        action.setStatusTip(button_tip)
        return action

    def on_repository_path_updated(self):
        self.repository_viewer.set_root_directory()
