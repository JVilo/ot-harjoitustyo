from entities.user import User
from entities.pef import Pef

from repositories.pef_repository import (
    pef_repository as default_pef_repository
)
from repositories.user_repository import (
    user_repository as default_user_repository
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
        user_repository=default_user_repository
    ):

        self._user = None
        self._pef_repository = pef_repository
        self._user_repository = user_repository

    def create_pef(self, value, user=None):
        """Creates a new PEF reference and associates it with a user."""
        if user is None:
            user = self._user  # Fall back to the logged-in user if no user is passed
        
        if not user:
            raise ValueError("No user provided and no logged-in user available.")
        
        pef = Pef(value=value, user=user)
        return self._pef_repository.create(pef)

    def get_reference_pef_for_user(self):
        if not self._user:
            return []

        """Fetches the stored reference PEF value for the given user."""
        ref= self._pef_repository.get_latest_for_user(self._user.username)
        #print(f"Fetched reference PEF for {self._user.username}: {ref}")
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
            raise ValueError("No user provided and no logged-in user available.")
        
        if gender == "male" and age > 16:
            height_in_m = height / 100
            reference_pef = (((height_in_m * 5.48) + 1.58) - (age * 0.041)) * 60
        elif gender == "female" and age > 16:
            height_in_m = height / 100
            reference_pef = (((height_in_m * 3.72) + 2.24) - (age * 0.03)) * 60
        else:
            reference_pef = ((height - 100) * 5) + 100

        ref_pef = Pef(value=reference_pef, user=self._user)
        self._pef_repository.create(ref_pef)
        #print(f"Saving reference PEF: {reference_pef} for user: {user.username}")
        return reference_pef

    def login(self, username, password):
        # logs in the user if the username and password match
        # checks if the username exists and if the password matches the stored one
        user = self._user_repository.find_by_username(username)

        if not user or user.password != password:
            raise InvalidCredentialsError("Invalid username or password")

        self._user = user

        return user

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
