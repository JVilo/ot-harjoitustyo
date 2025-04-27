from database_connection import get_database_connection


def drop_tables(connection):

    cursor = connection.cursor()

    cursor.execute("""
        drop table if exists users;
    """)
    cursor.execute("""
        drop table if exists pef_monitoring;
    """)
    cursor.execute("""
        drop table if exists MonitoringSession
    """)
    connection.commit()


def create_tables(connection):

    cursor = connection.cursor()

    # Create users table
    cursor.execute("""
            create table users (
                username text primary key,
                password text
            );
        """)

    # Create Pef_monitoring table with corrected syntax
    cursor.execute("""
            create table Pef_monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username text,
                date date,
                value1 integer,
                value2 integer,
                value3 integer,
                state text,
                time text
            );
        """)
    cursor.execute("""
            create table MonitoringSession (
            id INTEGER PRIMARY KEY,
            username TEXT,
            start_date TEXT,
            end_date TEXT
        );
        """)
    connection.commit()


def initialize_database():

    connection = get_database_connection()

    drop_tables(connection)
    create_tables(connection)


if __name__ == "__main__":
    initialize_database()
