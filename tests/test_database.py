import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "velops_star.db"


def test_database_exists():
    assert DB_PATH.exists()


def test_foreign_keys_integrity():
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

    assert result == []


def test_fact_table_not_empty():
    with sqlite3.connect(DB_PATH) as conn:
        count = conn.execute(
            """
            SELECT COUNT(*)
            FROM fait_disponibilite
            """
        ).fetchone()[0]

    assert count > 0


def test_dimensions_not_empty():
    with sqlite3.connect(DB_PATH) as conn:
        station_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM dim_station
            """
        ).fetchone()[0]

        time_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM dim_temps
            """
        ).fetchone()[0]

    assert station_count > 0
    assert time_count > 0