from collections import defaultdict
from entities.user import User
from entities.pef import Pef
from entities.pef_monitoring import PefMonitoring


from repositories.pef_repository import (
    pef_repository as default_pef_repository
)
from repositories.user_repository import (
    user_repository as default_user_repository
)
from repositories.pef_monitorin_repository import (
    pef_monitoring_repository as default_pef_monitoring_repository
)


class InvalidCredentialsError(Exception):
    pass


class UsernameExistsError(Exception):
    pass


class PasswordsDoNotMatch(Exception):
    pass


class PefService:
    """Service class providing functionalities related to PEF monitoring.

    Attributes:
        _user: The currently logged-in user.
        _pef_repository: Repository for PEF objects, managing database interactions.
        _user_repository: Repository for user management.
        _pef_monitoring_repository: Repository for monitoring event management.
    """

    def __init__(
        self,
        pef_repository=default_pef_repository,
        user_repository=default_user_repository,
        pef_monitoring_repository=default_pef_monitoring_repository,
    ):
        """Initializes a PefService instance."""
        self._user = None
        self._pef_repository = pef_repository
        self._user_repository = user_repository
        self._pef_monitoring_repository = pef_monitoring_repository

    def get_reference_pef_for_user(self):
        """Fetches the latest reference PEF for the logged-in user.

        Returns:
            List of Pef objects or an empty list if no user is logged in.
        """
        if not self._user:
            return []

        ref = self._pef_repository.get_latest_for_user(self._user.username)
        return list(ref)

    def get_user_pef(self):
        """Retrieves the PEF data for the logged-in user.

        Returns:
            Pef object or None if no user is logged in.
        """
        if not self._user:
            return None
        return self._pef_repository.find_by_user(self._user)

    def count_reference_pef(self, height, age, gender, user=None):
        """Calculates and stores a reference PEF based on user's height, age, and gender.

        Args:
            height: User's height in centimeters.
            age: User's age in years.
            gender: Gender ('male' or 'female').
            user: Optional, the user object. Defaults to the logged-in user.

        Returns:
            The reference Pef object.
        """
        if user is None:
            user = self._user

        if not user:
            raise ValueError("Käyttäjää ei ole.")

        height_in_m = height / 100

        if gender == "male" and age >= 16:
            reference_pef_value = (
                ((height_in_m * 5.48) + 1.58) - (age * 0.041)) * 60
        elif gender == "female" and age >= 16:
            reference_pef_value = (
                ((height_in_m * 3.72) + 2.24) - (age * 0.03)) * 60
        elif age < 16:
            reference_pef_value = ((height - 100) * 5) + 100
        else:
            raise ValueError("Täytä kaikki kentät ensin")

        ref_pef = Pef(value=reference_pef_value, user=user)
        self._pef_repository.create(ref_pef)
        return ref_pef

    def login(self, username, password):
        """Authenticates a user by username and password.

        Args:
            username: The user's username.
            password: The user's password.

        Raises:
            InvalidCredentialsError: If credentials are invalid.

        Returns:
            The user object if login is successful.
        """
        user = self._user_repository.find_by_username(username)
        if not user or user.password != password:
            raise InvalidCredentialsError(
                "Virheellinen käyttäjätunnus tai salasana.")
        self._user = user
        return user

    def calculate_percentage_difference(self, before_pef, after_pef):
        """Calculates the percentage change between two PEF values.

        Args:
            before_pef: Value before.
            after_pef: Value after.

        Returns:
            Percentage change.
        """
        if before_pef == 0:
            return 0
        return abs(((after_pef - before_pef) / before_pef) * 100)

    def get_warning_message(
        self, morning_evening_diff, morning_before_after_diff, evening_before_after_diff
    ):
        """Returns a warning message if PEF changes exceed thresholds.

        Args:
            morning_evening_diff: Change between morning and evening.
            morning_before_after_diff: Change before and after medication in the morning.
            evening_before_after_diff: Change before and after medication in the evening.

        Returns:
            Warning message or an empty string.
        """
        warnings = []

        if morning_evening_diff is not None and (
                morning_evening_diff > 20 or morning_evening_diff > 60
        ):
            warnings.append("Aamun ja illan välinen "
                            "PEF-erotus ylittää 20 % tai 60 L/min")

        if morning_before_after_diff is not None and (
                morning_before_after_diff > 15 or morning_before_after_diff > 60
        ):
            warnings.append(
                "Aamun ennen ja jälkeen lääkityksen välinen "
                "PEF-erotus ylittää 15 % tai 60 L/min!"
            )

        if evening_before_after_diff is not None and (
                evening_before_after_diff > 15 or evening_before_after_diff > 60
        ):
            warnings.append(
                "Illan ennen ja jälkeen lääkityksen välinen "
                "PEF-erotus ylittää 15 % tai 60 L/min!"
            )

        return "\n".join(warnings)

    def calculate_pef_differences(
        self, morning_before, morning_after, evening_before, evening_after
    ):
        """Calculates PEF percentage changes and warning messages.

        Args:
            morning_before: Morning PEF before medication.
            morning_after: Morning PEF after medication.
            evening_before: Evening PEF before medication.
            evening_after: Evening PEF after medication.

        Returns:
            Dictionary with change values and warning message.
        """
        # Diurnal variation
        morning_evening_diff = None
        if morning_before is not None and evening_before is not None:
            avg = (morning_before + evening_before) / 2
            morning_evening_diff = abs(
                (evening_before - morning_before) / avg * 100)

        # Bronchodilation
        before_after_diff_morning = None
        before_after_diff_evening = None
        if morning_before is not None and morning_after is not None:
            before_after_diff_morning = self.calculate_percentage_difference(
                morning_before, morning_after
            )
        if evening_before is not None and evening_after is not None:
            before_after_diff_evening = self.calculate_percentage_difference(
                evening_before, evening_after
            )

        warning_message = self.get_warning_message(
            morning_evening_diff,
            before_after_diff_morning,
            before_after_diff_evening,
        )

        return {
            "morning_evening_diff": morning_evening_diff,
            "before_after_diff_morning": before_after_diff_morning,
            "before_after_diff_evening": before_after_diff_evening,
            "warning_message": warning_message,
        }

    def create_monitoring_session(self, username, start_date, end_date):
        """Creates a new PEF monitoring session.

        Args:
            username: The user's username.
            start_date: Start date.
            end_date: End date.
        """
        self._pef_monitoring_repository.create_monitoring_session(
            username, start_date, end_date
        )

    def get_sessions_by_username(self, username):
        """Retrieves all monitoring sessions for a user.

        Args:
            username: The user's username.

        Returns:
            List of sessions.
        """
        return self._pef_monitoring_repository.get_sessions_by_username(username)

    def get_pef_entries_for_session(self, username, start_date, end_date):
        """Fetches PEF data for a specific session.

        Args:
            username: The user's username.
            start_date: Session start date.
            end_date: Session end date.

        Returns:
            List of PEF entries.
        """
        return self._pef_monitoring_repository.get_pef_entries_for_session(
            username, start_date, end_date
        )

    def add_value_to_monitoring(self, date, username, value1, value2, value3, state, time):
        """Adds a new PEF monitoring event.

        Args:
            date: Date.
            username: User's username.
            value1: First PEF value.
            value2: Second PEF value.
            value3: Third PEF value.
            state: State ('BEFORE MEDICATION' or 'AFTER MEDICATION').
            time: Time ('MORNING' or 'EVENING').

        Returns:
            The added PefMonitoring object.
        """
        pef_m = self._pef_monitoring_repository.add_value(PefMonitoring(
            username, date, value1, value2, value3, state, time
        ))
        return pef_m

    def get_monitoring_by_username(self):
        """Retrieves the logged-in user's monitoring and PEF data.

        Returns:
            List of ordered PefMonitoring objects or None if not logged in.
        """
        if not self._user:
            return None
        res = self._pef_monitoring_repository.find_monitoring_by_username(
            self._user.username
        )
        return self._pef_monitoring_repository.order_by_date(res)

    def calculate_monitoring_difference_for_session(self, username, start_date, end_date):
        """Calculates the change in PEF during a specific session.

        Args:
            username: The user's username.
            start_date: Start date.
            end_date: End date.

        Returns:
            Summary of change values.
        """
        pefs = self.get_pef_entries_for_session(username, start_date, end_date)
        unique_days = set(p["date"] for p in pefs)
        return self.calculate_monitoring_difference(pefs, len(unique_days))

    def calculate_monitoring_difference(self, pefs, monitored_days_count):
        """Calculates PEF value fluctuations and provides summaries.

        Args:
            pefs: List of PEF data.
            monitored_days_count: Number of recorded days.

        Returns:
            Summary data including change values and warnings.
        """
        thresholds = {"over_20": 0, "over_15": 0}
        daily_data = defaultdict(lambda: {
            "max_m": None, "max_m_p": None, "max_e": None, "max_e_p": None
        })

        all_pef_values = []

        # Populate daily maximum values and collect all PEF values
        for values in pefs:
            date = values["date"]
            self._assign_max_value(values, daily_data[date])
            all_pef_values.append(self._get_max_value(values))

        # Assess daily variations and responses
        for date, vals in daily_data.items():
            self._process_day_thresholds(vals, thresholds)

        # Calculate highest, lowest, and average PEF
        highest, lowest, average = self._calculate_pef_stats(all_pef_values)

        return self._build_monitoring_summary(
            thresholds["over_20"], thresholds["over_15"], monitored_days_count,
            highest, lowest, average
        )

    def _process_day_thresholds(self, vals, thresholds):
        """Processes PEF data for one day and updates thresholds."""
        m = vals["max_m"]
        e = vals["max_e"]

        # Daily change (morning vs evening)
        if m is not None and e is not None:
            variation = self._calculate_daily_variation(m, e)
            if variation >= 20 and abs(m - e) >= 60:
                thresholds["over_20"] += 1

        # Medication response in the morning
        if vals["max_m"] is not None and vals["max_m_p"] is not None:
            prosm = self._calculate_bronchodilation_response(
                vals["max_m"], vals["max_m_p"]
            )
            if prosm >= 15:
                thresholds["over_15"] += 1

        # Medication response in the evening
        if vals["max_e"] is not None and vals["max_e_p"] is not None:
            prose = self._calculate_bronchodilation_response(
                vals["max_e"], vals["max_e_p"]
            )
            if prose >= 15:
                thresholds["over_15"] += 1

    def _calculate_daily_variation(self, m, e):
        """Calculates daily variation percentage."""
        return abs(m - e) / max(m, e) * 100

    def _calculate_bronchodilation_response(self, initial, post):
        """Calculates the percentage change due to bronchodilation."""
        return ((post - initial) / initial) * 100

    def _calculate_pef_stats(self, all_pef_values):
        """Calculates maximum, minimum, and average PEF values."""
        if all_pef_values:
            highest = max(all_pef_values)
            lowest = min(all_pef_values)
            average = sum(all_pef_values) / len(all_pef_values)
        else:
            highest = lowest = average = None
        return highest, lowest, average

    def _assign_max_value(self, values, daily_values):
        """Assigns and stores the maximum value for the day and its timing."""
        max_val = self._get_max_value(values)
        if values["state"] == 'BEFORE MEDICATION':
            if values["time"] == 'MORNING':
                daily_values["max_m"] = max_val
            elif values["time"] == 'EVENING':
                daily_values["max_e"] = max_val
        elif values["state"] == 'AFTER MEDICATION':
            if values["time"] == 'MORNING':
                daily_values["max_m_p"] = max_val
            elif values["time"] == 'EVENING':
                daily_values["max_e_p"] = max_val

    def _get_max_value(self, values):
        """Returns the maximum of the three PEF values."""
        return max(values["value1"], values["value2"], values["value3"])

    def _build_monitoring_summary(
        self, over_20, over_15, monitored_days_count, highest, lowest, average
    ):
        """Builds a summary message and status report."""
        needed_times = max(1, monitored_days_count // 2)

        if over_20 >= needed_times and over_15 >= needed_times:
            warning_message = (
                f'PEF-vaihtelu ylitti diagnosointirajan'
                f' {over_20} kertaa!'
                f'Keuhkoputkia laajentava vaste ylitti diagnosointirajan'
                f' {over_15} kertaa!'
            )
        elif over_20 >= needed_times:
            warning_message = (f'PEF-vaihtelu ylitti'
                               f' diagnosointirajan {over_20} kertaa!')
        elif over_15 >= needed_times:
            warning_message = (f'Keuhkoputkia laajentava vaste'
                               f' ylitti diagnosointirajan {over_15} kertaa!')
        else:
            warning_message = "PEF-seurannassa ei havaittu merkittäviä muutoksia."

        return {
            "over_20": over_20,
            "over_15": over_15,
            "highest": highest,
            "lowest": lowest,
            "average": average,
            "warning_message": warning_message,
        }

    def get_current_user(self):
        """Returns the currently logged-in user or None."""
        return self._user

    def get_users(self):
        """Returns all users."""
        return self._user_repository.find_all()

    def logout(self):
        """Logs out the current user."""
        self._user = None

    def create_user(self, username, password, password2, login=True):
        """Creates a new user if the username is available and passwords match.

        Args:
            username: Username.
            password: Password.
            password2: Password confirmation.
            login: If True, logs in the user after creation.

        Raises:
            UsernameExistsError: If the username is already taken.
            PasswordsDoNotMatch: If the passwords do not match.

        Returns:
            The created User object.
        """
        existing_user = self._user_repository.find_by_username(username)
        if existing_user:
            raise UsernameExistsError(
                f"Käyttäjätunnus {username} on jo käytössä.")

        if password != password2:
            raise PasswordsDoNotMatch('Salasanat eivät täsmää.')

        if len(username) < 3:
            raise ValueError(
                "Käyttäjätunnuksen tulee olla vähintään 3 merkkiä pitkä.")

        if len(password) < 6:
            raise ValueError("Salasanan tulee olla vähintään 6 merkkiä pitkä.")

        user = self._user_repository.create(User(username, password))

        if login:
            self._user = user

        return user


pef_service = PefService()
