from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QListWidget,
    QTabWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QSplitter,
    QSizePolicy
)
from PySide6 import QtGui
from PySide6.QtGui import QPixmap, QIcon, QAction, QFont
from PySide6.QtCore import Signal, Qt, QSize
from View.UIRepViewer import RepositoryViewerWidget
from View.BaseWindow import BaseWindow
from View.UIMergeRequestTab import MergeRequestTab
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.UIDiffsWidget import DiffsWidget
from View.UIChangesList import ChangesList
import os


def _get_item_obj(item: str) -> QListWidgetItem:
    list_item = QListWidgetItem(item)
    list_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return list_item


class TabIndex:
    NONE = -1
    HISTORY = 0
    CHANGES_LIST = 1
    MERGE_REQUEST = 2


class GitSnifferWidget(QWidget):
    merge_request_selected = Signal()

    def __init__(self):
        super().__init__()
        self.changes_list_files_open = []
        self.changes = []
        """ History """
        self.history = QListWidget()
        self.history.setFont(QtGui.QFont("Courier New", 10))
        self.history.setSpacing(2)
        self.history_tab = QWidget()
        self.history_tab.setObjectName("HistoryTab")
        """ Changes List """
        self.changes_list = ChangesList()
        self.changes_list.setFont(QtGui.QFont("Courier New", 10))
        self.changes_list.setSpacing(2)
        self.changes_list_tab = QWidget()
        self.changes_list_tab.setObjectName("ChangesListTab")
        """ Merge Request """
        self.merge_request = MergeRequestTab()
        self.merge_request_tab = QWidget()
        self.merge_request_tab.setObjectName("MergeRequestTab")
        """ Other Widgets """
        self.tabs = QTabWidget()
        self.layout = QVBoxLayout()
        self.build()
        self.connect_signals()

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
        """ Merge tab """
        merge_request_layout = QVBoxLayout()
        merge_request_layout.addWidget(self.merge_request)
        self.merge_request_tab.setLayout(merge_request_layout)
        """Tabs"""
        self.tabs.setFont(QtGui.QFont("Courier New", 10))
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.changes_list_tab, "Change list")
        self.tabs.addTab(self.merge_request_tab, "Marge Request")
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def connect_signals(self):
        self.changes_list.itemClicked.connect(self.on_change_list_clicked)
        self.history.itemClicked.connect(self.on_commit_clicked)

    def on_change_list_clicked(self, item: QListWidgetItem):
        if not item:
            return

        try:
            change_file, diff = item.data(Qt.ItemDataRole.UserRole)
            if change_file and diff:
                diff_widget = DiffsWidget(diff, change_file)
                diff_widget.show()
                diff_widget.widget_closed.connect(lambda widget: self.changes_list_files_open.remove(widget))
                self.changes_list_files_open.append(diff_widget)
        except TypeError:
            return

    @staticmethod
    def on_commit_clicked(commit):
        print(commit)


class UIGitTab(QWidget):
    """ This widget is show when the Git tab is pressed in the LauncherWindow """
    history_tab_clicked = Signal()
    changes_list_clicked = Signal()
    merge_request_clicked = Signal()

    def __init__(self, working_path: str):
        super().__init__()
        self.repository_path = working_path
        """ Toolbar build """
        self.header = QHBoxLayout()
        self.upload_btn: QPushButton = BaseWindow.create_button(self, "arrowUp.png")
        self.download_btn: QPushButton = BaseWindow.create_button(self, "arrowDown.png")
        self.publish_btn: QPushButton = BaseWindow.create_button(self, "publish.png", "Publish")
        """ Layouts """
        self.main_layout = QVBoxLayout()
        self.body_layout = QHBoxLayout()
        """ Custom Widgets """
        self.repository_viewer = RepositoryViewerWidget(working_path)
        self.repository_viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.git_sniffer = GitSnifferWidget()
        self.git_sniffer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        """ Other widgets """
        self.splitter = QSplitter(Qt.Horizontal)
        self.build()
        self.apply_styles()
        self.connect_signals()
        self.user_session = None

    def build(self):
        """Buttons"""
        self.upload_btn.setFixedSize(QSize(120, 35))
        self.download_btn.setFixedSize(QSize(120, 35))
        self.publish_btn.setFixedSize(QSize(120, 35))
        """ Header Layout """
        self.repository_viewer.buttons_layout.addWidget(self.upload_btn, 0, Qt.AlignmentFlag.AlignLeft)
        self.repository_viewer.buttons_layout.addWidget(self.download_btn, 3, Qt.AlignmentFlag.AlignLeft)
        self.repository_viewer.buttons_layout.addWidget(self.publish_btn, 10, Qt.AlignmentFlag.AlignLeft)
        """ Body layout """
        self.splitter.addWidget(self.repository_viewer)
        self.splitter.addWidget(self.git_sniffer)
        self.body_layout.addWidget(self.splitter)
        """ Main layout """
        self.main_layout.addLayout(self.header)
        self.main_layout.addLayout(self.body_layout)
        self.setLayout(self.main_layout)

    def apply_styles(self):
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.upload_btn, "Blue")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.download_btn, "Blue")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.publish_btn, "Brown")

        publish_font = self.publish_btn.font()
        publish_font.setBold(True)
        self.publish_btn.setFont(publish_font)

    def connect_signals(self):
        self.git_sniffer.tabs.tabBarClicked.connect(self._on_git_sniffer_tab_clicked)

    def send_starting_signals(self):
        self.history_tab_clicked.emit()
        self.changes_list_clicked.emit()
        self.merge_request_clicked.emit()

    def _on_git_sniffer_tab_clicked(self, tab_index: int):
        if tab_index == TabIndex.HISTORY:
            self.history_tab_clicked.emit()
        elif tab_index == TabIndex.CHANGES_LIST:
            self.changes_list_clicked.emit()
        elif tab_index == TabIndex.MERGE_REQUEST:
            self.merge_request_clicked.emit()

    def create_action(self, img_name: str, button_tip: str) -> QAction:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "../Resources/Img/", img_name)
        pixmap = QPixmap(icon_path)
        action = QAction(QIcon(pixmap), "", self)
        action.setStatusTip(button_tip)
        return action

    def on_get_repository_history(self, commits: list):
        self.git_sniffer.history.clear()
        for commit in commits:
            commit_item = QListWidgetItem(commit)
            commit_id = commit.split(" ")[0]
            commit_item.setData(Qt.ItemDataRole.UserRole, commit_id)
            self.git_sniffer.history.addItem(commit_item)

        if self.git_sniffer.history.count() == 0:
            self.git_sniffer.history.addItem("No Commits yet")

    def on_get_current_changes(self, modified: list, changes: list):
        self.git_sniffer.changes.clear()
        self.git_sniffer.changes_list.clear()

        for change_file, diff in modified:
            change_item = QListWidgetItem(change_file)
            change_item.setData(Qt.ItemDataRole.UserRole, (change_file, diff))
            change_item.setToolTip(diff)
            self.git_sniffer.changes_list.addItem(change_item)
            self.git_sniffer.changes.append(change_file)

        for change_file, change in changes:
            change_item = QListWidgetItem()
            change_item.setText(f"{change_file}: -> ({change})")
            change_item.setData(Qt.ItemDataRole.UserRole, (change_file, change))
            self.git_sniffer.changes_list.addItem(change_item)
            self.git_sniffer.changes.append(change_file)

        if self.git_sniffer.changes_list.count() == 0:
            self.git_sniffer.changes_list.addItem("No changes yet")

    def show_anim_tab(self):
        self.splitter.setSizes([1, 0])
        self.git_sniffer.setDisabled(True)

    def hide_anim_tab(self):
        self.splitter.setSizes([1, 1])
        self.git_sniffer.setDisabled(False)

    def on_repository_path_updated(self):
        self.repository_viewer.set_root_directory()

    def set_main_branch_in_merge_request_tab(self, main_branch: str):
        self.git_sniffer.merge_request.set_main_branch(main_branch)

    def set_all_branches_in_merge_request_tab(self, branches: list):
        self.git_sniffer.merge_request.set_all_branches(branches)

    def set_all_merge_requests(self, merge_requests: list):
        self.git_sniffer.merge_request.add_merge_requests(merge_requests)

    def set_merge_request_commits(self, commits: list):
        self.git_sniffer.merge_request.add_commits(commits)

    def set_merge_request_changes(self, changes: list):
        self.git_sniffer.merge_request.add_changes(changes)

    def set_merge_requests_comments(self, comments: list):
        self.git_sniffer.merge_request.add_comments(comments)