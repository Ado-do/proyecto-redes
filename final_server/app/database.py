import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "sensor_data.db")


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-style access
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER,
            timestamp DATETIME,
            temperature REAL,
            pressure REAL,
            humidity REAL,
            PRIMARY KEY (id, timestamp)
        )""")
        conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON readings(timestamp)
        """)


def insert_reading(data: dict):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO readings 
            (id, timestamp, temperature, pressure, humidity) 
            VALUES (?, ?, ?, ?, ?)""",
            (
                data["id"],
                data["timestamp"],
                data["temperature"],
                data["pressure"],
                data["humidity"],
            ),
        )
        conn.commit()
