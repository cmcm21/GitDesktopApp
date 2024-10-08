from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QHBoxLayout,
    QToolBar
)
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtCore import Signal
from Utils.UserSession import UserSession
from Utils import FileManager
from Utils.Environment import RoleID
from View.CustomStyleSheetApplier import CustomStyleSheetApplier


class UserSessionWidget(QWidget):
    logout_signal = Signal()
    admin_signal = Signal()
    switch_account_signal = Signal(RoleID)

    def __init__(self):
        super(UserSessionWidget, self).__init__()
        self.user_session = UserSession()
        self.user_label = QLabel()
        self.user_label.setObjectName("UserLabel")
        """ User Actions """
        self.user_action = QAction(QIcon(QPixmap(FileManager.get_img_path("singleplayer.png"))), "Settings", self)
        self.user_action.setStatusTip("User session")
        self.user_action.setChecked(True)

        self.logout_action = QAction(QIcon(QPixmap(FileManager.get_img_path('exit.png'))), "Logout", self)
        self.logout_action.setStatusTip("Logout")
        self.logout_action.setChecked(True)

        self.switch_account = None
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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()

    def set_user(self):
        user_session = UserSession()
        if user_session is not None:
            self.user_label.setText(f"{user_session.username}: ({user_session.role})")

    def get_admin_action(self) -> QAction:
        self.admin_action = QAction(QIcon(QPixmap(FileManager.get_img_path("admin.png"))), "Admin", self)
        self.admin_action.triggered.connect(lambda: self.admin_signal.emit())
        return self.admin_action

    def get_switch_account_action(self) -> QAction:
        self.switch_account = QAction(QIcon(QPixmap(FileManager.get_img_path("switch_account.png"))), "Switch User Role", self)
        switch_to = RoleID.ADMIN_ANIM if self.user_session.role_id == RoleID.ADMIN.value else RoleID.ADMIN

        self.switch_account.setStatusTip(f"Switch to {switch_to}")
        self.switch_account.triggered.connect(lambda: self.switch_account_signal.emit(switch_to))
        return self.switch_account

    def set_styles(self):
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.user_label)

    def on_user_action_triggered(self, action):
        return
