from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import Qt, Signal
from View.BaseWindow import BaseWindow
from View.WindowID import WindowID
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.UISignupWindow import SignUpForm


class LoginWindow(BaseWindow):
    login_signal = Signal()
    sign_up_signal = Signal()

    def __init__(self, window_id: WindowID, width=350, height=450):
        super(LoginWindow, self).__init__("Login", window_id, width, height)
        self.setFixedSize(width, height)
        # Create widgets
        self.user_icon = QLabel()
        self.user_icon.setPixmap(self.get_pixmap("singleplayer.png"))
        self.icon_frame = self.create_default_frame("IconFrame")
        self.icon_frame.setFixedSize(160, 150)
        self.user_icon.setFixedSize(90, 80)

        self.user_icon.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.username_label = QLabel('Username:')
        self.username_label.adjustSize()
        self.username_input = QLineEdit()

        self.password_label = QLabel('Password:')
        self.password_label.adjustSize()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('Login')
        self.signup_button = QPushButton('Sign Up')

        self.frame = self.create_default_frame("LoginFrame")

        # Create layouts
        self.icon_layout = QVBoxLayout()
        self.username_layout = QHBoxLayout()
        self.username_layout.setContentsMargins(0, 0, 0, 0)
        self.username_layout.setSpacing(0)
        self.password_layout = QHBoxLayout()
        self.password_layout.setContentsMargins(0, 0, 0, 0)
        self.password_layout.setSpacing(0)
        self.main_layout = QVBoxLayout()
        self.form_layout = QVBoxLayout()
        self.button_layout = QVBoxLayout()

        # Set window title
        self.setWindowTitle('Login')
        self._build()
        self.apply_styles()
        self.connect_signals()

    def _build(self):
        # Config Label
        self.username_label.setFont(QFont("Courier New", 10))
        self.password_label.setFont(QFont("Courier New", 10))

        # Config Buttons
        self.login_button.setFixedSize(128, 30)
        self.signup_button.setFixedSize(128, 30)

        # Set frames
        self.frame.setLayout(self.form_layout)
        self.icon_frame.setLayout(self.icon_layout)
        self.icon_frame.layout().addWidget(self.user_icon)
        self.icon_frame.layout().setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Add widgets to form layout
        self.frame.layout().addWidget(self.icon_frame, 0, Qt.AlignmentFlag.AlignHCenter)
        self.username_layout.addWidget(self.username_label, 0, Qt.AlignmentFlag.AlignHCenter)
        self.username_layout.addWidget(self.username_input, 0, Qt.AlignmentFlag.AlignHCenter)
        self.frame.layout().addLayout(self.username_layout)

        self.password_layout.addWidget(self.password_label, 0, Qt.AlignmentFlag.AlignHCenter)
        self.password_layout.addWidget(self.password_input, 0, Qt.AlignmentFlag.AlignHCenter)
        self.frame.layout().addLayout(self.password_layout)

        # Add buttons to button layout
        self.button_layout.addWidget(self.login_button, 0, Qt.AlignmentFlag.AlignHCenter)
        self.button_layout.addWidget(self.signup_button, 0, Qt.AlignmentFlag.AlignHCenter)
        self.frame.layout().addLayout(self.button_layout)

        # Add form layout and button layout to main layout
        self.main_layout.addWidget(self.frame)

        # Add the main layout
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def connect_signals(self):
        self.signup_button.clicked.connect(self.on_signup_clicked)

    def on_signup_clicked(self):
        self.sign_up_window = SignUpForm()
        self.sign_up_window.show()

    def apply_styles(self):
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.username_input, colour="White")
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.password_input, colour="White")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.login_button, colour="Blue")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.signup_button, colour="Blue")

