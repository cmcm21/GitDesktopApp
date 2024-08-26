from Utils.SingletonMeta import SingletonMeta
from Controller.UserController import UserController


class UserSession(metaclass=SingletonMeta):
    _instance = None
    user_id = -1
    username = ""
    email = ""
    role = ""
    role_id = -1

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance.user = None
        return cls._instance

    def login(self, username):
        user_controller = UserController()
        user_data = user_controller.get_user(username)
        if user_data:
            self.user_id = user_data[0]
            self.username = user_data[1]
            self.email = user_data[3]
            self.role = user_data[4]
            self.role_id = user_data[5]

    def logout(self):
        self.user_id = -1
        self.username = ""
        self.email = ""
        self.role = ""
        self.role_id = -1

    def is_logged_in(self):
        return self.user is not None

    def __str__(self):
        return f"user: [{self.user_id}, {self.username}, {self.email}, {self.role}, {self.role_id}"
