from PySide6.QtCore import QObject, Signal, Slot
from Model.UserModel import UserModel
from Model.UserRolesModel import UserRolesModel
from Utils.ConfigFileManager import ConfigFileManager
from Utils.DataBaseConnection import DataBaseConnection
from Utils.FileManager import FileManager
import Utils.Environment as Env


class DataBaseManager(QObject):
    error_message_signal = Signal(str)
    message_signal = Signal(str)
    db_setup_start = Signal()
    db_setup_done = Signal()

    def __init__(self):
        super(DataBaseManager, self).__init__()
        self.config_manager = ConfigFileManager()
        self.config = self.config_manager.get_config()
        self.database_conn = DataBaseConnection()

    @Slot()
    def setup_db(self):
        if FileManager.file_exist(Env.DB_NAME):
            self.message_signal.emit(f"file: {Env.DB_NAME} already exists, skipping db setup")
            return

        self.db_setup_start.emit()
        roles = self.config["db"]["roles"]["names"]
        users = self.config['db']['users']['user_names']
        default_passwrd = self.config['db']['users']['default_password']
        emails = self.config['db']['users']['emails']
        users_roles = self.config['db']['users']['roles']

        role_model = UserRolesModel()
        user_model = UserModel()
        db_dir = FileManager.join_with_local_path(Env.DB_NAME)

        if not FileManager.dir_exist(db_dir):
            FileManager.create_dir(db_dir)

        if not self.table_exists('roles'):
            role_model.create_table()

        if not self.table_exists('users'):
            user_model.create_table()

        for role in roles:
            if not role_model.role_exists(role):
                role_model.add_role(role)

        for index in range(len(users)):
            if not user_model.user_exists(users[index]):
                role = role_model.get_role_by_name(users_roles[index])
                if role is not None:
                    user_model.add_user(users[index], default_passwrd, emails[index], role[0])

        self.db_setup_done.emit()

    def table_exists(self, table_name: str):
        return self.database_conn.execute_query_fetchone('''
        SELECT name FROM sqlite_master WHERE type='table' AND name=?
        ''', (table_name,)) is not None
