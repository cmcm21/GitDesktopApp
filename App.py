from PySide6.QtWidgets import QApplication
from View.UIManager import UIManager
from View.UIManager import WindowID
from Controller.GitController import GitController
from Controller.SystemController import SystemController
from PySide6.QtCore import QThread, Signal, Slot
from Utils.DataBaseManager import DataBaseManager
from Utils.UserSession import UserSession
import tomli
import os


def get_config() -> dict:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir,  "configFile.toml")
    with open(config_file_path, "rb") as config_file:
        config = tomli.load(config_file)

    return config


class Application(QApplication):

    git_setup = Signal()
    check_user_branch = Signal()
    system_controller_setup = Signal()
    db_setup = Signal()

    def __init__(self):
        super().__init__([])
        """ Control variables """
        self._set_style_sheet()
        self.config = get_config()
        self.ui_manager = UIManager(self.config)
        self.logger = self.ui_manager.logger
        self.git_installed = False
        self.user_session = UserSession()
        """ Create objects threads"""
        self._create_git_controller_thread()
        self._create_system_controller_thread()
        self._create_db_manager_thread()
        """ Connect objects signals """
        self._connect_ui_manager()
        self._connect_git_controller()
        self._connect_system_controller()
        self._connect_db_manager()

    def _create_git_controller_thread(self):
        """ Git controller thread creation"""
        self.git_controller_thread = QThread(self)
        self.git_controller = GitController(self.config)
        """ Git controller setup """
        self.git_controller.setup_completed.connect(self.ui_manager.on_setup_completed)
        self.git_setup.connect(self.git_controller.setup)
        self.check_user_branch.connect(self.git_controller.verify_user_branch)
        """ Move git controller to its own thread"""
        self.git_controller.moveToThread(self.git_controller_thread)
        """ Git controller start thread """
        self.git_controller_thread.start()

    def _create_system_controller_thread(self):
        """Create system controller thread"""
        self.system_controller_thread = QThread(self)
        """ Create system controller"""
        self.system_controller = SystemController(self.config)
        """ Move System controller to its own thread"""
        self.system_controller.moveToThread(self.system_controller_thread)
        """ Start Thread """
        self.system_controller_thread.start()

    def _create_db_manager_thread(self):
        """ Create db manager """
        self.db_manager_thread = QThread(self)
        """ Create db manager """
        self.db_manager = DataBaseManager(self.config)
        """ Move db manager to its own thread"""
        self.db_manager.moveToThread(self.db_manager_thread)
        """ Start db manager thread"""
        self.db_manager_thread.start()

    def _connect_ui_manager(self):
        self._connect_ui_manager_launcher()
        self._connect_ui_manager_login()

    def _connect_ui_manager_launcher(self):
        self.ui_manager.lw_window_closed.connect(self.on_main_window_closed)
        self.ui_manager.lw_git_merge_request_tab_clicked.connect(self.git_controller.get_main_branch)
        self.ui_manager.lw_git_merge_request_tab_clicked.connect(self.git_controller.get_all_branches)
        self.ui_manager.lw_git_merge_request_tab_clicked.connect(self.git_controller.load_merge_requests)
        self.ui_manager.lw_get_latest_clicked.connect(self.git_controller.get_latest)
        self.ui_manager.lw_uploaded_clicked.connect(self.git_controller.push_changes)
        self.ui_manager.lw_open_maya_clicked.connect(self.system_controller.open_maya)
        self.ui_manager.lw_get_merge_request_changed.connect(self.git_controller.get_merge_request_commits)
        self.ui_manager.lw_get_merge_request_changed.connect(self.git_controller.get_merge_request_changes)
        self.ui_manager.lw_get_merge_request_changed.connect(self.git_controller.get_merge_requests_comments)
        self.ui_manager.lw_merge_request_add_comment.connect(self.git_controller.merge_request_add_comment)
        self.ui_manager.lw_accept_merge_request_and_merge.connect(self.git_controller.merge_request_accept_and_merge)

    def _connect_ui_manager_login(self):
        self.ui_manager.lg_login_accepted.connect(self.login_accepted)

    def _connect_git_controller(self):
        self.git_controller.setup_started.connect(self.ui_manager.on_git_setup_started)
        self.git_controller.setup_completed.connect(self.on_git_setup_completed)
        self.git_controller.push_completed.connect(self.ui_manager.on_upload_completed)
        self.git_controller.get_latest_completed.connect(self.ui_manager.on_get_latest_completed)
        self.git_controller.log_message.connect(self.ui_manager.on_log_signal_received)
        self.git_controller.error_message.connect(self.ui_manager.on_err_signal_received)
        self.git_controller.send_main_branch.connect(self.ui_manager.on_get_main_branch)
        self.git_controller.send_all_branches.connect(self.ui_manager.on_get_all_branches)
        self.git_controller.send_merge_requests.connect(self.ui_manager.on_get_all_merge_requests)
        self.git_controller.send_merge_request_commits.connect(self.ui_manager.on_get_merge_request_commits)
        self.git_controller.send_merge_requests_changes.connect(self.ui_manager.on_get_merge_request_changes)
        self.git_controller.send_merge_requests_comments.connect(self.ui_manager.on_get_merge_requests_comments)

    def _connect_system_controller(self):
        self.system_controller.setup_started.connect(self.ui_manager.on_system_controller_setup_started)
        self.system_controller.log_message.connect(self.ui_manager.on_log_signal_received)
        self.system_controller.error_message.connect(self.ui_manager.on_err_signal_received)
        self.system_controller.maya_checked.connect(self.ui_manager.on_maya_checked)
        self.system_controller.git_checked.connect(self.on_git_checked)
        self.system_controller.git_installed.connect(self.on_git_installed)
        self.system_controller.setup_finished.connect(self.on_system_controller_setup_finished)
        self.system_controller_setup.connect(self.system_controller.setup)

    def _connect_db_manager(self):
        self.db_manager.message_signal.connect(self.ui_manager.on_log_signal_received)
        self.db_manager.error_message_signal.connect(self.ui_manager.on_err_signal_received)
        self.db_manager.db_setup_start.connect(self.ui_manager.on_db_setup_start)
        self.db_manager.db_setup_done.connect(self.ui_manager.on_db_setup_done)
        self.db_setup.connect(self.db_manager.setup_db)

    @Slot(str)
    def login_accepted(self, username: str):
        self.user_session.login(username)
        self.ui_manager.launcher_window.set_user_session(self.user_session)
        self.ui_manager.open_window(WindowID.LAUNCHER)
        self.system_controller_setup.emit()

    @Slot()
    def on_system_controller_setup_finished(self):
        if self.git_installed:
            self.git_setup.emit()

    @Slot(bool)
    def on_git_checked(self, success: bool):
        self.git_installed = success

    @Slot(bool)
    def on_git_installed(self, success: bool):
        if self.git_installed:
            return

        self.git_installed = success
        if self.git_installed:
            self.git_setup.emit()

    def on_git_setup_completed(self, success: bool):
        self.check_user_branch.emit()

    def _set_style_sheet(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dark_theme_path = os.path.join(script_dir, "./View/", "appStyle.qss")
        with open(dark_theme_path, "r") as file:
            qss = file.read()
            self.setStyleSheet(qss)

    @Slot()
    def on_main_window_closed(self):
        if self.system_controller_thread is not None:
            self.system_controller_thread.exit()
        if self.git_controller_thread is not None:
            self.git_controller_thread.exit()
        self.ui_manager.current_window.loading.stop_anim_screen()
        self.__del__()

    def run(self):
        self.ui_manager.open_window(WindowID.LOGING)
        self.db_setup.emit()
        self.exec()

    def __del__(self):
        return
