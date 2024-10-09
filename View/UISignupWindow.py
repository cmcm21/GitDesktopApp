from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QMainWindow,
    QMessageBox
)
from Utils.Environment import RoleID
from View.EnterButton import EnterButton
from View import CustomStyleSheetApplier
from Model.UserRolesModel import UserRolesModel
from Controller.UserController import UserController
from PySide6.QtCore import Signal, Qt
from enum import Enum
import re


class ErrorInputCode(Enum):
    LONG_USERNAME = 1
    INVALID_EMAIL = 2
    INVALID_PASSWD = 3
    EMPTY_FIELDS = 4


class SignUpForm(QMainWindow):
    error_message = Signal(str)
    log_message = Signal(str)

    def __init__(self, user_controller: UserController):
        super().__init__()
        self.setWindowTitle("Sing up window")
        # Create widgets

        self.create_username_field()
        self.create_email_field()
        self.create_select_role()
        self.create_password()
        self.create_reenter_password()

        self.signup_button = EnterButton('Sign Up', self)
        self._build()
        self.apply_styles()
        self.user_controller = user_controller
        self.connect_signals()

    def create_username_field(self):
        self.username_label = QLabel('User Name:')
        self.username_input = QLineEdit()

    def create_email_field(self):
        self.email_label = QLabel('Email:')
        self.email_input = QLineEdit()

    def create_select_role(self):
        self.role_label  = QLabel('User Role:')
        self.role_combo_box = QComboBox()
        self.role_combo_box.addItem("Animator", userData=RoleID.ANIMATOR.value)
        self.role_combo_box.addItem("Developer", userData=RoleID.DEV.value)

        self.role_combo_box.currentIndexChanged.connect(self.on_combo_box_changed)

    def on_combo_box_changed(self):
        return

    def create_password(self):
        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

    def create_reenter_password(self):
        self.reenter_password_label = QLabel('Re-enter Password:')
        self.reenter_password_input = QLineEdit()
        self.reenter_password_input.setEchoMode(QLineEdit.Password)

    def _build(self):
        # Create form layout and add widgets
        form_layout = QFormLayout()
        form_layout.addRow(self.username_label, self.username_input)
        form_layout.addRow(self.email_label, self.email_input)
        form_layout.addRow(self.role_label, self.role_combo_box)
        form_layout.addRow(self.password_label, self.password_input)
        form_layout.addRow(self.reenter_password_label, self.reenter_password_input)

        # Create main layout and add form layout and button
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.signup_button)

        # Set the layout for the main widget
        self.setLayout(main_layout)

        # Set window title and fixed size
        self.setFixedSize(400, 250)

        # Add the main layout
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def connect_signals(self):
        self.signup_button.clicked.connect(self.signup)
        self.user_controller.error_message.connect(lambda message: self.error_message.emit(message))
        self.user_controller.log_message.connect(lambda message: self.log_message.emit(message))

        self.username_input.returnPressed.connect(self.signup)
        self.email_input.returnPressed.connect(self.signup)
        self.reenter_password_input.returnPressed.connect(self.signup)
        self.password_input.returnPressed.connect(self.signup)

    def signup(self):
        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()
        re_password = self.reenter_password_input.text()

        role_model = UserRolesModel()
        if self.validate_inputs(username, email, password ,re_password):
            role_id = self.role_combo_box.currentData(Qt.ItemDataRole.UserRole)
            default_role_id = role_model.get_role_id(role_id)
            if default_role_id:
                if self.user_controller.add_user(username, password, email, default_role_id[0]):
                    self.close()
                else:
                    self.error_message.emit(f"Error trying to add user: {username}")
            else:
                self.error_message.emit(f"Error trying to add user: {username} user role invalid")
        return

    def validate_inputs(self, username: str, email: str, password: str, reenter_password: str):
        # Validate username
        if not username.strip():
            QMessageBox.warning(self, "Input Error", "Username cannot be empty.")
            return False

        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return False

        # Validate password
        if len(password) < 6:
            QMessageBox.warning(self, "Input Error", "Password must be at least 6 characters long.")
            return False

        # Validate re-enter password
        if password != reenter_password:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return False

        return True

    def apply_styles(self):
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.username_input)
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.email_input)
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.password_input)
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.reenter_password_input)
        CustomStyleSheetApplier.set_combo_box_style_and_colour(self.role_combo_box)
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.signup_button, colour="Yellow")
