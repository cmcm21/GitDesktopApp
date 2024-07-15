from View.BaseWindow import BaseWindow
from View.WindowID import WindowID
from View.UILogger import LoggerWidget
from View.UICommitWindow import CommitWindow
from View.UIGitTab import UIGitTab
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.UILoadingWidget import LoadingWidget
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QComboBox,
    QTabWidget,
)
from PySide6.QtCore import Qt, Signal, Slot, QSize


class LauncherWindow(BaseWindow):
    upload_repository_signal = Signal(str)
    download_repository_signal = Signal()
    project_changed = Signal(str)
    window_closed = Signal()

    def __init__(self, config: dict, window_id: WindowID, width=900, height=500):
        super(LauncherWindow, self).__init__("Puppet Launcher", window_id, width, height)
        self.config = config
        self.commit_window = None
        self._create_all_element()
        self._build()
        self._connect_buttons()

    def _create_all_element(self):
        """ Layouts """
        self.main_layout = QGridLayout()
        self.header_layout = QHBoxLayout()
        self.body_layout = QHBoxLayout()
        self.body_left = QVBoxLayout()
        self.body_right = QVBoxLayout()
        self.footer_layout = QHBoxLayout()
        """Combo box button"""
        self.project_combo_box = QComboBox()
        self.project_combo_box.addItems(["EDO"])
        self.project_combo_box.setFixedSize(QSize(150, 30))
        CustomStyleSheetApplier.set_combo_box_style_and_colour(self.project_combo_box, "White")
        self.project_combo_box.objectNameChanged.connect(self.project_selected_changed)
        """ New Workspace Button """
        self.new_workspace_btn = self.create_button(self, "plus.png", "")
        self.new_workspace_btn.setToolTip("New Workspace")
        self.new_workspace_btn.setObjectName("NewWorkspaceButton")
        self.new_workspace_btn.setFixedSize(QSize(80, 40))
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.new_workspace_btn, "Black")
        """ Open Maya Button """
        self.maya_btn = self.create_button(self, "mayaico.png", "")
        self.maya_btn.setToolTip("Open Maya")
        self.maya_btn.setObjectName("MayaButton")
        self.maya_btn.setFixedSize(QSize(80, 40))
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.maya_btn, "Black")
        """settings Button"""
        self.settings_btn = self.create_button(self, "gear.png", "")
        self.settings_btn .setToolTip("Open Settings")
        self.settings_btn.setObjectName("SettingsButton")
        self.settings_btn.setFixedSize(QSize(80, 40))
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.settings_btn, "Black")
        """Other Widgets"""
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

    def _build(self):
        """ Connect Button """
        self.connect_button = self.create_button(self, "singleplayer.png", "Connect")
        self.connect_button.setObjectName("ConnectButton")
        """ Header """
        self.header_layout.addWidget(self.project_combo_box, 0, Qt.AlignmentFlag.AlignLeft)
        self.header_layout.addWidget(self.loading, 0, Qt.AlignmentFlag.AlignRight)
        self.header_layout.setSpacing(0)
        """ Body left """
        self.left_frame.setLayout(self.body_left)
        self.left_frame.layout().addWidget(self.new_workspace_btn, 0, Qt.AlignmentFlag.AlignTop)
        self.left_frame.layout().addWidget(self.maya_btn, 0, Qt.AlignmentFlag.AlignTop)
        self.left_frame.layout().addWidget(self.settings_btn, 5, Qt.AlignmentFlag.AlignTop)
        self.left_frame.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        """Tabs"""
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
        self.main_layout.addLayout(self.header_layout, 0, 0)
        self.main_layout.addLayout(self.body_layout, 1, 0)
        self.main_layout.addLayout(self.footer_layout, 2, 0)
        self.main_layout.setSpacing(10)
        """ Set Main Layout """
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def _connect_buttons(self):
        self.git_tab.upload_btn.clicked.connect(self, self.create_commit_windows)
        self.git_tab.download_btn.clicked.connect(lambda: self.download_repository_signal.emit())

    def create_commit_windows(self):
        self.commit_window = CommitWindow()
        self.commit_window.accept_clicked_signal.connect(self._on_commit_window_accept)
        self.commit_window.cancel_clicked_signal.connect(self._on_commit_window_cancel)
        self.commit_window.show()

    def project_selected_changed(self):
        return

    @Slot(str)
    def _on_commit_window_accept(self, message):
        self.upload_repository_signal.emit(message)
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

    def _close_commit_window(self):
        if self.commit_window is not None:
            self.commit_window.close()
            self.commit_window = None

    def on_setup_completed(self, success: bool):
        self.git_tab.on_repository_path_updated()
