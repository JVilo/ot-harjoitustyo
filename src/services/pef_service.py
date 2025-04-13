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
            reference_pef = (((height_in_m * 5.48) + 1.58) - (age * 0.041)) * 60
            ref_pef = Pef(value=reference_pef, user=self._user)
            self._pef_repository.create(ref_pef)
            # print(f"Saving reference PEF: {reference_pef} for user: {user.username}")
            return reference_pef

        if gender == "female" and age >= 16:
            height_in_m = height / 100
            reference_pef = (((height_in_m * 3.72) + 2.24) - (age * 0.03)) * 60
            ref_pef = Pef(value=reference_pef, user=self._user)
            self._pef_repository.create(ref_pef)
            # print(f"Saving reference PEF: {reference_pef} for user: {user.username}")
            return reference_pef

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
        return ((after_pef - before_pef) / before_pef) * 100

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
        for morning/evening and before/after PEF with optional bronchodilation."""

        # Calculate morning/evening PEF difference (regardless of bronchodilation)
        morning_evening_diff = None
        if morning_before is not None and evening_before is not None:
            morning_evening_diff = self.calculate_percentage_difference(
                morning_before, evening_before)

        # Initialize the before/after differences
        before_after_diff_morning = None
        before_after_diff_evening = None

        # Only calculate the before/after differences if bronchodilation values are provided
        if morning_before is not None and morning_after is not None:
            before_after_diff_morning = self.calculate_percentage_difference(
                morning_before, morning_after)

        if evening_before is not None and evening_after is not None:
            before_after_diff_evening = self.calculate_percentage_difference(
                evening_before, evening_after)

        # Get the warning message based on the differences calculated
        warning_message = self.get_warning_message(
            morning_evening_diff, before_after_diff_morning or 0, before_after_diff_evening or 0
        )

        return {
            "morning_evening_diff": morning_evening_diff,
            "before_after_diff_morning": before_after_diff_morning,
            "before_after_diff_evening": before_after_diff_evening,
            "warning_message": warning_message
        }
# No Ui functionality yet ->
    def add_value_to_monitoring(self,username, date,
                                value1, value2, value3, state, time):

        pef_m = self._pef_monitoring_repository.add_value(PefMonitoring(
            date, username, value1, value2, value3, state, time))
        return pef_m

    def get_monitoring_by_username(self):
        if not self._user:
            return None
        all = self._pef_monitoring_repository.find_monitoring_by_username(self._user.username)
        ordered = self._pef_monitoring_repository.order_by_date(all)
        return ordered

    def calculate_monitoring_difference(self):
        over_20 = 0
        over_15 = 0
        pefs = self.get_monitoring_by_username()  # Get all monitoring data for the user
        current_day = None

        # Loop through all the rows for the user, sorted by date
        for values in pefs:
            if current_day != values.date:
                # We're on a new day, reset the daily values
                current_day = values.date
                max_m = max_m_p = max_e = max_e_p = None  # Reset max values for the day

            # Process values based on state and time
            if values.state == 'ENNNEN LÄÄKETÄ' and values.time == 'AAMU':
                max_m = max(values.value1, values.value2, values.value3)
            elif values.state == 'LÄÄKKEEN JÄLKEEN' and values.time == 'AAMU':
                max_m_p = max(values.value1, values.value2, values.value3)
            elif values.state == 'ENNNEN LÄÄKETÄ' and values.time == 'ILTA':
                max_e = max(values.value1, values.value2, values.value3)
            elif values.state == 'LÄÄKKEEN JÄLKEEN' and values.time == 'ILTA':
                max_e_p = max(values.value1, values.value2, values.value3)

                # Once we have all values for the day, calculate the differences
                if (max_m is not None and max_m_p is not None
                        and max_e is not None and max_e_p is not None):
                    prosm = ((max_m_p - max_m) / max_m) * 100
                    prose = ((max_e_p - max_e) / max_e) * 100
                    pros_d = ((max_m - max_e) / max_m) * 100

                    # Check if thresholds are exceeded
                    if prosm >= 15 or prose >= 15:
                        over_15 += 1
                    if pros_d >= 20:
                        over_20 += 1

        # Return results based on thresholds exceeded
        if over_20 >= 3:
            return f'Vuorokausi vaihtelu on ylittänyt diagnoosi rajan {over_20} kertaa!'
        if over_15 >= 3:
            return f'Bronkodilataatiovaste on ylittänyt diagnoosi rajan {over_15} kertaa!'
        if over_20 >= 3 and over_15 >= 3:
            return f'Vuorokausi vaihtelu on ylittänyt diagnoosi rajan {over_20} kertaa!' \
                   f'Bronkodilataatiovaste on ylittänyt diagnoosi rajan {over_15} kertaa!'

        return "Ei merkittäviä muutoksia pef-seurannassa"

# <-
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
