import sqlite3
from Utils.Environment import *
from contextlib import contextmanager
from Utils.SingletonMeta import SingletonMeta


class DataBaseConnection(metaclass=SingletonMeta):

    def __init__(self):
        self.db_file = DB_NAME
        self.conn = None

    @contextmanager
    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query, params=()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()

    def execute_query_fetchall(self, query: str, params=()) -> list:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()

    def execute_query_fetchone(self, query: str, params=()) -> tuple:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchone()
