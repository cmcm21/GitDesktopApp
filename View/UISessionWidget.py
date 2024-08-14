from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QToolBar,
    QMessageBox
)
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtCore import Signal
from Utils.UserSession import UserSession
from Utils.FileManager import FileManager
from View.CustomStyleSheetApplier import CustomStyleSheetApplier


class UserSessionWidget(QWidget):
    logout_signal = Signal()
    admin_signal = Signal()

    def __init__(self):
        super(UserSessionWidget, self).__init__()
        self.user_label = QLabel()
        self.user_label.setObjectName("UserLabel")
        """ User Actions """
        self.user_action = QAction(QIcon(QPixmap(FileManager.get_img_path("singleplayer.png"))), "Settings", self)
        self.user_action.setStatusTip("User session")
        self.user_action.setChecked(True)

        self.logout_action = QAction(QIcon(QPixmap(FileManager.get_img_path('exit.png'))), "Logout", self)
        self.logout_action.setStatusTip("Logout")
        self.logout_action.setChecked(True)

        self.admin_action = None
        self.main_layout = QVBoxLayout(self)

        self.connect_user_button()

    def connect_user_button(self):
        self.user_action.triggered.connect(self.on_user_action_triggered)
        self.logout_action.triggered.connect(self.on_logout_action_triggered)

    def on_logout_action_triggered(self, action):
        reply = QMessageBox.question(
            self,
            'Logout',
            'Are you sure you want to Logout?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.logout_signal.emit()

    def set_user(self):
        user_session = UserSession()
        if user_session is not None:
            self.user_label.setText(user_session.username)

    def get_admin_action(self) -> QAction:
        self.admin_action = QAction(QIcon(QPixmap(FileManager.get_img_path("admin.png"))), "Admin", self)
        self.admin_action.triggered.connect(lambda : self.admin_signal.emit())
        return self.admin_action

    def set_styles(self):
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.user_label)

    def on_user_action_triggered(self, action):
        return
