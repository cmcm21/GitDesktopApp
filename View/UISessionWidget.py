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
from View.BaseWindow import BaseWindow
from View.CustomStyleSheetApplier import CustomStyleSheetApplier


class UserSessionWidget(QWidget):
    logout_signal = Signal()

    def __init__(self):
        super(UserSessionWidget, self).__init__()
        self.user_label = QLabel()
        self.user_label.setObjectName("UserLabel")
        """ User Actions """
        self.user_action = QAction(QIcon(QPixmap(FileManager.get_img_path("singleplayer.png"))), "User", self)
        self.user_action.setStatusTip("User session")
        self.user_action.setChecked(True)

        self.logout_action = QAction(QIcon(QPixmap(FileManager.get_img_path('exit.png'))), "Logout", self)
        self.logout_action.setStatusTip("Logout")
        self.logout_action.setChecked(True)
        self.frame = BaseWindow.create_default_frame("UserSessionFrame")
        """ layouts """
        self.layout = QHBoxLayout(self)
        self.main_layout = QVBoxLayout(self)
        """ Toolbar """
        self.toolbar = QToolBar()
        self.toolbar.setObjectName("SessionToolbar")

        self.connect_user_button()
        self._build()

    def _build(self):
        self.layout.addWidget(self.toolbar)
        self.frame.setLayout(self.layout)
        self.frame.layout().addWidget(self.toolbar)
        self.main_layout.addWidget(self.frame)
        self.setLayout(self.layout)
        """Toolbar"""
        self.toolbar.addWidget(self.user_label)
        self.toolbar.addAction(self.user_action)
        self.toolbar.addAction(self.logout_action)
        self.toolbar.adjustSize()

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
            self.user_action.setText(user_session.username)
            self.user_label.setText(user_session.username)

    def set_styles(self):
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.user_label)

    def on_user_action_triggered(self, action):
        return
