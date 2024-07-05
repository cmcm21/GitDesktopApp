from View.LauncherWindow import LauncherWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Slot, Signal, QObject
from View.WindowID import WindowID


class UIManager(QObject):
    """Launcher window buttons signals"""
    lw_get_latest_clicked = Signal()
    lw_uploaded_clicked = Signal(str)
    lw_open_maya_clicked = Signal()
    lw_new_workspace_clicked = Signal()
    lw_window_closed = Signal()
    lw_get_merge_request_changed = Signal(int)
    lw_merge_request_add_comment = Signal(str, int)
    lw_accept_merge_request_and_merge = Signal(int, str)

    def __init__(self, config: dict):
        super().__init__()
        self.launcher_window = LauncherWindow(config, WindowID.LAUNCHER)
        self.logger = self.launcher_window.logger_widget.logger
        self.connect_button: QPushButton = self.launcher_window.connect_button
        self.windows = {
            WindowID.LAUNCHER: self.launcher_window
        }
        self.config = config
        self._connect_launcher_windows()

    def open_window(self, window_id: WindowID):
        if window_id not in self.windows:
            return

        if self.launcher_window is not None:
            self.launcher_window.close()

        self.launcher_window = self.windows[window_id]
        self.launcher_window.open()

    def _connect_launcher_windows(self):
        """ Using UIManager signals to make a bridge between UI Signals and Controllers """
        self.lw_git_history_tab_clicked = self.launcher_window.git_tab.history_tab_clicked
        self.lw_git_changes_list_tab_clicked = self.launcher_window.git_tab.changes_list_clicked
        self.lw_git_merge_request_tab_clicked = self.launcher_window.git_tab.merge_request_clicked
        self.lw_get_latest_clicked = self.launcher_window.git_tab.download_btn.clicked
        self.lw_uploaded_clicked = self.launcher_window.upload_repository_signal
        self.lw_open_maya_clicked = self.launcher_window.maya_btn.clicked
        self.lw_window_closed = self.launcher_window.window_closed
        self.lw_get_merge_request_changed = self.launcher_window.git_tab.git_sniffer.merge_request.selected_mr_changed
        self.lw_merge_request_add_comment = self.launcher_window.git_tab.git_sniffer.merge_request.add_comment
        self.lw_accept_merge_request_and_merge = self.launcher_window.git_tab.git_sniffer.merge_request.accept_and_merge

    @Slot(bool)
    def on_setup_completed(self, success: bool):
        if self.launcher_window.window_id != WindowID.LAUNCHER:
            return
        self.launcher_window.on_setup_completed(success)

    @Slot(str)
    def on_log_signal_received(self, log_message: str):
        self.logger.debug(log_message)

    @Slot(str)
    def on_err_signal_received(self, error_message: str):
        self.logger.error(error_message)

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

    @Slot(list)
    def on_get_merge_request_commits(self, merge_request_commits: list):
        self.launcher_window.git_tab.set_merge_request_commits(merge_request_commits)
        return

    @Slot(list)
    def on_get_merge_request_changes(self, changes: list):
        self.launcher_window.git_tab.set_merge_request_changes(changes)

    @Slot(list)
    def on_get_merge_requests_comments(self, comments: list):
        self.launcher_window.git_tab.set_merge_requests_comments(comments)

