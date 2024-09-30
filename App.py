from PySide6.QtWidgets import QApplication
from Utils.ConfigFileManager import ConfigFileManager
from View.UIManager import UIManager
from View.UIManager import WindowID
from Controller.GitController import GitController
from Controller.SystemController import SystemController
from PySide6.QtCore import QThread, Signal, Slot
from Utils.DataBaseManager import DataBaseManager
from Utils.UserSession import UserSession
from Utils.Environment import RoleID
from Utils.SignalManager import SignalManager
from Controller.AnimatorGitController import AnimatorGitController
import os


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
        self.ui_manager = UIManager()
        self.logger = self.ui_manager.logger
        self.git_installed = False
        self.user_session = UserSession()
        self.config = ConfigFileManager().get_config()
        """ Create objects threads """
        self._initialize_threads()
        """ Connect objects signals """
        self._connect_ui_manager()
        self._connect_git_controller()
        self._connect_system_controller()
        self._connect_db_manager()

    def _initialize_threads(self):
        self.git_controller = self._create_controller(GitController, "_git_controller_thread")
        self.system_controller = self._create_controller(SystemController, "_system_controller_thread")
        self.db_manager = self._create_controller(DataBaseManager, "_db_manager_thread")
        self.anim_git_controller = self._create_controller(AnimatorGitController, "_anim_git_controller_thread")

    def _create_controller(self, controller_cls, thread_name):
        thread = QThread(self)
        controller = controller_cls()
        setattr(self, thread_name, thread)
        controller.moveToThread(thread)
        thread.start()
        return controller

    def _connect_ui_manager(self):
        self._connect_ui_manager_launcher()
        self._connect_ui_manager_system_controller()
        self._connect_ui_manager_git_controller()
        self._connect_ui_manager_login()

    def _connect_ui_manager_launcher(self):
        SignalManager.connect_signals(self.ui_manager, [
            (self.ui_manager.lw_window_closed, self.on_main_window_closed),
            (self.ui_manager.lw_destroy_application, self.on_application_destroyed),
            (self.ui_manager.lg_destroy_application, self.on_application_destroyed),
            (self.ui_manager.lw_log_out, self.on_login_out),
            (self.ui_manager.lw_switch_account, self.on_switch_account)
        ])

    def _connect_ui_manager_system_controller(self):
        SignalManager.connect_signals(self.ui_manager, [
            (self.ui_manager.lw_open_maya_clicked, self.system_controller.open_maya),
            (self.ui_manager.lw_rep_viewer_open_file, self.system_controller.open_file),
            (self.ui_manager.lw_rep_viewer_open_explorer, self.system_controller.open_in_explorer),
            (self.ui_manager.lw_rep_viewer_delete_file, self.system_controller.delete_file)
        ])

    def _connect_ui_manager_git_controller(self):
        # Almost all this ui_manager signals are set using the setattr() method
        SignalManager.connect_signals(self.ui_manager, [
            (self.ui_manager.lw_git_merge_request_tab_clicked, self.git_controller.get_main_branch),
            (self.ui_manager.lw_git_merge_request_tab_clicked, self.git_controller.get_all_branches),
            (self.ui_manager.lw_git_merge_request_tab_clicked, self.git_controller.load_merge_requests),
            (self.ui_manager.lw_get_merge_request_changed, self.git_controller.get_merge_request_commits),
            (self.ui_manager.lw_get_merge_request_changed, self.git_controller.get_merge_request_changes),
            (self.ui_manager.lw_get_merge_request_changed, self.git_controller.get_merge_requests_comments),
            (self.ui_manager.lw_merge_request_add_comment, self.git_controller.merge_request_add_comment),
            (self.ui_manager.lw_accept_merge_request_and_merge, self.git_controller.merge_request_accept_and_merge),
            (self.ui_manager.lw_get_latest_clicked, self.git_controller.get_latest),
            (self.ui_manager.lw_commit_and_push_clicked, self.git_controller.commit_and_push_changes),
            (self.ui_manager.lw_git_history_tab_clicked, self.git_controller.get_repository_history),
            (self.ui_manager.lw_git_changes_list_tab_clicked, self.git_controller.get_repository_changes),
            (self.ui_manager.lw_log_out, self.git_controller.on_log_out),
            (self.ui_manager.lw_rep_viewer_rep_updated, self.git_controller.get_repository_changes),
            (self.ui_manager.lw_refresh_clicked, self.git_controller.on_refresh),
        ])

    def _connect_ui_manager_login(self):
        SignalManager.connect_signals(self.ui_manager, [
            (self.ui_manager.lg_login_accepted, self.login_accepted),
            (self.ui_manager.lg_login_accepted, self.ui_manager.on_login)
        ])

    def _connect_git_controller(self):
        SignalManager.connect_signals(self.git_controller, [
            (self.git_controller.setup_completed, self.on_git_setup_completed),
            (self.git_controller.setup_started, self.ui_manager.on_git_setup_started),
            (self.git_controller.setup_completed, self.ui_manager.on_setup_completed),
            (self.git_controller.push_and_commit_started, self.ui_manager.loading_process_started),
            (self.git_controller.push_and_commit_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.push_and_commit_completed, self.ui_manager.on_push_and_commit_completed),
            (self.git_controller.get_latest_started, self.ui_manager.loading_process_started),
            (self.git_controller.get_latest_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.accept_merge_started, self.ui_manager.loading_process_started),
            (self.git_controller.accept_merge_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.load_mr_started, self.ui_manager.loading_process_started),
            (self.git_controller.load_mr_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.add_comment_started, self.ui_manager.loading_process_started),
            (self.git_controller.add_comment_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.get_mr_changes_started, self.ui_manager.loading_process_started),
            (self.git_controller.get_mr_changes_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.get_mr_comments_started, self.ui_manager.loading_process_started),
            (self.git_controller.get_mr_comments_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.get_mr_commits_started, self.ui_manager.loading_process_started),
            (self.git_controller.get_mr_commits_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.auto_publish_started, self.ui_manager.loading_process_started),
            (self.git_controller.auto_publish_completed, self.ui_manager.loading_process_completed),

            (self.git_controller.log_message, self.ui_manager.on_log_signal_received),
            (self.git_controller.error_message, self.ui_manager.on_err_signal_received),
            (self.git_controller.send_main_branch, self.ui_manager.on_get_main_branch),
            (self.git_controller.send_all_branches, self.ui_manager.on_get_all_branches),
            (self.git_controller.send_merge_requests, self.ui_manager.on_get_all_merge_requests),
            (self.git_controller.send_merge_request_commits, self.ui_manager.on_get_merge_request_commits),
            (self.git_controller.send_merge_requests_changes, self.ui_manager.on_get_merge_request_changes),
            (self.git_controller.send_merge_requests_comments, self.ui_manager.on_get_merge_requests_comments),
            (self.git_controller.send_repository_history, self.ui_manager.on_get_repository_history),
            (self.git_controller.send_current_changes, self.ui_manager.on_get_changes_list),
            (self.git_controller.refreshing, self.ui_manager.loading_process_started),
            (self.git_controller.refreshing_completed, self.ui_manager.loading_process_completed)
        ])

        SignalManager.connect_signals(self, [
            (self.git_setup, self.git_controller.setup),
            (self.check_user_branch, self.git_controller.verify_user_branch)
        ])

    def _connect_system_controller(self):
        SignalManager.connect_signals(self.system_controller, [
            (self.system_controller.setup_started, self.ui_manager.loading_process_started),
            (self.system_controller.log_message, self.ui_manager.on_log_signal_received),
            (self.system_controller.error_message, self.ui_manager.on_err_signal_received),
            (self.system_controller.maya_checked, self.ui_manager.on_maya_checked),
            (self.system_controller.git_checked, self.on_git_checked),
            (self.system_controller.git_installed, self.on_git_installed),
            (self.system_controller.setup_finished, self.on_system_controller_setup_finished),
        ])

        SignalManager.connect_signal(self, self.system_controller_setup, self.system_controller.setup)

    def _connect_db_manager(self):
        SignalManager.connect_signals(self.db_manager, [
            (self.db_manager.message_signal, self.ui_manager.on_log_signal_received),
            (self.db_manager.error_message_signal, self.ui_manager.on_err_signal_received),
            (self.db_manager.db_setup_start, self.ui_manager.loading_process_started),
            (self.db_manager.db_setup_done, self.ui_manager.loading_process_completed),
            (self.db_setup, self.db_manager.setup_db)
        ])

    def _connect_git_animator_controller_generic(self):
        SignalManager.connect_signals(self.anim_git_controller, [
            (self.anim_git_controller.log_message, self.ui_manager.on_log_signal_received),
            (self.anim_git_controller.error_message, self.ui_manager.on_err_signal_received),
            (self.anim_git_controller.publishing_anim_rep, self.ui_manager.loading_process_started),
            (self.anim_git_controller.publishing_anim_rep_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.uploading_anim_files, self.ui_manager.loading_process_started),
            (self.anim_git_controller.uploading_anim_files_completed , self.ui_manager.loading_process_completed),
            (self.anim_git_controller.get_mr_comments_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.get_mr_comments_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.get_mr_commits_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.get_mr_commits_completed, self.ui_manager.loading_process_completed)
        ])

        SignalManager.connect_signals(self, [
            (self.check_user_branch, self.anim_git_controller.verify_user_branch),
            (self.git_animator_setup, self.anim_git_controller.setup)
        ])

        SignalManager.connect_signals(self.ui_manager, [
            (self.ui_manager.lw_publish_to_anim, self.anim_git_controller.publish_rep),
        ])

    def _connect_git_animator_controller(self):
        SignalManager.connect_signals(self.anim_git_controller,[
            (self.anim_git_controller.setup_started, self.ui_manager.on_git_setup_started),
            (self.anim_git_controller.setup_completed, self.on_git_setup_completed),
            (self.anim_git_controller.setup_completed, self.ui_manager.on_setup_completed),
            (self.anim_git_controller.get_latest_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.get_latest_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.refreshing, self.ui_manager.loading_process_started),
            (self.anim_git_controller.refreshing_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.load_mr_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.load_mr_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.add_comment_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.add_comment_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.get_mr_changes_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.get_mr_changes_completed, self.ui_manager.loading_process_completed)
        ])

        SignalManager.connect_signals(self.ui_manager,[
            (self.ui_manager.lw_get_latest_clicked, self.anim_git_controller.get_latest),
            (self.ui_manager.lw_refresh_clicked, self.anim_git_controller.on_refresh)
        ])

    def _disconnect_git_controller(self):
        SignalManager.disconnect_signals(self.git_controller, [
            (self.git_controller.setup_started, self.ui_manager.on_git_setup_started),
            (self.git_controller.setup_completed, self.on_git_setup_completed),
            (self.git_controller.push_and_commit_started, self.ui_manager.loading_process_started),
            (self.git_controller.push_and_commit_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.push_and_commit_completed, self.ui_manager.on_push_and_commit_completed),
            (self.git_controller.get_latest_started, self.ui_manager.loading_process_started),
            (self.git_controller.get_latest_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.accept_merge_started, self.ui_manager.loading_process_started),
            (self.git_controller.accept_merge_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.load_mr_started, self.ui_manager.loading_process_started),
            (self.git_controller.load_mr_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.add_comment_started, self.ui_manager.loading_process_started),
            (self.git_controller.add_comment_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.get_mr_changes_started, self.ui_manager.loading_process_started),
            (self.git_controller.get_mr_changes_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.get_mr_comments_started, self.ui_manager.loading_process_started),
            (self.git_controller.get_mr_comments_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.get_mr_commits_started, self.ui_manager.loading_process_started),
            (self.git_controller.get_mr_commits_completed, self.ui_manager.loading_process_completed),
            (self.git_controller.auto_publish_started, self.ui_manager.loading_process_started),
            (self.git_controller.auto_publish_completed, self.ui_manager.loading_process_completed),

            (self.git_controller.log_message, self.ui_manager.on_log_signal_received),
            (self.git_controller.error_message, self.ui_manager.on_err_signal_received),
            (self.git_controller.send_main_branch, self.ui_manager.on_get_main_branch),
            (self.git_controller.send_all_branches, self.ui_manager.on_get_all_branches),
            (self.git_controller.send_merge_requests, self.ui_manager.on_get_all_merge_requests),
            (self.git_controller.send_merge_request_commits, self.ui_manager.on_get_merge_request_commits),
            (self.git_controller.send_merge_requests_changes, self.ui_manager.on_get_merge_request_changes),
            (self.git_controller.send_merge_requests_comments, self.ui_manager.on_get_merge_requests_comments),
            (self.git_controller.send_repository_history, self.ui_manager.on_get_repository_history),
            (self.git_controller.send_current_changes, self.ui_manager.on_get_changes_list),
            (self.ui_manager.lw_log_out, self.git_controller.on_log_out),
            (self.git_controller.refreshing, self.ui_manager.loading_process_started),
            (self.git_controller.refreshing_completed, self.ui_manager.loading_process_completed)
        ])

        SignalManager.disconnect_signals(self, [
            (self.git_setup, self.git_controller.setup),
            (self.check_user_branch, self.git_controller.verify_user_branch)
        ])

    def _disconnect_ui_manager_git_controller(self):
        SignalManager.disconnect_signals(self.ui_manager, [
            (self.ui_manager.lw_git_merge_request_tab_clicked, self.git_controller.get_main_branch),
            (self.ui_manager.lw_git_merge_request_tab_clicked, self.git_controller.get_all_branches),
            (self.ui_manager.lw_git_merge_request_tab_clicked, self.git_controller.load_merge_requests),
            (self.ui_manager.lw_get_latest_clicked, self.git_controller.get_latest),
            (self.ui_manager.lw_commit_and_push_clicked, self.git_controller.commit_and_push_changes),
            (self.ui_manager.lw_get_merge_request_changed, self.git_controller.get_merge_request_commits),
            (self.ui_manager.lw_get_merge_request_changed, self.git_controller.get_merge_request_changes),
            (self.ui_manager.lw_get_merge_request_changed, self.git_controller.get_merge_requests_comments),
            (self.ui_manager.lw_merge_request_add_comment, self.git_controller.merge_request_add_comment),
            (self.ui_manager.lw_accept_merge_request_and_merge, self.git_controller.merge_request_accept_and_merge),
            (self.ui_manager.lw_git_history_tab_clicked, self.git_controller.get_repository_history),
            (self.ui_manager.lw_git_changes_list_tab_clicked, self.git_controller.get_repository_changes),
            (self.ui_manager.lw_refresh_clicked, self.git_controller.on_refresh)
        ])

    def _disconnect_git_animator_controller(self):
        SignalManager.disconnect_signals(self.anim_git_controller, [
            (self.anim_git_controller.setup_started, self.ui_manager.on_git_setup_started),
            (self.anim_git_controller.setup_completed, self.ui_manager.on_setup_completed),
            (self.anim_git_controller.setup_completed, self.on_git_setup_completed),
            (self.anim_git_controller.get_latest_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.get_latest_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.refreshing, self.ui_manager.loading_process_started),
            (self.anim_git_controller.refreshing_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.load_mr_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.load_mr_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.add_comment_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.add_comment_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.get_mr_changes_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.get_mr_changes_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.get_mr_comments_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.get_mr_comments_completed, self.ui_manager.loading_process_completed),
            (self.anim_git_controller.get_mr_commits_started, self.ui_manager.loading_process_started),
            (self.anim_git_controller.get_mr_commits_completed, self.ui_manager.loading_process_completed)
        ])

        SignalManager.disconnect_signals(self.ui_manager, [
            (self.ui_manager.lw_get_latest_clicked, self.anim_git_controller.get_latest),
            (self.ui_manager.lw_refresh_clicked, self.anim_git_controller.on_refresh)
        ])

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

    @staticmethod
    def is_animator(role: RoleID):
        return role == RoleID.ANIMATOR.value or role == RoleID.ADMIN_ANIM.value

    @Slot(str)
    def login_accepted(self, username: str, role: RoleID = RoleID.NONE):
        self.user_session.login(username)
        if role != RoleID.NONE:
            self.user_session.role_id = role.value

        self.ui_manager.launcher_window.set_user_session(self.user_session)
        self.ui_manager.open_window(WindowID.LAUNCHER)
        self._connect_git_animator_controller_generic()

        # We need to disconnect and connect the signals soo we don't duplicate calls
        if self.is_animator(self.user_session.role_id):
            self._disconnect_git_controller()
            self._disconnect_ui_manager_git_controller()

            self._connect_git_animator_controller()
        else:
            self._disconnect_git_animator_controller()

            self._connect_git_controller()
            self._connect_ui_manager_git_controller()

        self.system_controller_setup.emit()

    @Slot()
    def on_system_controller_setup_finished(self):
        if self.git_installed:
            if self.is_animator(self.user_session.role_id):
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
        self._stop_thread("_system_controller_thread")
        self._stop_thread("_git_controller_thread")
        self._stop_thread("_db_manager_thread")
        self._stop_thread("_anim_git_controller_thread")

        if self.user_session is not None:
            del self.user_session
        self.__del__()

    def _stop_thread(self, thread_name):
        thread = getattr(self, thread_name, None)
        if thread:
            thread.quit()
            thread.wait()

    @Slot()
    def on_login_out(self):
        self.user_session.logout()
        self.ui_manager.open_window(WindowID.LOGING)

    @Slot()
    def on_switch_account(self, role: RoleID):
        self.ui_manager.launcher_window.logger_widget.clear_log()
        self.login_accepted(self.user_session.username, role)

