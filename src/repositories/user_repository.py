from src.entities.user import User
from src.database_connection import get_database_connection


def get_user_by_row(row):
    return User(row["username"], row["password"]) if row else None

class UserRepository:

    def __init__(self, connection):
        self._connection = connection

    def find_all(self):
        # Fetches all users as a list
        cursor = self._connection.cursor()
        cursor.execute("select * from users")
        rows = cursor.fetchall()

        return list(map(get_user_by_row, rows))

    def find_by_username(self, username):
        # Returns the user with the specified username
        cursor = self._connection.cursor()
        cursor.execute(
            "select * from users where username = ?",
            (username,)
        )
        row = cursor.fetchone()

        return get_user_by_row(row)

    def find_by_id(self, user_id):
        # Returns the user with the specified id
        cursor = self._connection.cursor()
        cursor.execute(
            "select * from users where id = ?",
            (user_id,)
        )
        row = cursor.fetchone()

        return get_user_by_row(row)

    def create(self, user):
        # Creates a new user and associates a password with it
        cursor = self._connection.cursor()
        cursor.execute(
            "insert into users (username, password) values (?, ?)",
            (user.username, user.password)
        )
        self._connection.commit()

        return user

    def delete_all(self):
        # Deletes all users from the database
        cursor = self._connection.cursor()
        cursor.execute("delete from users")
        self._connection.commit()


user_repository = UserRepository(get_database_connection())
