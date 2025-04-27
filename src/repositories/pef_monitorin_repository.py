from entities.pef_monitoring import PefMonitoring
from database_connection import get_database_connection


class PefMonitoringRepository:

    def __init__(self, connection):
        self._connection = connection

    def find_monitoring_by_username(self, username):
        cursor = self._connection.cursor()
        cursor.execute("""
            select * from Pef_monitoring
            where username = ? """,
                       (username,)
                       )
        rows = cursor.fetchall()
        return rows

    def order_by_date(self, rows):
        # Make sure the data is ordered by date (ascending)
        return sorted(rows, key=lambda x: x[2])

    def add_value(self, pef_monitoring: PefMonitoring):
        cursor = self._connection.cursor()
        cursor.execute("""
            insert into Pef_monitoring
            (username, date, value1, value2, value3, state, time)
            values (?,?,?,?,?,?,?) """,
                       (pef_monitoring.username, pef_monitoring.date, pef_monitoring.value1,
                        pef_monitoring.value2, pef_monitoring.value3,
                        pef_monitoring.state, pef_monitoring.time)
                       )
        self._connection.commit()

    def delete_all_monitoring(self):
        # Deletes all monitoring data from the database
        cursor = self._connection.cursor()
        cursor.execute("delete from Pef_monitoring")
        self._connection.commit()

    def create_monitoring_session(self, username, start_date, end_date):
        cursor = self._connection.cursor()
        cursor.execute("""
            INSERT INTO MonitoringSession (username, start_date, end_date)
            VALUES (?, ?, ?)
        """, (username, start_date, end_date))
        self._connection.commit()

    def get_sessions_by_username(self, username):
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT * FROM MonitoringSession
            WHERE username = ?
            ORDER BY start_date DESC
        """, (username,))
        return cursor.fetchall()

    def get_pef_entries_for_session(self, username, start_date, end_date):
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT * FROM Pef_monitoring
            WHERE username = ? AND date BETWEEN ? AND ?
        """, (username, start_date, end_date))
        return cursor.fetchall()


pef_monitoring_repository = PefMonitoringRepository(get_database_connection())
