from PySide6.QtCore import QObject, Signal, Slot, QThread
from Utils.DataBaseConnection import DataBaseConnection
import sqlite3


class UserRolesModel(QObject):
    error_message_signal = Signal(str)
    message_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.conn = DataBaseConnection()

    def create_table(self):
        try:
            self.conn.execute_query('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_role TEXT NOT NULL UNIQUE
            )
            ''')
            self.message_signal.emit("roles table created successfully!!!")
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while creating the roles table: {e}")
            print(f"An error occurred while creating the roles table: {e}")

    def add_role(self, user_role: str):
        try:
            self.conn.execute_query('''
            INSERT INTO roles (user_role)
            VALUES (?)
            ''', (user_role,))
            self.message_signal.emit(f"New role: {user_role} was added successfully!!")
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while adding a role: {e}")
            print(f"An error occurred while adding a role: {e}")

    def get_role_id(self, user_role: int):
        try:
            return self.conn.execute_query_fetchone('''
            SELECT * FROM roles WHERE user_role = ?
            ''', (user_role, ))
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while retrieving the role id({user_role}): {e}")
            print(f"An error occurred while retrieving the role id({user_role}): {e}")
        return

    def get_role_by_name(self, role: str) -> tuple:
        try:
            return self.conn.execute_query_fetchone('''
            SELECT * FROM roles WHERE user_role = ?
            ''', (role,))
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while retrieving the role({role}): {e}")
            print(f"An error occurred while retrieving the role({role}): {e}")

    def get_all_roles(self) -> list:
        try:
            return self.conn.execute_query(''' SELECT * FROM roles ''')
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while retrieving all roles: {e}")
            print(f"An error occurred while retrieving all roles: {e}")
            return []

    def role_exists(self, role_id: int) -> bool:
        try:
            role = self.conn.execute_query_fetchone('''
            SELECT 1 FROM roles WHERE id = ?
            ''', (role_id,))
            return role is not None
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while checking if the role exists: {e}")
            print(f"An error occurred while checking if the role exists: {e}")
            return False
