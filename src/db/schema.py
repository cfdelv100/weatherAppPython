import sqlite3

from src.config import DATABASE_PATH


def initialize_database(database_path: str = DATABASE_PATH) -> None:
    connection = sqlite3.connect(database_path)
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                age INTEGER,
                email TEXT
            )
            """
        )
        connection.commit()
    finally:
        connection.close()
