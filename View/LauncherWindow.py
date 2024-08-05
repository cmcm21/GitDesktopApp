from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QComboBox,
    QTabWidget,
    QMenu,
    QFrame,
    QMessageBox
)
from View.BaseWindow import BaseWindow
from View.WindowID import WindowID
from View.UILogger import LoggerWidget
from View.UICommitWindow import CommitWindow
from View.UIGitTab import UIGitTab
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.UISessionWidget import UserSessionWidget
from View.UIAdminWidget import AdminWindow
from Utils.UserSession import UserSession
from Utils.Environment import ROLE_ID
import Utils.Environment as Env


class LauncherWindow(BaseWindow):
    upload_repository_signal = Signal(str)
    get_latest = Signal()
    project_changed = Signal(str)
    window_closed = Signal()
    login_out = Signal()
    admin_window_clicked = Signal()
    check_changes_list = Signal()

    def __init__(self, config: dict, window_id: WindowID, width=900, height=500):
        super(LauncherWindow, self).__init__("Puppet Launcher", window_id, width, height)
        self.user_session: UserSession = None
        self.project_combo_box_actions = {}
        self.config = config
        self.admin_window = None
        self.commit_window = None
        self._create_all_element()
        self._apply_styles()
        self._build()
        self._connect_signals()

    def _create_all_element(self):
        """ Layouts """
        self.main_layout = QGridLayout()
        self.header_layout = QHBoxLayout()
        self.body_layout = QHBoxLayout()
        self.body_left = QVBoxLayout()
        self.body_right = QVBoxLayout()
        self.footer_layout = QHBoxLayout()
        """Project Menu button"""
        self.combo_box = QComboBox(self)
        self.user_menu = QMenu("User", self)
        self.set_project_combo_box()
        """ New Workspace Button """
        self.new_workspace_btn = self.create_button(self, "plus.png", "")
        self.new_workspace_btn.setToolTip("New Workspace")
        self.new_workspace_btn.setObjectName("NewWorkspaceButton")
        self.new_workspace_btn.setFixedSize(QSize(80, 40))
        """ Open Maya Button """
        self.maya_btn = self.create_button(self, "mayaico.png", "")
        self.maya_btn.setToolTip("Open Maya")
        self.maya_btn.setObjectName("MayaButton")
        self.maya_btn.setFixedSize(QSize(80, 40))
        """ settings Button """
        self.settings_btn = self.create_button(self, "gear.png", "")
        self.settings_btn.setToolTip("Open Settings")
        self.settings_btn.setObjectName("SettingsButton")
        self.settings_btn.setFixedSize(QSize(80, 40))
        """ Other Widgets """
        self.left_frame = LauncherWindow.create_default_frame("MainWindowLeftFrame")
        self.left_frame.setMaximumWidth(120)
        self.git_tab_frame = LauncherWindow.create_default_frame("GitTabFrame")
        self.pv4_tab_frame = LauncherWindow.create_default_frame("Pv4TabFrame")
        self.body_tap = QTabWidget()
        self.body_tap.setObjectName("MainWindowTabs")
        """ Custom Widgets """
        self.git_tab = UIGitTab(self.config["general"]["working_path"])
        self.pv4_tab = UIGitTab(self.config["general"]["working_path"])
        self.git_tab.setObjectName("GitTab")
        self.pv4_tab.setObjectName("PV4Tab")
        self.logger_widget = LoggerWidget()
        self.user_session_widget = UserSessionWidget()

    def _apply_styles(self):
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.maya_btn, "Black")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.new_workspace_btn, "Black")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.settings_btn, "Black")
        CustomStyleSheetApplier.set_combo_box_style_and_colour(self.combo_box, "White")
        self.user_menu.setFont(QFont("Courier New", 10))

    def _build(self):
        """ Connect Button """
        self.connect_button = self.create_button(self, "singleplayer.png", "Connect")
        self.connect_button.setObjectName("ConnectButton")
        """ Header """
        self.header_layout.addWidget(self.loading, 0, Qt.AlignmentFlag.AlignRight)
        self.header_layout.setSpacing(0)
        """ Body left """
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.left_frame.setLayout(self.body_left)
        self.left_frame.layout().addWidget(self.combo_box, 0, Qt.AlignmentFlag.AlignTop)
        self.left_frame.layout().addWidget(separator)
        self.left_frame.layout().addWidget(self.new_workspace_btn, 0, Qt.AlignmentFlag.AlignTop)
        self.left_frame.layout().addWidget(self.maya_btn, 0, Qt.AlignmentFlag.AlignTop)
        self.left_frame.layout().addWidget(self.settings_btn, 5, Qt.AlignmentFlag.AlignTop)
        self.left_frame.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        """ Tabs """
        git_tab_layout = QVBoxLayout()
        self.git_tab_frame.setLayout(git_tab_layout)
        self.git_tab_frame.layout().addWidget(self.git_tab)
        self.git_tab_frame.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_tap.addTab(self.git_tab_frame, "Git")

        pv4_tab_layout = QVBoxLayout()
        self.pv4_tab_frame.setLayout(pv4_tab_layout)
        self.pv4_tab_frame.layout().addWidget(self.pv4_tab)
        self.pv4_tab_frame.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_tap.addTab(self.pv4_tab_frame, "PV4")
        """ Body Right """
        self.body_right.addWidget(self.body_tap, 0)
        self.body_right.addWidget(self.logger_widget, 5)
        """ Nesting Layouts """
        self.body_layout.addWidget(self.left_frame, 1)
        self.body_layout.addLayout(self.body_right, 6)
        self.body_layout.setSpacing(10)
        """ Main Layout """
        self.main_layout.addLayout(self.body_layout, 1, 0)
        self.main_layout.addLayout(self.footer_layout, 2, 0)
        self.main_layout.addLayout(self.header_layout, 3, 0)
        self.main_layout.setSpacing(2)
        """ Menubar """
        self.menuBar().setObjectName("LauncherUserMenu")
        self.menuBar().addMenu(self.user_menu)
        self.menuBar().addSeparator()
        """ Set Main Layout """
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def show(self):
        super().show()
        self.layout().update()

    def set_project_combo_box(self):
        for project in self.config["projects"]["projects"]:
            action = self.create_project_action(project)
            self.project_combo_box_actions[project] = action
            self.combo_box.addItem(project)

    def create_project_action(self, project_id):
        project_action = QAction(project_id)
        project_action.triggered.connect(lambda action: self.project_selected_changed(project_id))
        return project_action

    def _connect_signals(self):
        self.git_tab.upload_btn.clicked.connect(self, self.create_commit_windows)
        self.git_tab.download_btn.clicked.connect(self.on_get_latest_clicked)
        self.user_session_widget.logout_signal = self.login_out

    def on_get_latest_clicked(self):
        if len(self.git_tab.git_sniffer.changes) == 0:
            self.get_latest.emit()
            return

        message_box = QMessageBox()
        message_box.setWindowTitle("Confirm")
        message_box.setIcon(QMessageBox.Information)
        message_box.setText("You are going to lose your changes. are you sure to get latest?")
        message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        message_box.setDefaultButton(QMessageBox.Ok)

        reply = message_box.exec()

        if reply == QMessageBox.Ok:
            self.get_latest.emit()

    def create_commit_windows(self):
        self.commit_window = CommitWindow()
        self.commit_window.accept_clicked_signal.connect(self._on_commit_window_accept)
        self.commit_window.cancel_clicked_signal.connect(self._on_commit_window_cancel)
        self.commit_window.show()

    def set_user_session(self, user_session: UserSession):
        self.user_session = user_session
        self.user_session_widget.set_user()
        self.set_user_buttons()
        self.user_menu.setTitle(self.user_session.username)

    def set_user_buttons(self):
        if self.user_session.role_id == Env.ROLE_ID.ANIMATOR.value:
            self.set_animator()

        if self.user_session.role_id == Env.ROLE_ID.DEV.value:
            self.set_dev_user()

        if self.user_session.role_id == Env.ROLE_ID.ADMIN.value:
            self.set_admin_user()

    def set_animator(self):
        self.git_tab.upload_btn.hide()
        self.git_tab.git_sniffer.hide()
        self.build_session_menu()

    def set_dev_user(self):
        self.git_tab.git_sniffer.merge_request.accept_btn.hide()
        self.git_tab.git_sniffer.show()
        self.build_session_menu()

    def set_admin_user(self):
        self.git_tab.upload_btn.show()
        self.git_tab.git_sniffer.show()
        self.build_session_menu()

    def add_username(self, message) -> str:
        if self.user_session is None:
            self.user_session = UserSession()

        return f"[{self.user_session.username}]:: {message}"

    def build_session_menu(self):
        self.user_menu.clear()
        self.user_menu.addAction(self.user_session_widget.user_action)
        self.user_menu.addAction(self.user_session_widget.logout_action)

        if self.user_session.role_id == ROLE_ID.ADMIN.value:
            self.user_session_widget.admin_signal.connect(self.create_admin_window)
            self.user_menu.addAction(self.user_session_widget.get_admin_action())

    def create_admin_window(self):
        if self.admin_window is None:
            self.admin_window = AdminWindow()

        self.admin_window.show()

    def _close_commit_window(self):
        if self.commit_window is not None:
            self.commit_window.close()
            self.commit_window = None

    def on_setup_completed(self, success: bool):
        self.git_tab.on_repository_path_updated()

    def project_selected_changed(self, project_id):
        return

    def create_project_item(self, project_id):
        return

    @Slot(str)
    def _on_commit_window_accept(self, message):
        self.upload_repository_signal.emit(self.add_username(message))
        self._close_commit_window()

    @Slot()
    def _on_commit_window_cancel(self):
        self._close_commit_window()

    @Slot(str)
    def _on_get_main_branch(self, main_branch):
        return

    @Slot(list)
    def _on_get_all_branch(self, branches):
        return
