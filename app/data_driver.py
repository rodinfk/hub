import sqlite3
import os

from models import ReportData
from models import DTO


class DataDriver:
    def __init__(self, db_path="DATA.db"):
        self.db_path = db_path

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA busy_timeout=5000")
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def create_tables(self):
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Robots (
                    id INTEGER PRIMARY KEY,
                    robot_id VARCHAR(20) UNIQUE NOT NULL,
                    project_name VARCHAR(20) NOT NULL,
                    robot_type VARCHAR(20) NOT NULL
                )
            ''')

    def drop_db(self):
        os.remove(self.db_path)

    def write_report(self, robot_id, data: ReportData):
        with self._connect() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                INSERT OR IGNORE INTO Robots (robot_id, project_name, robot_type)
                VALUES (?, ?, ?)
            ''', (robot_id, data.name, data.robot_type))

            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {data.name} (
                    id INTEGER PRIMARY KEY,
                    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    bags INTEGER NOT NULL,
                    profile_loaded VARCHAR(35),
                    errors TEXT,
                    left_status VARCHAR(20),
                    right_status VARCHAR(20)
                )
            ''')

            cursor.execute(f'''
                INSERT INTO {data.name} 
                (bags, profile_loaded, errors, left_status, right_status)
                VALUES (?, ?, ?, ?, ?)
            ''', 
            (data.total_bags, data.profile_loaded, " ".join(data.errors), data.left_status, data.right_status)
            )

    def get_last_data_by_serial_key(self, key):
        robot = self.get_robot_by_serial_key(key)
        with self._connect() as connection:
            cursor = connection.cursor()
            
            cursor.execute(f'''SELECT * FROM {robot.name} ORDER BY id DESC LIMIT 1''')

            row = cursor.fetchone()
            return DTO.sql_to_Report(row)

    def get_today_data_by_serial_key(self, key):
        robot = self.get_robot_by_serial_key(key)
        with self._connect() as connection:
            cursor = connection.cursor()
            
            cursor.execute(f'SELECT * FROM {robot.name} WHERE time >= date("now") AND time < date("now", "+1 day");')

            rows = cursor.fetchall()
            return [DTO.sql_to_Report(r) for r in rows]

    def get_robot_by_serial_key(self, key):
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM Robots WHERE robot_id = ?', [key])
        
            row = cursor.fetchone()

            if row is None:
                return

            return DTO.sql_to_Robot(row)

    def get_all_reports(self, key):
        robot = self.get_robot_by_serial_key(key)
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM {robot.name}')

            rows = cursor.fetchall()
            return [DTO.sql_to_Report(r) for r in rows]


sql = DataDriver()
#sql.create_tables()


