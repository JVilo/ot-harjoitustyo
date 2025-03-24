import sqlite3
from config import DATABASE_FILE_PATH, DATABASE_FILENAME

print(DATABASE_FILE_PATH, "in connection.py")
#print(sqlite3.connect(DATABASE_FILENAME))
connection = sqlite3.connect(DATABASE_FILENAME)
#print(connection)
connection.row_factory = sqlite3.Row


def get_database_connection():
    return connection