from entities.user import User
from database_connection import get_database_connection


def get_user_by_row(row):
    """Creates a User object from a database row.

    Args:
        row: A dictionary representing a database row.

    Returns:
        A User object or None if row is None.
    """
    return User(row["username"], row["password"]) if row else None


class UserRepository:
    """Repository for managing user data in the database."""

    def __init__(self, connection):
        """Initializes with a database connection.

        Args:
            connection: The database connection object.
        """
        self._connection = connection

    def find_all(self):
        """Retrieves all users from the database.

        Returns:
            List of User objects.
        """
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return list(map(get_user_by_row, rows))

    def find_by_username(self, username):
        """Finds a user by username.

        Args:
            username: The username to search for.

        Returns:
            User object if found, else None.
        """
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return get_user_by_row(row)

    def find_by_id(self, user_id):
        """Finds a user by user ID.

        Args:
            user_id: The ID of the user.

        Returns:
            User object if found, else None.
        """
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return get_user_by_row(row)

    def create(self, user):
        """Creates a new user in the database.

        Args:
            user: The User object to create.

        Returns:
            The created User object.
        """
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (user.username, user.password)
        )
        self._connection.commit()
        return user

    def delete_all(self):
        """Deletes all users from the database."""
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM users")
        self._connection.commit()


user_repository = UserRepository(get_database_connection())
