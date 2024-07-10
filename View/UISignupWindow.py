from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QFormLayout
)
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.BaseWindow import BaseWindow
from View.WindowID import WindowID


class SignUpForm(BaseWindow):
    def __init__(self):
        super().__init__("Sign Up", WindowID.SIGNUP)
        # Create widgets
        self.username_label = QLabel('User Name:')
        self.username_input = QLineEdit()

        self.email_label = QLabel('Email:')
        self.email_input = QLineEdit()

        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.reenter_password_label = QLabel('Re-enter Password:')
        self.reenter_password_input = QLineEdit()
        self.reenter_password_input.setEchoMode(QLineEdit.Password)

        self.signup_button = QPushButton('Sign Up')
        self._build()
        self.apply_styles()

    def _build(self):
        # Create form layout and add widgets
        form_layout = QFormLayout()
        form_layout.addRow(self.username_label, self.username_input)
        form_layout.addRow(self.email_label, self.email_input)
        form_layout.addRow(self.password_label, self.password_input)
        form_layout.addRow(self.reenter_password_label, self.reenter_password_input)

        # Create main layout and add form layout and button
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.signup_button)

        # Set the layout for the main widget
        self.setLayout(main_layout)

        # Set window title and fixed size
        self.setFixedSize(300, 200)

        # Add the main layout
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def apply_styles(self):
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.username_input)
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.email_input)
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.password_input)
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.reenter_password_input)
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.signup_button, colour="Yellow")
