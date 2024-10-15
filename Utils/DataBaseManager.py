from PySide6.QtCore import QObject, Signal, Slot
from Model.UserModel import UserModel
from Model.UserRolesModel import UserRolesModel
from Utils.ConfigFileManager import ConfigFileManager
from Utils.DataBaseConnection import DataBaseConnection
from Utils import FileManager
import Utils.Environment as Env


class DataBaseManager(QObject):
    error_message_signal = Signal(str)
    message_signal = Signal(str)
    db_setup_start = Signal()
    db_setup_done = Signal()


    def __init__(self, config_manager=None, database_conn=None, file_manager=FileManager,
                 role_model=None, user_model=None):
        super(DataBaseManager, self).__init__()
        self.config_manager = config_manager or ConfigFileManager()
        self.config = None  # Load config when needed
        self.database_conn = database_conn or DataBaseConnection()
        self.file_manager = file_manager
        self.role_model = role_model or UserRolesModel()
        self.user_model = user_model or UserModel()

    @Slot()
    def setup_db(self):
        self.db_setup_start.emit()

        if self.file_manager.file_exist(Env.DB_NAME):
            self.message_signal.emit(f"file: {Env.DB_NAME} already exists, skipping db setup")
            self.db_setup_done.emit()
            return

        self.config = self.config_manager.get_config()  # Load config here
        self.initialize_database()
        self.db_setup_done.emit()

    def initialize_database(self):
        db_dir = self.file_manager.join_with_local_path(Env.DB_NAME)

        if not self.file_manager.dir_exist(db_dir):
            self.file_manager.create_dir(db_dir)

        self.create_roles()
        self.create_users()

    def create_roles(self):
        if not self.table_exists('roles'):
            self.role_model.create_table()

        for role in self.get_roles():
            if not self.role_model.role_exists(role):
                self.role_model.add_role(role)

    def create_users(self):
        if not self.table_exists('users'):
            self.user_model.create_table()

        users = self.get_users()
        for index, user in enumerate(users["user_names"]):
            if not self.user_model.user_exists(user):
                role_name = users["roles"][index]
                role = self.role_model.get_role_by_name(role_name)
                if role is not None:
                    email = users["emails"][index]
                    password = users["default_password"]
                    self.user_model.add_user(user, password, email, role[0])

    def table_exists(self, table_name: str):
        return self.database_conn.execute_query_fetchone('''
            SELECT name FROM sqlite_master WHERE type='table' AND name=?
        ''', (table_name,)) is not None

    def get_roles(self):
        return self.config.get('db', {}).get('roles', {}).get('names', [])

    def get_users(self):
        user_config = self.config.get('db', {}).get('users', {})
        return {
            "user_names": user_config.get('user_names', []),
            "default_password": user_config.get('default_password', ''),
            "emails": user_config.get('emails', []),
            "roles": user_config.get('roles', [])
        }
