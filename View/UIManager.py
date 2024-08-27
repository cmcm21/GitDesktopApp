from Utils.ConfigFileManager import ConfigFileManager
from Utils.Environment import ROLE_ID
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

    lw_publish_to_anim = Signal(str)
    lw_uploaded_clicked = Signal(str)
    lw_get_merge_request_changed = Signal(int)
    lw_merge_request_add_comment = Signal(str, int)
    lw_accept_merge_request_and_merge = Signal(int, str)
    lw_file_tree_clicked = Signal(str)
    sdw_select_directory = Signal(str)
    lw_switch_account = Signal(ROLE_ID)
    lg_login_accepted = Signal(str)

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

        # Define a list of (signal, slot) tuples
        connections = [
            (self.launcher_window.git_tab.history_tab_clicked, 'lw_git_history_tab_clicked'),
            (self.launcher_window.git_tab.changes_list_clicked, 'lw_git_changes_list_tab_clicked'),
            (self.launcher_window.git_tab.merge_request_clicked, 'lw_git_merge_request_tab_clicked'),
            (self.launcher_window.maya_btn.clicked, 'lw_open_maya_clicked'),
            (self.launcher_window.get_latest, 'lw_get_latest_clicked'),
            (self.launcher_window.upload_repository, 'lw_uploaded_clicked'),
            (self.launcher_window.window_closed, 'lw_window_closed'),
            (self.launcher_window.application_destroyed, 'lw_destroy_application'),
            (self.launcher_window.log_out, 'lw_log_out')
        ]

        self.launcher_window.git_tab.git_sniffer.merge_request.selected_mr_changed.connect(
            lambda index: self.lw_get_merge_request_changed(index))

        self.launcher_window.git_tab.git_sniffer.merge_request.add_comment.connect(
            lambda comment: self.lw_merge_request_add_comment(comment))

        self.launcher_window.git_tab.git_sniffer.merge_request.accept_and_merge.connect(
            lambda comment: self.lw_accept_merge_request_and_merge(comment))

        self.launcher_window.git_tab.repository_viewer.file_selected.connect(
            lambda file_path: self.lw_file_tree_clicked.emit(file_path))

        self.launcher_window.publish_to_anim_rep.connect(
            lambda comment: self.lw_publish_to_anim.emit(comment))

        self.launcher_window.switch_account.connect(
            lambda role_id: self.lw_switch_account.emit(role_id))

        # Connect each no-parameters-signal to the corresponding attribute
        for signal, attr_name in connections:
            print(f"Connecting {signal} with {attr_name} ")
            setattr(self, attr_name, signal)
            #signal.connect( lambda : self.emit_signal_wrapper(signal, attr_name) )

        # Additional connections
        self.lw_destroy_application.connect(self._on_application_destroyed)
        self.login_window.application_destroyed.connect(self._on_application_destroyed)

    def emit_signal_wrapper(self, signal:str, attr_name:str):
        print(f"{signal} was triggered")
        getattr(self, attr_name).emit()

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

    @Slot()
    def on_anim_rep_creating(self):
        self.launcher_window.loading.show_anim_screen()

    @Slot()
    def on_anim_rep_creation_completed(self):
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
