from PySide6.QtCore import Qt, Signal, Slot, QSize, QPoint
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
    QPushButton,
)
from Utils.ConfigFileManager import ConfigFileManager
from View import CustomStyleSheetApplier
from View.BaseWindow import BaseWindow
from View.WindowID import WindowID
from View.UILogger import LoggerWidget
from View.UIGitTab import UIGitTab
from View.UISessionWidget import UserSessionWidget
from View.UIAdminWidget import AdminWindow
from View.UISettingsWindows import SettingWindows
from View.PublishWindow import PublishWindow
from View.CustomSplitter import CustomSplitter
from Utils.UserSession import UserSession
from Utils.Environment import RoleID
from Utils.SignalManager import SignalManager
from View.UILoadingWindow import LoadingWindows
import Utils.Environment as Env


class LauncherWindow(BaseWindow):
    push_and_commit = Signal(str, list)
    publish_to_anim_rep = Signal(str, list)
    get_latest = Signal()
    reset_changes = Signal()
    project_changed = Signal(str)
    window_closed = Signal()
    admin_window_clicked = Signal()
    public_to_anim = Signal
    switch_account = Signal(RoleID)
    refresh_signal = Signal()
    log_out = Signal()
    open_maya = Signal()

    def __init__(self, window_id: WindowID, width=900, height=500):
        super().__init__("Puppet Launcher", window_id, width, height)
        self.loading_window = None
        self.admin_window = None
        self.user_session = None
        self.publish_window = None
        self.settings_window = None

        self.config_manager = ConfigFileManager()
        self.config = self.config_manager.get_config()

        self._initialize_attributes()
        self._create_all_elements()
        self._apply_styles()
        self._build_layouts()
        self._connect_signals()

    def _initialize_attributes(self):
        self.user_session = None
        self.project_combo_box_actions = {}
        self.admin_window = None
        self.loading_window = None
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
        self.loading_layout = QHBoxLayout()
        self.body_layout = QHBoxLayout()
        self.body_left = QVBoxLayout()
        self.body_right = QVBoxLayout()

    def _create_buttons(self):
        self.combo_box = QComboBox(self)
        self.user_menu = QMenu("User", self)
        self.set_project_combo_box()

        #self.new_workspace_btn = self._create_button("plus.png", "NewWorkspaceButton", "New Workspace")
        self._maya_btn = self._create_button("mayaico.png", "MayaButton", "Open Maya")
        self._maya_btn.clicked.connect(lambda: self.open_maya.emit())

        self._refresh_btn = self._create_button("refresh.png", "RefreshButton", "Refresh")
        self._refresh_btn.clicked.connect(self.refresh_clicked)
        self._refresh_btn.setIconSize(QSize(32, 32))

        self._settings_btn = self._create_button("gear.png", "SettingsButton", "Open Settings")
        self._settings_btn.clicked.connect(self.open_settings)

    @property
    def maya_btn(self):
        return self._maya_btn

    @property
    def refresh_btn(self):
        return self._refresh_btn

    @property
    def settings_btn(self):
        return self._settings_btn

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

    def refresh_clicked(self):
        if self.throw_message_box("Reload", "Are you sure to Reload window?", self):
            self.refresh_signal.emit()

    def open_settings(self):
        self.settings_window = SettingWindows(WindowID.SETTINGS, self.logger_widget)
        SignalManager.connect_signal(self.settings_window, self.settings_window.window_closed, self.settings_closed)
        self.settings_window.show()

    @Slot()
    def settings_closed(self):
        return

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

        self.pv4_tab = QWidget()
        self.pv4_tab.setObjectName("PV4Tab")
        self._add_tab(self.pv4_tab_frame, self.pv4_tab, "PV4")

    def _add_tab(self, frame: QFrame, widget: QWidget, title: str):
        layout = QVBoxLayout()
        frame.setLayout(layout)
        layout.addWidget(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_tap.addTab(frame, title)

    def _create_misc_widgets(self):
        self.splitter = CustomSplitter(Qt.Orientation.Vertical)
        self.logger_widget = LoggerWidget()
        self.user_session_widget = UserSessionWidget()

    def _apply_styles(self):
        # self._set_button_style(self.new_workspace_btn)
        CustomStyleSheetApplier.set_buttons_style_and_colour(self._maya_btn, "Black")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self._settings_btn, "Black")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self._refresh_btn, "Black")
        CustomStyleSheetApplier.set_combo_box_style_and_colour(self.combo_box, "White")
        self.user_menu.setFont(QFont("Courier New", 10))

    def _build_layouts(self):
        self._build_header()
        self._build_body_left()
        self._build_body_right()
        self._build_main_layout()
        self._build_menu_bar()

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

    def _build_header(self):
        self.loading_layout.addWidget(self.loading, 0, Qt.AlignmentFlag.AlignRight)
        self.loading_layout.setSpacing(0)

    def _build_body_left(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.left_frame.setLayout(self.body_left)
        layout = self.left_frame.layout()
        layout.addWidget(self.combo_box, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(separator)
       # layout.addWidget(self.new_workspace_btn, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self._maya_btn, 5, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self._refresh_btn, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self._settings_btn, 0, Qt.AlignmentFlag.AlignBottom)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _build_body_right(self):
        self.splitter.addWidget(self.body_tap)
        self.splitter.addWidget(self.logger_widget)
        self.body_right.addWidget(self.splitter)
        self.body_right.setContentsMargins(0, 0, 0, 0)

    def _build_main_layout(self):
        self.body_layout.addWidget(self.left_frame, 1)
        self.body_layout.addLayout(self.body_right, 6)

        self.main_layout.addLayout(self.body_layout, 1, 0)
        self.main_layout.addLayout(self.loading_layout, 3, 0)

        self.main_layout.setSpacing(2)

    def _build_menu_bar(self):
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

    def project_selected_changed(self, project_id):
        return

    def _connect_signals(self):
        self.git_tab.git_sniffer.push_and_commit_clicked.connect(self.on_git_commit_and_push)
        self.git_tab.get_latest_clicked.connect(self.on_get_latest_clicked)
        self.git_tab.publish_clicked.connect(self.create_publish_window)
        self.git_tab.reset_clicked.connect(self.on_reset_changes_clicked)
        self.user_session_widget.logout_signal.connect(self._log_out)

    def _log_out(self):
        self.log_out.emit()

    def on_get_latest_clicked(self):
        if len(self.git_tab.git_sniffer.changes) == 0:
            self.get_latest.emit()
            return

        if (self.throw_message_box("Confirm get latest",
                               "You're going to lose your changes. Are you Sure to Get Latest?"), self):
            self.get_latest.emit()

    def create_publish_window(self):
        self.publish_window = PublishWindow(" Publish to animator repository ", "Add a publish comment")
        self.publish_window.compile_all_signal.connect(
            lambda message: self._on_publish_window_accept(message, []))

        # In order to get the changes and disable/enable publish changes button
        self.git_tab.changes_list_clicked.emit()
        self.publish_window.cancel_signal.connect(self._on_publish_window_cancel)
        self.publish_window.show()

    def on_reset_changes_clicked(self):
        if self.throw_message_box("Reset changes", "Are you sure to reset everything?", self):
            self.reset_changes.emit()

    def on_git_commit_and_push(self, message, changes):
        if self.throw_message_box("Commit and Push", "Are you sure to commit and push changes?", self):
            self.push_and_commit.emit(self.add_username(message), changes)

    def set_user_session(self, user_session: UserSession):
        self.user_session = user_session
        self.user_session_widget.set_user()
        self.set_user_buttons()
        self.user_menu.setTitle(f"{self.user_session.username} ( {self.user_session.role} )")

    def set_user_buttons(self):
        if (self.user_session.role_id == Env.RoleID.ANIMATOR.value or
                self.user_session.role_id == Env.RoleID.ADMIN_ANIM.value):
            self.set_animator()

        if self.user_session.role_id == Env.RoleID.DEV.value:
            self.set_dev_user()

        if self.user_session.role_id == Env.RoleID.ADMIN.value:
            self.set_admin_user()

    def set_animator(self):
        self.git_tab.show_anim_tab()
        self.git_tab.publish_btn.hide()
        self.build_session_menu()

    def set_dev_user(self):
        self.git_tab.git_sniffer.merge_request.accept_btn.hide()
        self.git_tab.hide_anim_tab()
        self.git_tab.publish_btn.hide()
        self.build_session_menu()

    def set_admin_user(self):
        self.git_tab.hide_anim_tab()
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

        if self.user_session.role_id == RoleID.ADMIN.value or self.user_session.role_id == RoleID.ADMIN_ANIM.value:
            self.user_session_widget.admin_signal.connect(self.on_create_admin_window)

            # noinspection PyTypeChecker
            SignalManager.connect_signal(self.user_session_widget,
                                         self.user_session_widget.switch_account_signal, self.on_switch_account)

            self.user_menu.addAction(self.user_session_widget.get_admin_action())
            self.user_menu.addAction(self.user_session_widget.get_switch_account_action())

    def on_create_admin_window(self):
        if self.admin_window is None:
            self.admin_window = AdminWindow()

        self.admin_window.show()

    @Slot(RoleID)
    def on_switch_account(self, role: RoleID):
        message_box = QMessageBox()
        message_box.setWindowTitle("Switch Roles")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText("Are you sure to switch roles?")
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        message_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        reply = message_box.exec()

        if reply == QMessageBox.StandardButton.Ok:
            # noinspection PyTypeChecker
            SignalManager.disconnect_signal(self.user_session_widget,
                                            self.user_session_widget.switch_account_signal, self.on_switch_account)
            self.switch_account.emit(role)

    def _close_commit_window(self):
        if self.commit_window is not None:
            self.commit_window.close()
            self.commit_window = None

    def _close_publish_window(self):
        if self.publish_window is not None:
            self.publish_window.close()
            self.publish_window = None

    def on_setup_completed(self, success: bool, path: str):
        self.git_tab.on_repository_path_updated(path)

    def on_push_and_commit_completed(self, message, changes):
        if self.user_session.role_id == RoleID.ADMIN.value:
            if self.throw_message_box("Animator repository", "Would you like to publish to animators", self):
                self.publish_to_anim_rep.emit(message, changes)

    @Slot(str)
    def _on_commit_window_accept(self, message):
        self.push_and_commit.emit(self.add_username(message))
        self._close_commit_window()

    @Slot()
    def _on_commit_window_cancel(self):
        self._close_commit_window()

    @Slot(str)
    def _on_publish_window_accept(self, message, compile_all):
        self.publish_to_anim_rep.emit(self.add_username(message), compile_all)
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

    def create_project_item(self, project_id):
        return

    def disable_window(self, value: bool):
        self.setDisabled(value)
        self.logger_widget.setDisabled(False)

    def start_loading_process(self):
        if self.loading_window is not None:
            return

        self.loading.show_anim_screen()

    def stop_loading_process(self):
        self.loading.stop_anim_screen()

    def long_process_started(self):
        if self.loading_window is None:
            self.loading_window = LoadingWindows(self)

            self.loading_window.close_event.connect(self._on_loading_windows_close_event)
            self.loading_window.start()
            self.loading_window.setWindowModality(Qt.WindowModality.WindowModal)
            self.loading_window.show()

    def long_process_ended(self):
        if self.loading_window is None:
            return

        self.loading_window.stop()
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Confirmation")
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setText("Process Completed!!")
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        reply = message_box.exec()

    def _on_loading_windows_close_event(self):
        if self.loading_window is not None:
            self.loading_window.close()
            self.loading_window = None

