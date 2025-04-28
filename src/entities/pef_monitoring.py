class PefMonitoring:
    """Represents a PEF monitoring data record.

    Attributes:
        username: The username associated with the monitoring record.
        date: The date of the monitoring entry.
        value1: The first measurement value.
        value2: The second measurement value.
        value3: The third measurement value.
        state: The state or status of the monitoring.
        time: The time of the monitoring entry.
    """

    def __init__(self, username, date, value1, value2, value3, state, time):
        """Initializes a new PefMonitoring instance.

        Args:
            username: The username associated with the record.
            date: The date of the record.
            value1: The first measurement value.
            value2: The second measurement value.
            value3: The third measurement value.
            state: The current state or condition.
            time: The time of the entry.
        """
        self.username = username
        self.date = date
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3
        self.state = state
        self.time = time
