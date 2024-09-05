from Utils.ConfigFileManager import ConfigFileManager
from Utils.Environment import RoleID
from Utils.SignalManager import SignalManager
from View.LauncherWindow import LauncherWindow
from View.UILoginWindow import LoginWindow
from View.WindowID import WindowID
from View.SelectDirectory import SelectDirectoryWindow
from PySide6.QtCore import Slot, Signal, QObject, QTimer


class UIManager(QObject):
    """Launcher window buttons signals"""
    lw_get_latest_clicked = Signal()
    lw_open_maya_clicked = Signal()
    lw_log_out = Signal()
    lw_new_workspace_clicked = Signal()
    lw_window_closed = Signal()
    lw_destroy_application = Signal()
    lg_destroy_application = Signal()
    lw_git_history_tab_clicked = Signal()
    lw_git_changes_list_tab_clicked = Signal()
    lw_git_merge_request_tab_clicked = Signal()
    lw_refresh_clicked = Signal()

    lw_publish_to_anim = Signal(str, bool)
    lw_uploaded_clicked = Signal(str)
    lw_get_merge_request_changed = Signal(int)
    lw_merge_request_add_comment = Signal(str, int)
    lw_accept_merge_request_and_merge = Signal(int, str)
    sdw_select_directory = Signal(str)
    lw_switch_account = Signal(RoleID)
    lg_login_accepted = Signal(str)
    lw_rep_viewer_open_file = Signal(str)
    lw_rep_viewer_delete_file = Signal(str)
    lw_rep_viewer_open_explorer = Signal(str)
    lw_rep_viewer_rep_updated = Signal()

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigFileManager()
        self.config = self.config_manager
        self.launcher_window = LauncherWindow(window_id=WindowID.LAUNCHER)
        self.login_window = LoginWindow(WindowID.LOGING)
        self.select_directory_window = None
        self.current_window = None
        self.logger = self.launcher_window.logger_widget.logger
        self.windows = {
            WindowID.LAUNCHER: self.launcher_window,
            WindowID.LOGING: self.login_window
        }
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
        """Using UIManager signals to bridge between UI Signals and Controllers"""
        self._connect_git_tab()
        self._connect_git_merge_request_signals()
        self._connect_repository_viewer_signals()
        self._connect_launcher_window_signals()

        # Additional connections
        self.lw_destroy_application.connect(self._on_application_destroyed)
        self.login_window.application_destroyed.connect(self._on_application_destroyed)

    def _connect_git_merge_request_signals(self):
        SignalManager.connect_signals(self.launcher_window.git_tab.git_sniffer, [
            (self.launcher_window.git_tab.git_sniffer.merge_request.selected_mr_changed, self.lw_get_merge_request_changed.emit),
            (self.launcher_window.git_tab.git_sniffer.merge_request.add_comment, self.lw_merge_request_add_comment.emit),
            (self.launcher_window.git_tab.git_sniffer.merge_request.accept_and_merge, self.lw_accept_merge_request_and_merge.emit)
        ])

    def _connect_repository_viewer_signals(self):
        SignalManager.connect_signals(self.launcher_window.git_tab.repository_viewer, [
            (self.launcher_window.git_tab.repository_viewer.open_file, self.lw_rep_viewer_open_file.emit),
            (self.launcher_window.git_tab.repository_viewer.delete_file, self.lw_rep_viewer_delete_file.emit),
            (self.launcher_window.git_tab.repository_viewer.open_explorer, self.lw_rep_viewer_open_explorer.emit),
            (self.launcher_window.git_tab.repository_viewer.repo_updated, self.lw_rep_viewer_rep_updated.emit)
        ])

    def _connect_launcher_window_signals(self):
        SignalManager.connect_signals(self.launcher_window, [
            (self.launcher_window.publish_to_anim_rep, self.lw_publish_to_anim.emit),
            (self.launcher_window.get_latest, self.lw_get_latest_clicked),
            (self.launcher_window.switch_account, self.lw_switch_account.emit),
            (self.launcher_window.upload_repository, self.lw_uploaded_clicked.emit),
            (self.launcher_window.open_maya, self.lw_open_maya_clicked.emit),
            (self.launcher_window.window_closed, self.lw_window_closed.emit),
            (self.launcher_window.application_destroyed, self.lw_destroy_application.emit),
            (self.launcher_window.log_out, self.lw_log_out.emit),
            (self.launcher_window.refresh, self.lw_refresh_clicked)
        ])

    def _connect_git_tab(self):
        SignalManager.connect_signals(self.launcher_window.git_tab, [
            (self.launcher_window.git_tab.history_tab_clicked, self.lw_git_history_tab_clicked.emit),
            (self.launcher_window.git_tab.changes_list_clicked, self.lw_git_changes_list_tab_clicked.emit),
            (self.launcher_window.git_tab.merge_request_clicked, self.lw_git_merge_request_tab_clicked.emit)
        ])

    def _on_application_destroyed(self):
        for window in self.windows.values():
            window.loading.stop_anim_screen()

    def _connect_login_window(self):
        self.login_window.login_signal.connect(lambda username: self.lg_login_accepted.emit(username))

    def _connect_launcher_windows_to_loading_screen(self):
        self.lw_get_merge_request_changed.connect(lambda: self.launcher_window.loading.show_anim_screen())
        self.lw_merge_request_add_comment.connect(lambda: self.launcher_window.loading.show_anim_screen())
        self.lw_accept_merge_request_and_merge.connect(lambda: self.launcher_window.loading.show_anim_screen())
        self.lw_uploaded_clicked.connect(lambda: self.launcher_window.loading.show_anim_screen())
        self.lw_get_latest_clicked.connect(lambda: self.launcher_window.loading.show_anim_screen())

    @Slot()
    def on_git_setup_started(self):
        self.launcher_window.loading.show_anim_screen()

    @Slot(bool)
    def on_setup_completed(self, success: bool):
        if self.launcher_window.window_id != WindowID.LAUNCHER:
            return
        self.launcher_window.on_setup_completed(success)
        self.launcher_window.loading.stop_anim_screen()
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
        if self.launcher_window.publish_window is not None:
            self.launcher_window.publish_window.get_changes_list(changes, changes_modified)

    @Slot()
    def on_anim_rep_publishing(self):
        self.launcher_window.loading.show_anim_screen()

    @Slot()
    def on_anim_rep_publishing_completed(self):
        self.launcher_window.loading.stop_anim_screen()

    @Slot()
    def on_login(self):
        self.launcher_window.logger_widget.clear_log()

    @Slot()
    def on_anim_upload_files_started(self):
        self.launcher_window.loading.show_anim_screen()

    @Slot()
    def on_anim_upload_files_completed(self):
        self.launcher_window.loading.stop_anim_screen()

    @Slot()
    def on_setup_no_directory(self):
        self.select_directory_window = SelectDirectoryWindow()
        self.select_directory_window.directory_selected.connect(self.test_select_dir)
        self.select_directory_window.show()

    @Slot(str)
    def test_select_dir(self, path):
        self.sdw_select_directory.emit(path)
