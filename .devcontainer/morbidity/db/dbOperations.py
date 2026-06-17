from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[1] # it guarantees that SQLite always creates or opens a single-database file in the exact same location, regardless of where or how I run my Python script.
DB_PATH = BASE_DIR / "morbidity.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


def create_tables():
    """Create the normalized morbidity records table."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS morbidity_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            age_group TEXT NOT NULL,
            gender TEXT NOT NULL,
            count INTEGER NOT NULL,
            UNIQUE(month, diagnosis, age_group, gender)
        )
        """
    )
    conn.commit()


def insert_records(records):
    """Insert many records into the database.

    Each record should look like:
    (month, diagnosis, age_group, gender, count)
    """
    if not records:
        return 0

    cursor.executemany(
        """
        INSERT OR REPLACE INTO morbidity_records
        (month, diagnosis, age_group, gender, count)
        VALUES (?, ?, ?, ?, ?)
        """,
        records,
    )
    conn.commit()
    return len(records)


def get_morbidity_data():
    cursor.execute("SELECT * FROM morbidity_records")
    return cursor.fetchall()


def close_db():
    conn.close()
