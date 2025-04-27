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

    def __init__(
        self,
        pef_repository=default_pef_repository,
        user_repository=default_user_repository,
        pef_monitoring_repository=default_pef_monitoring_repository,
    ):

        self._user = None
        self._pef_repository = pef_repository
        self._user_repository = user_repository
        self._pef_monitoring_repository = pef_monitoring_repository

    def get_reference_pef_for_user(self):
        if not self._user:
            return []

        ref = self._pef_repository.get_latest_for_user(self._user.username)

        return list(ref)

    def get_user_pef(self):
        if not self._user:
            return None
        return self._pef_repository.find_by_user(self._user)

    def count_reference_pef(self, height, age, gender, user=None):
        """Calculates the reference PEF based on height, age, and gender."""
        if user is None:
            user = self._user  # Fall back to the logged-in user if no user is passed

        if not user:
            raise ValueError(
                "No user provided and no logged-in user available.")

        if gender == "male" and age >= 16:
            height_in_m = height / 100
            reference_pef = (((height_in_m * 5.48) + 1.58) -
                             (age * 0.041)) * 60
            ref_pef = Pef(value=reference_pef, user=self._user)
            self._pef_repository.create(ref_pef)
            # print(f"Saving reference PEF: {reference_pef} for user: {user.username}")

        if gender == "female" and age >= 16:
            height_in_m = height / 100
            reference_pef = (((height_in_m * 3.72) + 2.24) - (age * 0.03)) * 60
            ref_pef = Pef(value=reference_pef, user=self._user)
            self._pef_repository.create(ref_pef)
            # print(f"Saving reference PEF: {reference_pef} for user: {user.username}")

        if age < 16:
            reference_pef = ((height - 100) * 5) + 100
            ref_pef = Pef(value=reference_pef, user=self._user)
            self._pef_repository.create(ref_pef)
            # print(f"Saving reference PEF: {reference_pef} for user: {user.username}")

        return reference_pef

    def login(self, username, password):
        # logs in the user if the username and password match
        # checks if the username exists and if the password matches the stored one
        user = self._user_repository.find_by_username(username)

        if not user or user.password != password:
            raise InvalidCredentialsError("Invalid username or password")

        self._user = user

        return user

    def calculate_percentage_difference(self, before_pef, after_pef):
        """Calculates the percentage difference between before and after PEF values."""
        if before_pef == 0:
            return 0  # Handle division by zero
        return abs(((after_pef - before_pef) /before_pef) * 100)

    def get_warning_message(
            self, morning_evening_diff, morning_before_after_diff, evening_before_after_diff
    ):
        """Returns a warning message 
        if any of the PEF differences exceed the threshold values."""

        # Check if the values are not None before comparing them
        if morning_evening_diff is not None and (
            morning_evening_diff > 20 or morning_evening_diff > 60
        ):
            return "PEF ero aamun ja illan välillä on yli 20% tai 60 L/min!"
        if morning_before_after_diff is not None and (
            morning_before_after_diff > 15 or morning_before_after_diff > 60
        ):
            return "PEF ero aamun ennen ja jälkeen lääkkeen on yli 15% tai 60 L/min!"
        if evening_before_after_diff is not None and (
            evening_before_after_diff > 15 or evening_before_after_diff > 60
        ):
            return "PEF ero illan ennen ja jälkeen lääkkeen on yli 15% tai 60 L/min!"

        return ""

    def calculate_pef_differences(
            self, morning_before, morning_after, evening_before, evening_after
    ):
        """Calculates the percentage differences
        for morning/evening and before/after PEF with formulas."""

        # Diurnal variation = difference between morning and evening (before meds), using average
        morning_evening_diff = None
        if morning_before is not None and evening_before is not None:
            avg = (morning_before + evening_before) / 2
            morning_evening_diff = abs((evening_before - morning_before) / avg * 100)

        # Bronchodilation responses
        before_after_diff_morning = None
        before_after_diff_evening = None

        if morning_before is not None and morning_after is not None:
            before_after_diff_morning = self.calculate_percentage_difference(
                morning_before, morning_after)

        if evening_before is not None and evening_after is not None:
            before_after_diff_evening = self.calculate_percentage_difference(
                evening_before, evening_after)

        # Warning message if needed
        warning_message = self.get_warning_message(
            morning_evening_diff, before_after_diff_morning, before_after_diff_evening
        )

        return {
            "morning_evening_diff": morning_evening_diff,
            "before_after_diff_morning": before_after_diff_morning,
            "before_after_diff_evening": before_after_diff_evening,
            "warning_message": warning_message
        }

    def create_monitoring_session(self, username, start_date, end_date):
        self._pef_monitoring_repository.create_monitoring_session(username, start_date, end_date)

    def get_sessions_by_username(self, username):
        return self._pef_monitoring_repository.get_sessions_by_username(username)

    def get_pef_entries_for_session(self, username, start_date, end_date):
        return self._pef_monitoring_repository.get_pef_entries_for_session(
            username, start_date, end_date
        )

    def add_value_to_monitoring(self, date, username,
                            value1, value2, value3, state, time):

        pef_m = self._pef_monitoring_repository.add_value(PefMonitoring(
            username, date, value1, value2, value3, state, time
        ))
        return pef_m

    def get_monitoring_by_username(self):
        if not self._user:
            return None
        res = self._pef_monitoring_repository.find_monitoring_by_username(
            self._user.username)
        return self._pef_monitoring_repository.order_by_date(res)

    def calculate_monitoring_difference_for_session(self, username, start_date, end_date):
        # Fetch the PEF entries for the session
        pefs = self.get_pef_entries_for_session(username, start_date, end_date)

        # Calculate the number of distinct days monitored
        unique_days = set(p["date"] for p in pefs)

        # Now call the method to calculate differences and pass number of days
        return self.calculate_monitoring_difference(pefs, len(unique_days))

    def calculate_monitoring_difference(self, pefs, monitored_days_count):
        """Calculate differences and thresholds based on PEF values"""
        thresholds = {"over_20": 0, "over_15": 0}
        daily_data = defaultdict(lambda: {
            "max_m": None, "max_m_p": None, "max_e": None, "max_e_p": None
        })

        all_pef_values = []

        # Populate daily data and collect all PEF values
        for values in pefs:
            date = values["date"]
            self._assign_max_value(values, daily_data[date])
            all_pef_values.append(self._get_max_value(values))

        # Process daily data to calculate variations and responses
        for date, vals in daily_data.items():
            self._process_day_thresholds(vals, thresholds)

        # Calculate highest, lowest, and average PEF values
        highest, lowest, average = self._calculate_pef_stats(all_pef_values)

        return self._build_monitoring_summary(
            thresholds["over_20"], thresholds["over_15"], monitored_days_count,
            highest, lowest, average
        )

    def _process_day_thresholds(self, vals, thresholds):
        """Process a single day's PEF data and update the thresholds"""
        m = vals["max_m"]
        e = vals["max_e"]

        # Calculate daily variation (morning vs evening)
        if m is not None and e is not None:
            variation = self._calculate_daily_variation(m, e)
            if variation >= 20 and abs(m - e) >= 60:
                thresholds["over_20"] += 1

        # Bronchodilation response morning
        if vals["max_m"] is not None and vals["max_m_p"] is not None:
            prosm = self._calculate_bronchodilation_response(vals["max_m"], vals["max_m_p"])
            if prosm >= 15:
                thresholds["over_15"] += 1

        # Bronchodilation response evening
        if vals["max_e"] is not None and vals["max_e_p"] is not None:
            prose = self._calculate_bronchodilation_response(vals["max_e"], vals["max_e_p"])
            if prose >= 15:
                thresholds["over_15"] += 1

    def _calculate_daily_variation(self, m, e):
        """Calculate the daily variation between morning and evening PEF values"""
        return abs(m - e) / max(m, e) * 100

    def _calculate_bronchodilation_response(self, initial, post):
        """Calculate the bronchodilation response percentage"""
        return ((post - initial) / initial) * 100

    def _calculate_pef_stats(self, all_pef_values):
        """Calculate highest, lowest, and average PEF values"""
        if all_pef_values:
            highest = max(all_pef_values)
            lowest = min(all_pef_values)
            average = sum(all_pef_values) / len(all_pef_values)
        else:
            highest = lowest = average = None
        return highest, lowest, average

    def _reset_daily_values(self):
        """Reset the daily values to default (None)"""
        return {
            "max_m": None,
            "max_m_p": None,
            "max_e": None,
            "max_e_p": None
        }

    def _assign_max_value(self, values, daily_values):
        """Assign the maximum value based on the state and time of the measurement"""
        max_val = self._get_max_value(values)
        if values["state"] == 'ENNEN LÄÄKETTÄ':
            if values["time"] == 'AAMU':
                daily_values["max_m"] = max_val
            elif values["time"] == 'ILTA':
                daily_values["max_e"] = max_val
        elif values["state"] == 'LÄÄKKEEN JÄLKEEN':
            if values["time"] == 'AAMU':
                daily_values["max_m_p"] = max_val
            elif values["time"] == 'ILTA':
                daily_values["max_e_p"] = max_val

    def _get_max_value(self, values):
        """Return the maximum value among the three possible PEF values"""
        return max(values["value1"], values["value2"], values["value3"])

    def _calculate_day_differences(self, max_m, max_m_p, max_e, max_e_p):
        """Calculate the percentage differences between the values"""
        prosm = ((max_m_p - max_m) / max_m) * 100
        prose = ((max_e_p - max_e) / max_e) * 100
        pros_d = ((max(max_m, max_e) - min(max_m, max_e)) / max(max_m, max_e)) * 100
        return prosm, prose, pros_d

    def _update_thresholds(self, prosm, prose, pros_d, thresholds):
        """Update thresholds for different conditions (e.g., over 15%, over 20%)"""
        if prosm >= 15 or prose >= 15:
            thresholds["over_15"] += 1
        if pros_d >= 20:
            thresholds["over_20"] += 1
        return thresholds

    def _build_monitoring_summary(self, over_20, over_15,
                                  monitored_days_count, highest, lowest, average
                                  ):
        """Builds a summary dictionary instead of a text block."""
        needed_times = max(1, monitored_days_count // 2)

        if over_20 >= needed_times and over_15 >= needed_times:
            warning_message = (
                f'Päivittäinen vaihtelu ylitti diagnostisen kynnyksen {over_20} kertaa!\n'
                f'Keuhkoputkia laajentava vaste ylitti diagnostisen kynnyksen {over_15} kertaa!'
            )
        elif over_20 >= needed_times:
            warning_message = (f'Päivittäinen vaihtelu ylitti diagnostisen kynnyksen'
                               f' {over_20} kertaa!')
        elif over_15 >= needed_times:
            warning_message = (f'Keuhkoputkia laajentava vaste ylitti diagnostisen kynnyksen'
                               f' {over_15} kertaa!')
        else:
            warning_message = "Ei merkittäviä muutoksia PEF-seurannassa."

        return {
            "over_20": over_20,
            "over_15": over_15,
            "highest": highest,
            "lowest": lowest,
            "average": average,
            "warning_message": warning_message
        }
    def get_current_user(self):
        # returns the current logged-in user, or None if not logged in
        return self._user

    def get_users(self):
        # returns all users
        return self._user_repository.find_all()

    def logout(self):
        # logs out the user
        # sets the current user to None, effectively logging them out
        self._user = None

    def create_user(self, username, password, password2, login=True):
        # creates a user if the username is not in use and the password confirmation matches
        existing_user = self._user_repository.find_by_username(username)

        if existing_user:
            raise UsernameExistsError(f"Username {username} already exists")

        if password != password2:
            raise PasswordsDoNotMatch('Passwords do not match')

        user = self._user_repository.create(User(username, password))

        if login:
            self._user = user

        return user


pef_service = PefService()
