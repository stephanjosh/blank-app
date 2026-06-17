import sqlite3
from pathlib import Path

from dbOperations import create_tables

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "morbidity.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def count_records():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM morbidity_records")
        return cursor.fetchone()[0]


def print_first_10_records():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT month, diagnosis, age_group, gender, count FROM morbidity_records LIMIT 10"
        )
        records = cursor.fetchall()
        for record in records:
            print(record)


def show_top_diagnoses():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT diagnosis, SUM(count) AS total_count
            FROM morbidity_records
            GROUP BY diagnosis
            ORDER BY total_count DESC
            LIMIT 10
            """
        )
        records = cursor.fetchall()
        print("Top 10 diagnoses by total count:")
        for diagnosis, total_count in records:
            print(f"{diagnosis}: {total_count}")


if __name__ == "__main__":
    create_tables()
    print(f"Total records: {count_records()}")
    print("\nFirst 10 records:")
    print_first_10_records()
    print()
    show_top_diagnoses()