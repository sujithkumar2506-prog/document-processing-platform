import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "metadata.db"


def connection_helper():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    return connection, cursor