from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtCore import Qt, Signal, Slot
from View.BaseWindow import BaseWindow
from View.WindowID import WindowID
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.UISignupWindow import SignUpForm
from Controller.UserController import UserController
from Model.UserRolesModel import UserRolesModel
import Utils.Environment as Env


class LoginWindow(BaseWindow):
    login_signal = Signal(str)
    sign_up_signal = Signal()

    def __init__(self, window_id: WindowID, width=350, height=450):
        super(LoginWindow, self).__init__("Login", window_id, width, height)
        self.sign_up_window = None
        self.setFixedSize(width, height)
        # Create widgets
        self.user_icon = QLabel()
        self.user_icon.setPixmap(self.get_pixmap("singleplayer.png"))
        self.icon_frame = self.create_default_frame("IconFrame")
        self.icon_frame.setFixedSize(160, 150)
        self.user_icon.setFixedSize(90, 80)
        self.error_label = QLabel()

        # Username
        self.user_icon.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.username_label = QLabel('Username:')
        self.username_label.adjustSize()
        self.username_input = QLineEdit()

        # Password
        self.password_label = QLabel('Password:')
        self.password_label.adjustSize()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        # Buttons
        self.login_button = QPushButton('Login')
        self.signup_button = QPushButton('Sign Up')

        # Create layouts
        self.frame = self.create_default_frame("LoginFrame")
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

        # Controllers and Models
        self.user_controller = UserController()
        self.role_model = UserRolesModel()

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
        self.icon_frame.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets to form layout
        self.frame.layout().addWidget(self.icon_frame, 0, Qt.AlignmentFlag.AlignCenter)
        self.username_layout.addWidget(self.username_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.username_layout.addWidget(self.username_input, 0, Qt.AlignmentFlag.AlignCenter)
        self.frame.layout().addLayout(self.username_layout)

        self.password_layout.addWidget(self.password_label, 0, Qt.AlignmentFlag.AlignCenter)
        self.password_layout.addWidget(self.password_input, 0, Qt.AlignmentFlag.AlignCenter)
        self.frame.layout().addLayout(self.password_layout)

        # Add buttons to button layout
        self.button_layout.addWidget(self.login_button, 0, Qt.AlignmentFlag.AlignCenter)
        self.button_layout.addWidget(self.signup_button, 0, Qt.AlignmentFlag.AlignCenter)
        self.frame.layout().addLayout(self.button_layout)

        # Add Error label
        self.frame.layout().addWidget(self.error_label, 0, Qt.AlignmentFlag.AlignCenter)

        # Add form layout and button layout to main layout
        self.main_layout.addWidget(self.frame)
        self.main_layout.addWidget(self.loading)

        # Add the main layout
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def connect_signals(self):
        self.signup_button.clicked.connect(self.on_signup_clicked)
        self.login_button.clicked.connect(self.on_check_login)
        self.user_controller.log_message.connect(self.log)
        self.user_controller.error_message.connect(self.log_error)

    def on_check_login(self):
        self.loading.show_anim_screen()
        username = self.username_input.text()
        password = self.password_input.text()
        if password == "" or username == "":
            self.loading.stop_anim_screen()
            return

        if not self.user_controller.check_user(username, password):
            self.log_error("There was an error trying to login, username or password is incorrect")
        else:
            Env.SEASON_USER = self.user_controller
            self.login_signal.emit(username)

        self.loading.stop_anim_screen()

    def log_error(self, message: str):
        self.error_label.setStyleSheet("color: red;")
        self.show_label_message(message)

    def log(self, message: str):
        self.error_label.setStyleSheet("color: green;")
        self.show_label_message(message)

    def show_label_message(self, message:str):
        self.error_label.setText(message)
        self.error_label.adjustSize()
        self.error_label.setWordWrap(True)

    def on_signup_clicked(self):
        self.sign_up_window = SignUpForm(self.user_controller, self.role_model)
        self.sign_up_window.show()

    def apply_styles(self):
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.username_input, colour="White")
        CustomStyleSheetApplier.set_line_edit_style_and_colour(self.password_input, colour="White")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.login_button, colour="Blue")
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.signup_button, colour="Blue")

