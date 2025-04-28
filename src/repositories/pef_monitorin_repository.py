from entities.pef_monitoring import PefMonitoring
from database_connection import get_database_connection


class PefMonitoringRepository:
    """Repository class for managing PEF monitoring data in the database."""

    def __init__(self, connection):
        """Initializes the repository with a database connection.

        Args:
            connection: The database connection object.
        """
        self._connection = connection

    def find_monitoring_by_username(self, username):
        """Retrieves all monitoring records for a specific username.

        Args:
            username: The username to filter records.

        Returns:
            List of rows matching the username.
        """
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT * FROM Pef_monitoring
            WHERE username = ?""",
                       (username,))
        rows = cursor.fetchall()
        return rows

    def order_by_date(self, rows):
        """Sorts monitoring records by date in ascending order.

        Args:
            rows: List of monitoring records.

        Returns:
            Sorted list of records by date.
        """
        return sorted(rows, key=lambda x: x[2])  # assuming date is at index 2

    def add_value(self, pef_monitoring: PefMonitoring):
        """Inserts a new monitoring record into the database.

        Args:
            pef_monitoring: The PefMonitoring object to add.
        """
        cursor = self._connection.cursor()
        cursor.execute("""
            INSERT INTO Pef_monitoring
            (username, date, value1, value2, value3, state, time)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                       (pef_monitoring.username, pef_monitoring.date,
                        pef_monitoring.value1, pef_monitoring.value2,
                        pef_monitoring.value3, pef_monitoring.state,
                        pef_monitoring.time))
        self._connection.commit()

    def delete_all_monitoring(self):
        """Deletes all monitoring data from the database."""
        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM Pef_monitoring")
        self._connection.commit()

    def create_monitoring_session(self, username, start_date, end_date):
        """Creates a new monitoring session for a user.

        Args:
            username: The username for the session.
            start_date: The start date of the session.
            end_date: The end date of the session.
        """
        cursor = self._connection.cursor()
        cursor.execute("""
            INSERT INTO MonitoringSession (username, start_date, end_date)
            VALUES (?, ?, ?)""",
                       (username, start_date, end_date))
        self._connection.commit()

    def get_sessions_by_username(self, username):
        """Retrieves all monitoring sessions for a username.

        Args:
            username: The username to filter sessions.

        Returns:
            List of session records.
        """
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT * FROM MonitoringSession
            WHERE username = ?
            ORDER BY start_date DESC""",
                       (username,))
        return cursor.fetchall()

    def get_pef_entries_for_session(self, username, start_date, end_date):
        """Retrieves PEF entries within a date range for a user.

        Args:
            username: The username associated with entries.
            start_date: The start date for filtering.
            end_date: The end date for filtering.

        Returns:
            List of matching PEF records.
        """
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT * FROM Pef_monitoring
            WHERE username = ? AND date BETWEEN ? AND ?""",
                       (username, start_date, end_date))
        return cursor.fetchall()


pef_monitoring_repository = PefMonitoringRepository(get_database_connection())
