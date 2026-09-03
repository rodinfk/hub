import sqlite3
import os

from dotenv import dotenv_values


def config():
    return dotenv_values(".env")


class DataDriver:
    def __init__(self, db_path="Bot.db"):
        self.db_path = db_path

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def create_tables(self):
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    robot_id VARCHAR(20) NOT NULL
                )
            ''')

    def drop_db(self):
        os.remove(self.db_path)

    def write_user(self, user_id: int, robot_id: str):
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                INSERT OR IGNORE INTO Users (user_id, robot_id)
                VALUES (?, ?)
            ''', (user_id, robot_id))

    def get_robot_by_user_id(self, user_id):
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(f'''
                SELECT robot_id
                FROM Users
                WHERE user_id = {user_id}'''
                )
        
            row = cursor.fetchone()

            if row is None:
                return

            return row[0]

    def delete_user(self, user_id):
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute(f'''
                DELETE FROM Users
                WHERE user_id = {user_id}'''
            )
                


sql = DataDriver()