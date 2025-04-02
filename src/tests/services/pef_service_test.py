import unittest
from unittest.mock import MagicMock, patch
from entities.pef import Pef
from entities.user import User
from services.pef_service import PefService, InvalidCredentialsError, UsernameExistsError, PasswordsDoNotMatch

class TestPefService(unittest.TestCase):
    
    def setUp(self):
        # Initialize a mock PefService
        self.pef_service = PefService()

        # Create mock repositories
        self.mock_pef_repository = MagicMock()
        self.mock_user_repository = MagicMock()

        # Set the PefService to use the mock repositories
        self.pef_service._pef_repository = self.mock_pef_repository
        self.pef_service._user_repository = self.mock_user_repository


    def test_login_invalid_credentials(self):

        username = "wrong_user"
        password = "wrong_password"
        self.mock_user_repository.find_by_username.return_value = None

        with self.assertRaises(InvalidCredentialsError):
            self.pef_service.login(username, password)

    @patch("services.pef_service.User")
    def test_create_user_success(self, MockUser):
        
        username = "new_user"
        password = "password123"
        password2 = "password123"
        user_mock = MagicMock(id=1, username=username, password=password)
        self.mock_user_repository.find_by_username.return_value = None
        self.mock_user_repository.create.return_value = user_mock

        new_user = self.pef_service.create_user(username, password, password2)

        self.assertEqual(new_user.username, username)
        self.assertEqual(new_user.password, password)
        self.mock_user_repository.create.assert_called_once_with(MockUser(username, password))

    def test_create_user_username_exists(self):
        
        username = "existing_user"
        password = "password123"
        password2 = "password123"
        existing_user_mock = MagicMock(id=1, username=username)
        self.mock_user_repository.find_by_username.return_value = existing_user_mock

        with self.assertRaises(UsernameExistsError):
            self.pef_service.create_user(username, password, password2)

    def test_create_user_passwords_do_not_match(self):
    
        username = "new_user"
        password = "password123"
        password2 = "password124"  # Different password for mismatch

        self.mock_user_repository.find_by_username.return_value = None

        with self.assertRaises(PasswordsDoNotMatch):
            self.pef_service.create_user(username, password, password2)

    def test_logout(self):
        
        self.pef_service._user = MagicMock(id=1, username='test_user')

        self.pef_service.logout()

        self.assertIsNone(self.pef_service.get_current_user())

