"""
Базовые тесты для класса DataDriver.

Важно: подставьте правильный путь импорта под ваш проект.
Предполагается, что классы DataDriver, ReportData, Report, Robot, DTO
находятся в модуле data_driver.py (поменяйте на свой при необходимости).
"""

import os
import sqlite3
from datetime import datetime

import pytest

from data_driver import DataDriver, ReportData
from models import Robot, Report, DTO

# ---------------------------------------------------------------------------
# Фикстуры
# ---------------------------------------------------------------------------

@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_data.db")


@pytest.fixture
def driver(db_path):
    d = DataDriver(db_path=db_path)
    d.create_tables()
    return d


@pytest.fixture
def sample_report():
    return ReportData(
        name="RobotProjectA",
        total_bags=10,
        profile_loaded="profile_1",
        errors=["err1", "err2"],
        robot_type="picker",
        left_status="ok",
        right_status="ok",
    )


# ---------------------------------------------------------------------------
# create_tables
# ---------------------------------------------------------------------------

def test_create_tables_creates_robots_table(driver, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='Robots'"
    )
    row = cursor.fetchone()
    conn.close()
    assert row is not None


def test_create_tables_is_idempotent(driver):
    # Повторный вызов не должен падать (IF NOT EXISTS)
    driver.create_tables()
    driver.create_tables()


# ---------------------------------------------------------------------------
# write_report
# ---------------------------------------------------------------------------

def test_write_report_inserts_robot_row(driver, db_path, sample_report):
    driver.write_report("SN-001", sample_report)

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT robot_id, project_name, robot_type FROM Robots WHERE robot_id = ?",
        ("SN-001",),
    ).fetchone()
    conn.close()

    assert row == ("SN-001", sample_report.name, sample_report.robot_type)


def test_write_report_creates_data_table_and_row(driver, db_path, sample_report):
    driver.write_report("SN-001", sample_report)

    conn = sqlite3.connect(db_path)
    table_exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (sample_report.name,),
    ).fetchone()
    assert table_exists is not None

    row = conn.execute(f"SELECT * FROM {sample_report.name}").fetchone()
    conn.close()

    assert row is not None
    # id, time, bags, profile_loaded, errors, left_status, right_status
    assert row[2] == sample_report.total_bags
    assert row[3] == sample_report.profile_loaded
    assert row[4] == "err1 err2"  # errors склеиваются через пробел
    assert row[5] == sample_report.left_status
    assert row[6] == sample_report.right_status


def test_write_report_does_not_duplicate_robot_on_repeat(driver, db_path, sample_report):
    driver.write_report("SN-001", sample_report)
    driver.write_report("SN-001", sample_report)  # тот же robot_id ещё раз

    conn = sqlite3.connect(db_path)
    count = conn.execute(
        "SELECT COUNT(*) FROM Robots WHERE robot_id = ?", ("SN-001",)
    ).fetchone()[0]
    conn.close()

    assert count == 1  # INSERT OR IGNORE не создаёт дубликат


def test_write_report_appends_multiple_reports(driver, db_path, sample_report):
    driver.write_report("SN-001", sample_report)
    driver.write_report("SN-001", sample_report)

    conn = sqlite3.connect(db_path)
    count = conn.execute(f"SELECT COUNT(*) FROM {sample_report.name}").fetchone()[0]
    conn.close()

    assert count == 2  # записи в таблице отчётов накапливаются


# ---------------------------------------------------------------------------
# get_robot_by_serial_key
# ---------------------------------------------------------------------------

def test_get_robot_by_serial_key_found(driver, sample_report):
    driver.write_report("SN-001", sample_report)

    robot = driver.get_robot_by_serial_key("SN-001")

    assert robot is not None
    assert isinstance(robot, Robot)
    assert robot.name == sample_report.name
    assert robot.type == sample_report.robot_type


def test_get_robot_by_serial_key_not_found_returns_none(driver):
    robot = driver.get_robot_by_serial_key("UNKNOWN")
    assert robot is None


# ---------------------------------------------------------------------------
# get_last_data_by_serial_key
# ---------------------------------------------------------------------------

def test_get_last_data_by_serial_key_returns_latest_report(driver, sample_report):
    driver.write_report("SN-001", sample_report)

    second_report = sample_report.model_copy(update={"total_bags": 99})
    driver.write_report("SN-001", second_report)

    last = driver.get_last_data_by_serial_key("SN-001")

    assert isinstance(last, Report)
    assert last.bags == 99


# ---------------------------------------------------------------------------
# get_today_data_by_serial_key
# ---------------------------------------------------------------------------

def test_get_today_data_by_serial_key_returns_todays_reports(driver, sample_report):
    driver.write_report("SN-001", sample_report)
    driver.write_report("SN-001", sample_report)

    reports = driver.get_today_data_by_serial_key("SN-001")

    assert len(reports) == 2
    assert all(isinstance(r, Report) for r in reports)
    today = datetime.now().date()
    assert all(r.time.date() == today for r in reports)


# ---------------------------------------------------------------------------
# get_all_reports
# ---------------------------------------------------------------------------

def test_get_all_reports_returns_all_written_reports(driver, sample_report):
    driver.write_report("SN-001", sample_report)
    driver.write_report("SN-001", sample_report)
    driver.write_report("SN-001", sample_report)

    reports = driver.get_all_reports("SN-001")

    assert len(reports) == 3
    assert all(isinstance(r, Report) for r in reports)


def test_get_all_reports_empty_when_no_reports(driver, sample_report):
    # Робот ещё не писал отчёты -> у него нет таблицы -> ожидаем ошибку
    # либо пустой список, в зависимости от желаемого поведения.
    # Здесь фиксируем текущее (потенциально проблемное) поведение:
    with pytest.raises(AttributeError):
        # get_robot_by_serial_key("SN-404") вернёт None,
        # и обращение к robot.name упадёт с AttributeError
        driver.get_all_reports("SN-404")

