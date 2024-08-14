from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QMetaMethod
from View.UIManager import UIManager
from View.UIManager import WindowID
from Controller.GitController import GitController
from Controller.SystemController import SystemController
from PySide6.QtCore import QThread, Signal, Slot
from Utils.DataBaseManager import DataBaseManager
from Utils.UserSession import UserSession
from Utils.Environment import ROLE_ID
from Utils.SignalManager import SignalManager
from Controller.AnimatorGitController import AnimatorGitController
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
    git_animator_setup = Signal()
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
        """ Create objects threads """
        self._create_git_controller_thread()
        self._create_system_controller_thread()
        self._create_db_manager_thread()
        self._create_git_animator_controller()
        """ Connect objects signals """
        self._connect_ui_manager()
        self._connect_git_controller()
        self._connect_system_controller()
        self._connect_db_manager()

    def _create_git_controller_thread(self):
        """ Git controller thread creation """
        self.git_controller_thread = QThread(self)
        self.git_controller = GitController(self.config)
        """ Git controller setup """
        self.git_controller.setup_completed.connect(self.ui_manager.on_setup_completed)

        SignalManager.connect_signal(self, self.git_setup, self.git_controller.setup)
        SignalManager.connect_signal(self, self.check_user_branch, self.git_controller.verify_user_branch)

        """ Move git controller to its own thread """
        self.git_controller.moveToThread(self.git_controller_thread)
        """ Git controller start thread """
        self.git_controller_thread.start()

    def _create_system_controller_thread(self):
        """ Create system controller thread """
        self.system_controller_thread = QThread(self)
        """ Create system controller """
        self.system_controller = SystemController(self.config)
        """ Move System controller to its own thread """
        self.system_controller.moveToThread(self.system_controller_thread)
        """ Start Thread """
        self.system_controller_thread.start()

    def _create_db_manager_thread(self):
        """ Create db manager """
        self.db_manager_thread = QThread(self)
        """ Create db manager """
        self.db_manager = DataBaseManager(self.config)
        """ Move db manager to its own thread """
        self.db_manager.moveToThread(self.db_manager_thread)
        """ Start db manager thread """
        self.db_manager_thread.start()

    def _create_git_animator_controller(self):
        """ Create git controller thread"""
        self.anim_git_controller_thread = QThread(self)
        """ Create anim git controller """
        self.anim_git_controller = AnimatorGitController(self.config)
        SignalManager.connect_signal(self, self.git_animator_setup, self.anim_git_controller.setup)
        SignalManager.connect_signal(self, self.check_user_branch, self.anim_git_controller.verify_user_branch)
        """ Move anim git controller to thread """
        self.anim_git_controller.moveToThread(self.anim_git_controller_thread)
        """ Start Thread """
        self.anim_git_controller_thread.start()

    def _connect_ui_manager(self):
        self._connect_ui_manager_launcher()
        self._connect_ui_manager_git_controller()
        self._connect_ui_manager_login()

    def _connect_ui_manager_launcher(self):
        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_window_closed,
                                     self.on_main_window_closed)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_login_out,
                                     self.on_login_out)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_open_maya_clicked,
                                     self.system_controller.open_maya)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_destroy_application,
                                     self.on_application_destroyed)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lg_destroy_application,
                                     self.on_application_destroyed)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_file_tree_clicked,
                                     self.system_controller.open_file)

    def _connect_ui_manager_git_controller(self):
        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_git_merge_request_tab_clicked,
                                     self.git_controller.get_main_branch)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_git_merge_request_tab_clicked,
                                     self.git_controller.get_all_branches)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_git_merge_request_tab_clicked,
                                     self.git_controller.load_merge_requests)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_get_merge_request_changed,
                                     self.git_controller.get_merge_request_commits)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_get_merge_request_changed,
                                     self.git_controller.get_merge_request_changes)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_get_merge_request_changed,
                                     self.git_controller.get_merge_requests_comments)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_merge_request_add_comment,
                                     self.git_controller.merge_request_add_comment)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_accept_merge_request_and_merge,
                                     self.git_controller.merge_request_accept_and_merge)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_get_latest_clicked,
                                     self.git_controller.get_latest)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_uploaded_clicked,
                                     self.git_controller.push_changes)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_git_history_tab_clicked,
                                     self.git_controller.get_repository_history)

        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_git_changes_list_tab_clicked,
                                     self.git_controller.get_repository_changes)

    def _connect_ui_manager_login(self):
        SignalManager.connect_signal(self.ui_manager, self.ui_manager.lg_login_accepted, self.login_accepted)

    def _connect_git_controller(self):
        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.setup_completed,
                                     self.on_git_setup_completed)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.setup_completed,
                                     self.anim_git_controller.on_git_setup_completed)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.setup_started,
                                     self.ui_manager.on_git_setup_started)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.push_completed,
                                     self.ui_manager.on_upload_completed)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.get_latest_completed,
                                     self.ui_manager.on_get_latest_completed)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.log_message,
                                     self.ui_manager.on_log_signal_received)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.error_message,
                                     self.ui_manager.on_err_signal_received)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.send_main_branch,
                                     self.ui_manager.on_get_main_branch)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.send_all_branches,
                                     self.ui_manager.on_get_all_branches)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.send_merge_requests,
                                     self.ui_manager.on_get_all_merge_requests)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.send_merge_request_commits,
                                     self.ui_manager.on_get_merge_request_commits)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.send_merge_requests_changes,
                                     self.ui_manager.on_get_merge_request_changes)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.send_merge_requests_comments,
                                     self.ui_manager.on_get_merge_requests_comments)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.send_repository_history,
                                     self.ui_manager.on_get_repository_history)

        SignalManager.connect_signal(self.git_controller,
                                     self.git_controller.send_current_changes,
                                     self.ui_manager.on_get_changes_list)

    def _connect_system_controller(self):
        SignalManager.connect_signal(self.system_controller,
                                     self.system_controller.setup_started,
                                     self.ui_manager.on_system_controller_setup_started)

        SignalManager.connect_signal(self.system_controller,
                                     self.system_controller.log_message,
                                     self.ui_manager.on_log_signal_received)

        SignalManager.connect_signal(self.system_controller,
                                     self.system_controller.error_message,
                                     self.ui_manager.on_err_signal_received)

        SignalManager.connect_signal(self.system_controller,
                                     self.system_controller.maya_checked,
                                     self.ui_manager.on_maya_checked)

        SignalManager.connect_signal(self.system_controller,
                                     self.system_controller.git_checked,
                                     self.on_git_checked)

        SignalManager.connect_signal(self.system_controller,
                                     self.system_controller.git_installed,
                                     self.on_git_installed)

        SignalManager.connect_signal(self.system_controller,
                                     self.system_controller.setup_finished,
                                     self.on_system_controller_setup_finished)

        SignalManager.connect_signal(self.system_controller,
                                     self.system_controller_setup,
                                     self.system_controller.setup)

    def _connect_db_manager(self):
        SignalManager.connect_signal(self.db_manager,
                                     self.db_manager.message_signal,
                                     self.ui_manager.on_log_signal_received)

        SignalManager.connect_signal(self.db_manager,
                                     self.db_manager.error_message_signal,
                                     self.ui_manager.on_err_signal_received)

        SignalManager.connect_signal(self.db_manager,
                                     self.db_manager.db_setup_start,
                                     self.ui_manager.on_db_setup_start)

        SignalManager.connect_signal(self.db_manager,
                                     self.db_manager.db_setup_done,
                                     self.ui_manager.on_db_setup_done)

        SignalManager.connect_signal(self.db_manager,
                                     self.db_setup,
                                     self.db_manager.setup_db)

    def _connect_git_animator_controller_generic(self):
        SignalManager.connect_signal(self.anim_git_controller,
                                     self.anim_git_controller.log_message,
                                     self.ui_manager.on_log_signal_received)

        SignalManager.connect_signal(self.anim_git_controller,
                                     self.anim_git_controller.error_message,
                                     self.ui_manager.on_err_signal_received)

        SignalManager.connect_signal(self.anim_git_controller,
                                     self.anim_git_controller.creating_anim_rep,
                                     self.ui_manager.on_anim_rep_creating)

        SignalManager.connect_signal(self.anim_git_controller,
                                     self.anim_git_controller.anim_rep_creation_completed,
                                     self.ui_manager.on_anim_rep_creation_completed)

    def _connect_git_animator_controller(self):
        SignalManager.connect_signal(self.anim_git_controller,
                                     self.anim_git_controller.setup_started,
                                     self.ui_manager.on_git_setup_started)

        SignalManager.connect_signal(self.anim_git_controller,
                                     self.anim_git_controller.setup_completed,
                                     self.ui_manager.on_setup_completed)

        SignalManager.connect_signal(self.anim_git_controller,
                                     self.anim_git_controller.setup_completed,
                                     self.on_git_setup_completed)

        SignalManager.connect_signal(self.anim_git_controller,
                                     self.anim_git_controller.get_latest_completed,
                                     self.ui_manager.on_get_latest_completed)

        self._connect_ui_manager_git_anim_controller()

    def _connect_ui_manager_git_anim_controller(self):
        SignalManager.connect_signal(self.ui_manager,
                                     self.ui_manager.lw_get_latest_clicked,
                                     self.anim_git_controller.get_anim_rep_latest)

    def _disconnect_ui_manager_git_anim_controller(self):
        get_anim_rep_meta_method = QMetaMethod.fromSignal(self.ui_manager.lw_get_latest_clicked)
        if self.ui_manager.isSignalConnected(get_anim_rep_meta_method):
            self.ui_manager.lw_get_latest_clicked.disconnect(self.anim_git_controller.get_anim_rep_latest)

    def _disconnect_git_controller(self):
        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.setup_started,
                                        self.ui_manager.on_git_setup_started)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.setup_completed,
                                        self.on_git_setup_completed)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.setup_completed,
                                        self.anim_git_controller.on_git_setup_completed)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.push_completed,
                                        self.ui_manager.on_upload_completed)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.get_latest_completed,
                                        self.ui_manager.on_get_latest_completed)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.log_message,
                                        self.ui_manager.on_log_signal_received)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.error_message,
                                        self.ui_manager.on_err_signal_received)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.send_main_branch,
                                        self.ui_manager.on_get_main_branch)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.send_all_branches,
                                        self.ui_manager.on_get_all_branches)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.send_merge_requests,
                                        self.ui_manager.on_get_all_merge_requests)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.send_merge_request_commits,
                                        self.ui_manager.on_get_merge_request_commits)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.send_merge_requests_changes,
                                        self.ui_manager.on_get_merge_request_changes)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.send_merge_requests_comments,
                                        self.ui_manager.on_get_merge_requests_comments)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.send_repository_history,
                                        self.ui_manager.on_get_repository_history)

        SignalManager.disconnect_signal(self.git_controller,
                                        self.git_controller.send_current_changes,
                                        self.ui_manager.on_get_changes_list)

    def _disconnect_ui_manager_git_controller(self):
        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_git_merge_request_tab_clicked,
                                        self.git_controller.get_main_branch)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_git_merge_request_tab_clicked,
                                        self.git_controller.get_all_branches)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_git_merge_request_tab_clicked,
                                        self.git_controller.load_merge_requests)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_get_latest_clicked,
                                        self.git_controller.get_latest)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_uploaded_clicked,
                                        self.git_controller.push_changes)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_get_merge_request_changed,
                                        self.git_controller.get_merge_request_commits)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_get_merge_request_changed,
                                        self.git_controller.get_merge_request_changes)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_get_merge_request_changed,
                                        self.git_controller.get_merge_requests_comments)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_merge_request_add_comment,
                                        self.git_controller.merge_request_add_comment)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_accept_merge_request_and_merge,
                                        self.git_controller.merge_request_accept_and_merge)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_git_history_tab_clicked,
                                        self.git_controller.get_repository_history)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_git_changes_list_tab_clicked,
                                        self.git_controller.get_repository_changes)

    def _disconnect_git_animator_controller(self):
        SignalManager.disconnect_signal(self.anim_git_controller,
                                        self.anim_git_controller.setup_started,
                                        self.ui_manager.on_git_setup_started)

        SignalManager.disconnect_signal(self.anim_git_controller,
                                        self.anim_git_controller.setup_completed,
                                        self.ui_manager.on_setup_completed)

        SignalManager.disconnect_signal(self.anim_git_controller,
                                        self.anim_git_controller.setup_completed,
                                        self.on_git_setup_completed)

        SignalManager.disconnect_signal(self.anim_git_controller,
                                        self.anim_git_controller.get_latest_completed,
                                        self.ui_manager.on_get_latest_completed)

        SignalManager.disconnect_signal(self.ui_manager,
                                        self.ui_manager.lw_get_latest_clicked,
                                        self.anim_git_controller.get_anim_rep_latest)

    def on_git_setup_completed(self, success: bool):
        self.check_user_branch.emit()

    def _set_style_sheet(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dark_theme_path = os.path.join(script_dir, "./View/", "appStyle.qss")
        with open(dark_theme_path, "r") as file:
            qss = file.read()
            self.setStyleSheet(qss)

    def run(self):
        if self.config['test']['debug']:
            self.ui_manager.open_window(WindowID.LAUNCHER)
            self.login_accepted(self.config['test']['debug_user'])
        else:
            self.ui_manager.open_window(WindowID.LOGING)

        self.db_setup.emit()
        self.exec()

    def __del__(self):
        self.closeAllWindows()
        return

    @Slot(str)
    def login_accepted(self, username: str):
        self.user_session.login(username)
        self.ui_manager.launcher_window.set_user_session(self.user_session)
        self.ui_manager.open_window(WindowID.LAUNCHER)
        self._connect_git_animator_controller_generic()

        # We need to disconnect and connect the signals soo we don't duplicate calls
        if self.user_session.role_id == ROLE_ID.ANIMATOR.value:
            self._disconnect_git_controller()
            self._disconnect_ui_manager_git_controller()

            self._connect_ui_manager_git_anim_controller()
            self._connect_git_animator_controller()
        else:
            self._disconnect_ui_manager_git_controller()
            self._disconnect_ui_manager_git_anim_controller()

            self._connect_git_controller()
            self._connect_ui_manager_git_controller()

        self.system_controller_setup.emit()

    @Slot()
    def on_system_controller_setup_finished(self):
        if self.git_installed:
            if self.user_session.role_id == ROLE_ID.ANIMATOR.value:
                print("User is an animator")
                self.git_animator_setup.emit()
            else:
                print("User is not animator")
                self.git_setup.emit()

    @Slot(bool)
    def on_git_checked(self, success: bool):
        self.git_installed = success

    @Slot(bool)
    def on_git_installed(self, success: bool):
        if self.git_installed:
            return

        self.git_installed = success

    @Slot()
    def on_main_window_closed(self):
        self.ui_manager.current_window.loading.stop_anim_screen()

    @Slot()
    def on_application_destroyed(self):
        if self.system_controller_thread is not None:
            self.system_controller_thread.quit()
            self.system_controller_thread.wait()

        if self.git_controller_thread is not None:
            self.git_controller_thread.quit()
            self.git_controller_thread.wait()

        if self.db_manager_thread is not None:
            self.db_manager_thread.quit()
            self.db_manager_thread.wait()

        if self.anim_git_controller_thread is not None:
            self.anim_git_controller_thread.quit()
            self.anim_git_controller_thread.wait()

        if self.user_session:
            del self.user_session

        self.__del__()

    @Slot()
    def on_login_out(self):
        self.user_session.logout()
        self.ui_manager.open_window(WindowID.LOGING)
