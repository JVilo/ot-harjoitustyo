from src.entities.user import User
from src.entities.pef import Pef

from src.repositories.pef_repository import (
    pef_repository as default_pef_repository
)
from src.repositories.user_repository import (
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
        pef = Pef(value=value, user=user)
        return self._pef_repository.create(pef)

    def get_user_pef(self):
        if not self._user:
            return None
        return self._pef_repository.find_by_user(self._user)

    def count_reference_pef(self, height, age, gender):

        return self._pef_repository.count_reference(height, age, gender)

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
