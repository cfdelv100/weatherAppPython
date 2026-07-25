import sqlite3

from src.config import DATABASE_PATH


class UserRepository:
    def __init__(self, database_path: str = DATABASE_PATH):
        self.database_path = database_path

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def create_user(self, username: str, password: str, name: str, age: int | None, email: str) -> bool:
        connection = self._connect()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False

            cursor.execute(
                """
                INSERT INTO users (username, password, name, age, email)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, password, name, age, email),
            )
            connection.commit()
            return True
        finally:
            connection.close()

    def authenticate(self, username: str, password: str):
        connection = self._connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT username, password, name, age, email FROM users WHERE username = ? AND password = ?",
                (username, password),
            )
            return cursor.fetchone()
        finally:
            connection.close()
