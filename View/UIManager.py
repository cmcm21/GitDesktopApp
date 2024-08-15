from View.LauncherWindow import LauncherWindow
from View.UILoginWindow import LoginWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Slot, Signal, QObject, QTimer
from View.WindowID import WindowID
from Utils.Environment import ROLE_ID
from Utils.UserSession import UserSession


class UIManager(QObject):
    """Launcher window buttons signals"""
    lw_get_latest_clicked = Signal()
    lw_uploaded_clicked = Signal(str)
    lw_publish_to_anim = Signal(str)
    lw_open_maya_clicked = Signal()
    lw_login_out = Signal()
    lw_new_workspace_clicked = Signal()
    lw_window_closed = Signal()
    lw_get_merge_request_changed = Signal(int)
    lw_merge_request_add_comment = Signal(str, int)
    lw_accept_merge_request_and_merge = Signal(int, str)
    lw_file_tree_clicked = Signal(str)
    lg_login_accepted = Signal()
    lw_destroy_application = Signal()
    lg_destroy_application = Signal()

    def __init__(self, config: dict):
        super().__init__()
        self.launcher_window = LauncherWindow(config, WindowID.LAUNCHER)
        self.login_window = LoginWindow(WindowID.LOGING)
        self.current_window = None
        self.logger = self.launcher_window.logger_widget.logger
        self.connect_button: QPushButton = self.launcher_window.connect_button
        self.windows = {
            WindowID.LAUNCHER: self.launcher_window,
            WindowID.LOGING: self.login_window
        }
        self.config = config
        self._connect_launcher_windows()
        self._connect_login_window()
        self._connect_launcher_windows_to_loading_screen()

    def open_window(self, window_id: WindowID):
        if window_id not in self.windows:
            return

        if self.current_window is not None and self.current_window != self.windows[window_id]:
            self.current_window.automatic_close = True
            self.current_window.close()

        self.current_window = self.windows[window_id]
        self.current_window.open()
        if window_id == WindowID.LAUNCHER:
            self.current_window.automatic_close = False
            QTimer.singleShot(500, self.open_launcher_window)

    def open_launcher_window(self):
        self.current_window.repaint()
        self.current_window.update()

    def _connect_launcher_windows(self):
        """ Using UIManager signals to make a bridge between UI Signals and Controllers """
        self.lw_git_history_tab_clicked = self.launcher_window.git_tab.history_tab_clicked
        self.lw_git_changes_list_tab_clicked = self.launcher_window.git_tab.changes_list_clicked
        self.lw_git_merge_request_tab_clicked = self.launcher_window.git_tab.merge_request_clicked
        self.lw_get_latest_clicked = self.launcher_window.get_latest
        self.lw_uploaded_clicked = self.launcher_window.upload_repository
        self.lw_open_maya_clicked = self.launcher_window.maya_btn.clicked
        self.lw_window_closed = self.launcher_window.window_closed
        self.lw_get_merge_request_changed = self.launcher_window.git_tab.git_sniffer.merge_request.selected_mr_changed
        self.lw_merge_request_add_comment = self.launcher_window.git_tab.git_sniffer.merge_request.add_comment
        self.lw_accept_merge_request_and_merge = self.launcher_window.git_tab.git_sniffer.merge_request.accept_and_merge
        self.lw_login_out = self.launcher_window.login_out
        self.lw_destroy_application = self.launcher_window.application_destroyed
        self.lg_destroy_application = self.login_window.application_destroyed
        self.lw_file_tree_clicked = self.launcher_window.git_tab.repository_viewer.file_selected
        self.lw_publish_to_anim = self.launcher_window.publish_to_anim_rep

        self.lw_destroy_application.connect(self._on_application_destroyed)
        self.lg_destroy_application.connect(self._on_application_destroyed)
        self.launcher_window.switch_account.connect(self.on_switch_accounts)

    def _on_application_destroyed(self):
        for window in self.windows.values():
            window.loading.stop_anim_screen()

    def _connect_login_window(self):
        self.lg_login_accepted = self.login_window.login_signal

    def _connect_launcher_windows_to_loading_screen(self):
        self.lw_get_merge_request_changed.connect(lambda: self.launcher_window.loading.show_anim_screen())
        self.lw_merge_request_add_comment.connect(lambda: self.launcher_window.loading.show_anim_screen())
        self.lw_accept_merge_request_and_merge.connect(lambda: self.launcher_window.loading.show_anim_screen())
        self.lw_uploaded_clicked.connect(lambda: self.launcher_window.loading.show_anim_screen())
        self.lw_get_latest_clicked.connect(lambda: self.launcher_window.loading.show_anim_screen())

    def on_switch_accounts(self, role: ROLE_ID):
        user_session = UserSession()
        user_session.role_id = role.value

        if self.current_window.window_id == WindowID.LAUNCHER:
            self.current_window.automatic_close = True
            self.current_window.close()
            self.current_window.set_user_session(user_session)

            self.current_window = self.windows[WindowID.LAUNCHER]
            self.current_window.open()
            self.current_window.automatic_close = False

    @Slot()
    def on_git_setup_started(self):
        self.launcher_window.loading.show_anim_screen()

    @Slot(bool)
    def on_setup_completed(self, success: bool):
        if self.launcher_window.window_id != WindowID.LAUNCHER:
            return
        self.launcher_window.on_setup_completed(success)
        self.launcher_window.loading.stop_anim_screen()
        self.current_window.showMaximized()
        self.launcher_window.git_tab.send_starting_signals()

    @Slot(str)
    def on_log_signal_received(self, log_message: str):
        self.logger.debug(log_message)

    @Slot(str)
    def on_err_signal_received(self, error_message: str):
        self.logger.error(error_message)
        self.launcher_window.loading.stop_anim_screen()

    @Slot(bool)
    def on_maya_checked(self, is_installed):
        if not is_installed:
            self.launcher_window.maya_btn.setToolTip("Maya is Not installed in the Operation System")

    @Slot(str)
    def on_get_main_branch(self, main_branch: str):
        self.launcher_window.git_tab.set_main_branch_in_merge_request_tab(main_branch)

    @Slot(list)
    def on_get_all_branches(self, branches: str):
        self.launcher_window.git_tab.set_all_branches_in_merge_request_tab(branches)

    @Slot(list)
    def on_get_all_merge_requests(self, merge_requests: list):
        self.launcher_window.git_tab.set_all_merge_requests(merge_requests)
        self.launcher_window.loading.stop_anim_screen()

    @Slot(list)
    def on_get_merge_request_commits(self, merge_request_commits: list):
        self.launcher_window.git_tab.set_merge_request_commits(merge_request_commits)
        self.launcher_window.loading.stop_anim_screen()

    @Slot(list)
    def on_get_merge_request_changes(self, changes: list):
        self.launcher_window.git_tab.set_merge_request_changes(changes)
        self.launcher_window.loading.stop_anim_screen()

    @Slot(list)
    def on_get_merge_requests_comments(self, comments: list):
        self.launcher_window.git_tab.set_merge_requests_comments(comments)
        self.launcher_window.loading.stop_anim_screen()

    @Slot()
    def on_get_latest_completed(self):
        self.launcher_window.loading.stop_anim_screen()

    @Slot()
    def on_upload_completed(self):
        self.launcher_window.loading.stop_anim_screen()

    @Slot()
    def on_system_controller_setup_started(self):
        self.launcher_window.loading.show_anim_screen()

    @Slot()
    def on_db_setup_done(self):
        self.login_window.loading.stop_anim_screen()

    @Slot()
    def on_db_setup_start(self):
        self.login_window.loading.show_anim_screen()

    @Slot(list)
    def on_get_repository_history(self, commits: list):
        self.launcher_window.git_tab.on_get_repository_history(commits)

    @Slot(list)
    def on_get_changes_list(self, changes_modified: list, changes: list):
        self.launcher_window.git_tab.on_get_current_changes(changes_modified, changes)

    @Slot()
    def on_anim_rep_creating(self):
        self.launcher_window.loading.show_anim_screen()

    @Slot()
    def on_anim_rep_creation_completed(self):
        self.launcher_window.loading.stop_anim_screen()

    @Slot()
    def on_login(self):
        self.launcher_window.logger_widget.clear_log()

