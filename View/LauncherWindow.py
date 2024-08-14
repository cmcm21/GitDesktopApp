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
    QMessageBox,
    QPushButton
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
    upload_repository = Signal(str)
    get_latest = Signal()
    publish_to_anim_rep = Signal(str)
    project_changed = Signal(str)
    window_closed = Signal()
    login_out = Signal()
    admin_window_clicked = Signal()
    check_changes_list = Signal()

    def __init__(self, config: dict, window_id: WindowID, width=900, height=500):
        super().__init__("Puppet Launcher", window_id, width, height)
        self.admin_window = None
        self.user_session = None
        self.commit_window = None
        self.publish_window = None
        self.config = config
        self._initialize_attributes()
        self._create_all_elements()
        self._apply_styles()
        self._build_layouts()
        self._connect_signals()

    def _initialize_attributes(self):
        self.user_session: UserSession = None
        self.project_combo_box_actions = {}
        self.admin_window = None
        self.commit_window = None
        self.publish_window = None

    def _create_all_elements(self):
        self._create_layouts()
        self._create_buttons()
        self._create_frames()
        self._create_tabs()
        self._create_misc_widgets()

    def _create_layouts(self):
        self.main_layout = QGridLayout()
        self.header_layout = QHBoxLayout()
        self.body_layout = QHBoxLayout()
        self.body_left = QVBoxLayout()
        self.body_right = QVBoxLayout()
        self.footer_layout = QHBoxLayout()

    def _create_buttons(self):
        self.combo_box = QComboBox(self)
        self.user_menu = QMenu("User", self)
        self.set_project_combo_box()

        self.new_workspace_btn = self._create_button("plus.png", "NewWorkspaceButton", "New Workspace")
        self.maya_btn = self._create_button("mayaico.png", "MayaButton", "Open Maya")
        self.settings_btn = self._create_button("gear.png", "SettingsButton", "Open Settings")

    def _create_button(self, icon_path: str, object_name: str, tooltip: str) -> QPushButton:
        button = self.create_button(self, icon_path, "")
        button.setToolTip(tooltip)
        button.setObjectName(object_name)
        button.setFixedSize(QSize(80, 40))
        return button

    def _create_frames(self):
        self.left_frame = self._create_frame("MainWindowLeftFrame", max_width=120)
        self.git_tab_frame = self._create_frame("GitTabFrame")
        self.pv4_tab_frame = self._create_frame("Pv4TabFrame")

    @staticmethod
    def _create_frame(object_name: str, max_width: int = None) -> QFrame:
        frame = LauncherWindow.create_default_frame(object_name)
        if max_width:
            frame.setMaximumWidth(max_width)
        return frame

    def _create_tabs(self):
        self.body_tap = QTabWidget()
        self.body_tap.setObjectName("MainWindowTabs")

        self.git_tab = UIGitTab(self.config["general"]["working_path"])
        self.git_tab.setObjectName("GitTab")
        self._add_tab(self.git_tab_frame, self.git_tab, "Git")

        self.pv4_tab = UIGitTab(self.config["general"]["working_path"])
        self.pv4_tab.setObjectName("PV4Tab")
        self._add_tab(self.pv4_tab_frame, self.pv4_tab, "PV4")

    def _add_tab(self, frame: QFrame, widget: QWidget, title: str):
        layout = QVBoxLayout()
        frame.setLayout(layout)
        layout.addWidget(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_tap.addTab(frame, title)

    def _create_misc_widgets(self):
        self.logger_widget = LoggerWidget()
        self.user_session_widget = UserSessionWidget()

    def _apply_styles(self):
        self._set_button_style(self.maya_btn)
        self._set_button_style(self.new_workspace_btn)
        self._set_button_style(self.settings_btn)
        CustomStyleSheetApplier.set_combo_box_style_and_colour(self.combo_box, "White")
        self.user_menu.setFont(QFont("Courier New", 10))

    @staticmethod
    def _set_button_style(button: QPushButton):
        CustomStyleSheetApplier.set_buttons_style_and_colour(button, "Black")

    def _build_layouts(self):
        self._build_header()
        self._build_body_left()
        self._build_body_right()
        self._nest_layouts()
        self._build_menubar()

        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def _build_header(self):
        self.connect_button = self._create_button("singleplayer.png", "ConnectButton", "Connect")
        self.header_layout.addWidget(self.loading, 0, Qt.AlignmentFlag.AlignRight)
        self.header_layout.setSpacing(0)

    def _build_body_left(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        self.left_frame.setLayout(self.body_left)
        layout = self.left_frame.layout()
        layout.addWidget(self.combo_box, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(separator)
        layout.addWidget(self.new_workspace_btn, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.maya_btn, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.settings_btn, 5, Qt.AlignmentFlag.AlignTop)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _build_body_right(self):
        self.body_right.addWidget(self.body_tap, 0)
        self.body_right.addWidget(self.logger_widget, 5)

    def _nest_layouts(self):
        self.body_layout.addWidget(self.left_frame, 1)
        self.body_layout.addLayout(self.body_right, 6)
        self.body_layout.setSpacing(10)
        self.main_layout.addLayout(self.body_layout, 1, 0)
        self.main_layout.addLayout(self.footer_layout, 2, 0)
        self.main_layout.addLayout(self.header_layout, 3, 0)
        self.main_layout.setSpacing(2)

    def _build_menubar(self):
        self.menuBar().setObjectName("LauncherUserMenu")
        self.menuBar().addMenu(self.user_menu)
        self.menuBar().addSeparator()

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
        self.git_tab.upload_btn.clicked.connect(self.create_commit_windows)
        self.git_tab.download_btn.clicked.connect(self.on_get_latest_clicked)
        self.git_tab.publish_btn.clicked.connect(self.create_publish_window)
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

    def create_publish_window(self):
        self.publish_window = CommitWindow(" Publish current scripts ", "Add a publish comment")
        self.publish_window.accept_clicked_signal.connect(self._on_publish_window_accept)
        self.publish_window.cancel_clicked_signal.connect(self._on_publish_window_cancel)
        self.publish_window.show()

    def create_commit_windows(self):
        self.commit_window = CommitWindow(" Commit Windows")
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
        self.git_tab.show_anim_tab()
        self.git_tab.publish_btn.hide()
        self.build_session_menu()

    def set_dev_user(self):
        self.git_tab.git_sniffer.merge_request.accept_btn.hide()
        self.git_tab.hide_anim_tab()
        self.git_tab.publish_btn.show()
        self.git_tab.upload_btn.show()
        self.build_session_menu()

    def set_admin_user(self):
        self.git_tab.upload_btn.show()
        self.git_tab.hide_anim_tab()
        self.git_tab.upload_btn.show()
        self.git_tab.publish_btn.show()
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

    def _close_publish_window(self):
        if self.publish_window is not None:
            self.publish_window.close()
            self.publish_window = None

    def on_setup_completed(self, success: bool):
        self.git_tab.on_repository_path_updated()

    @Slot(str)
    def _on_commit_window_accept(self, message):
        self.upload_repository.emit(self.add_username(message))
        self._close_commit_window()

    @Slot()
    def _on_commit_window_cancel(self):
        self._close_commit_window()

    @Slot(str)
    def _on_publish_window_accept(self, message):
        self.publish_to_anim_rep.emit(self.add_username(message))
        self._close_publish_window()

    @Slot()
    def _on_publish_window_cancel(self):
        self._close_publish_window()

    @Slot(str)
    def _on_get_main_branch(self, main_branch):
        return

    @Slot(list)
    def _on_get_all_branch(self, branches):
        return

    def project_selected_changed(self, project_id):
        return

    def create_project_item(self, project_id):
        return
