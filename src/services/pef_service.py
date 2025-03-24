from entities.user import User

from repositories.user_repository import (
    user_repository as default_user_repository
)

class InvalidCredentialsError(Exception):
    pass


class UsernameExistsError(Exception):
    pass

class PasswordsDoNotMach(Exception):
    pass

class PefService:

    def __init__(
        self,
        user_repository=default_user_repository
    ):
        
        self._user = None
        self._user_repository = user_repository

    def login(self, username, password):

        user = self._user_repository.find_by_username(username)

        if not user or user.password != password:
            raise InvalidCredentialsError("Invalid username or password")

        self._user = user

        return user

    def get_current_user(self):

        return self._user

    def get_users(self):

        return self._user_repository.find_all()

    def logout(self):
        self._user = None

    def create_user(self, username, password, password2, login=True):

        existing_user = self._user_repository.find_by_username(username)

        if existing_user:
            raise UsernameExistsError(f"Username {username} already exists")
        
        elif password != password2:
            raise PasswordsDoNotMach(f'Passwords do not match')

        user = self._user_repository.create(User(username, password))

        if login:
            self._user = user

        return user


pef_service = PefService()