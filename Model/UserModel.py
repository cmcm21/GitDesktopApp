from PySide6.QtCore import QObject, Signal, Slot, QThread
from Utils.DataBaseConnection import DataBaseConnection
import bcrypt
import sqlite3


class UserModel(QObject):
    error_message_signal = Signal(str)
    message_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.conn = DataBaseConnection()

    def create_table(self):
        try:
            self.conn.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                role_id INTEGER,
                FOREIGN KEY (role_id) REFERENCES roles (id)
            )
            ''')
            self.message_signal.emit("user data table created!!")
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while creating the users table: {e}")
            print(f"An error occurred while creating the users table: {e}")

    def add_user(self, username: str, password: str, email: str, role_id: int) -> bool:
        try:
            hash_passwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.conn.execute_query('''
            INSERT INTO users (username, password, email, role_id)
            VALUES (?, ?, ?, ?)
            ''', (username, hash_passwd.decode('utf-8'), email, role_id))
            self.message_signal.emit(f"user : {username} was added to data base successfully!!")
            return True
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while adding a user: {username}")
            return False

    def get_password(self, username: str) -> str:
        try:
            user_passwd = self.conn.execute_query_fetchone(
                "SELECT password FROM users WHERE username=?", (username,))
            if user_passwd and isinstance(user_passwd[0], str):
                return user_passwd[0]
            return ""
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while getting password: {e}")
            print(f"An error occurred while checking user: {e}")
            return ""

    def get_user_by_id(self, user_id: int) -> tuple:
        try:
            return self.conn.execute_query_fetchone('''
            SELECT users.id, users.username, users.password, users.email, roles.user_role, users.role_id
            FROM users
            JOIN roles ON users.role_id = roles.id
            WHERE users.id = ?
            ''', (user_id,))
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while retrieving the user: {e}")
            print(f"An error occurred while retrieving the user: {e}")

    def get_user_by_username(self, username: str) -> tuple:
        try:
            return self.conn.execute_query_fetchone('''
            SELECT users.id, users.username, users.password, users.email, roles.user_role, users.role_id
            FROM users
            JOIN roles ON users.role_id = roles.id
            WHERE users.username = ?
            ''', (username,))
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while retrieving the user: {e}")
            print(f"An error occurred while retrieving the user: {e}")

    def update_user(self, user_id: int, username: str, password: str, email: str, role_id: int):
        try:
            self.conn.execute_query('''
            UPDATE users
            SET username = ?, password = ?, email = ?, role_id = ?
            WHERE id = ?
            ''', (username, password, email, role_id, user_id))
            self.message_signal.emit(f"user: {username} was updated in data base successfully!!")
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while updating the user: {e}")
            print(f"An error occurred while updating the user: {e}")

    def delete_user_by_id(self, user_id: int):
        try:
            self.conn.execute_query(''' DELETE FROM users WHERE id = ? ''', (user_id,))
            self.message_signal.emit(f"user: {user_id} was deleted from data base successfully!!")
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while deleting the user: {e}")
            print(f"An error occurred while deleting the user: {e}")

    def delete_user(self, username: str):
        try:
            self.conn.execute_query(''' DELETE FROM users WHERE username = ? ''', (username,))
            self.message_signal.emit(f"user: {username} was deleted from data base successfully!!")
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while deleting the user: {e}")
            print(f"An error occurred while deleting the user: {e}")

    def user_exists(self, username: str):
        try:
            return self.conn.execute_query_fetchone('''
            SELECT 1 FROM users WHERE username = ?
            ''', (username,)) is not None
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while checking if the user exists: {e}")
            print(f"An error occurred while checking if the user exists: {e}")
            return False

    def get_all_users(self):
        try:
            return self.conn.execute_query('''
            SELECT users.id, users.username, users.password, users.email, roles.user_role
            FROM users
            JOIN roles ON users.role_id = roles.id
            ''')
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while retrieving all users: {e}")
            print(f"An error occurred while retrieving all users: {e}")
            return []

    def get_all_users_table(self):
        try:
            return self.conn.execute_query('''
            SELECT users.username, users.email, roles.user_role
            FROM users
            JOIN roles ON users.role_id = roles.id
            ''')
        except sqlite3.Error as e:
            self.error_message_signal.emit(f"An error occurred while retrieving all users: {e}")
            print(f"An error occurred while retrieving all users: {e}")
            return []
