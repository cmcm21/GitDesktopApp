from PySide6.QtCore import QObject, Signal, Slot
from Model.UserRolesModel import UserRolesModel
from Model.UserModel import UserModel
import re
import bleach
import validators
import bcrypt


class UserController(QObject):
    error_message = Signal(str)
    log_message = Signal(str)

    def __init__(self):
        super(UserController, self).__init__()
        self.user_model = UserModel()
        self.role_model = UserRolesModel()
        self.connect_user_model()

    def check_user(self, username, password) -> bool:
        if not self.validate_username(username):
            return False
        clean_username = self.sanitize_input(username)
        stored_password = self.user_model.get_password(username)
        if stored_password != "":
            return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))

        return False

    def connect_user_model(self):
        self.user_model.error_message_signal = self.error_message
        self.user_model.message_signal = self.log_message

    def add_user(self, username: str, password: str, email: str, role_id: int) -> bool:
        if not self.validate_username(username):
            print("Invalid Username, use just characters, numbers and hyphens ")
            self.error_message.emit("Invalid Username, use just characters, numbers and hyphens ")
            return False

        if not self.validate_password(password):
            print("Invalid password, password should be at least 8 characters long")
            self.error_message.emit("Invalid password, password shouldbe at least 8 characters long")
            return False

        if not self.validate_email(email):
            print("Invalid email, verify your email address")
            self.error_message.emit("Invalid email, verify your email address")
            return False

        if not self.role_model.role_exists(role_id):
            print(f"Invalid role, role: {role_id} doesn't exist")
            self.error_message.emit(f"Invalid role, role: {role_id} doesn't exist")
            return False

        clean_username = self.sanitize_input(username)
        clean_password = self.sanitize_input(password)
        clean_email = self.sanitize_input(email)

        if self.user_model.add_user(clean_username, clean_password, clean_email, role_id):
            self.user_model.message_signal.emit(f"User : {username} added to database correctly")
            return True
        else:
            print("error in User model trying to add a new user")
            return False

    def get_user(self, username: str) -> tuple:
        return self.user_model.get_user_by_username(username)

    @staticmethod
    def validate_username(username):
        # Username must be alphanumeric and between 3 and 30 characters
        return re.match(r'^[a-zA-Z0-9_-]{3,30}$', username) is not None

    @staticmethod
    def validate_password(password):
        # Example: Password must be at least 8 characters long
        return len(password) >= 8

    @staticmethod
    def validate_email(email):
        # Use validators library to validate email format
        return validators.email(email)

    @staticmethod
    def sanitize_input(user_input):
        # Allow only safe HTML tags
        allowed_tags = ['b', 'i', 'u', 'em', 'strong']
        return bleach.clean(user_input, tags=allowed_tags, strip=True)


