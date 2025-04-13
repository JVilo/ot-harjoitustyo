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
        self.mock_user_repository.create.assert_called_once_with(
            MockUser(username, password))

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

    def test_count_reference_pef_adult_male(self):
        user = User('TestUser', 'pass')
        self.pef_service._user = user
        self.mock_pef_repository.create = MagicMock()

        ref_pef = self.pef_service.count_reference_pef(180, 30, 'male')

        expected = (((1.8 * 5.48) + 1.58) - (30 * 0.041)) * 60
        self.assertAlmostEqual(ref_pef, expected, places=2)

    def test_count_reference_pef_child(self):
        user = User('ChildUser', 'pass')
        self.pef_service._user = user
        self.mock_pef_repository.create = MagicMock()

        ref_pef = self.pef_service.count_reference_pef(140, 10, 'male')

        expected = ((140 - 100) * 5) + 100
        self.assertEqual(ref_pef, expected)

    def test_calculate_percentage_difference(self):
        before = 300
        after = 330
        result = self.pef_service.calculate_percentage_difference(
            before, after)

        self.assertEqual(result, 10.0)

    def test_get_reference_pef_for_user_with_user(self):
        self.pef_service._user = User("MockUser", "pass")
        self.mock_pef_repository.get_latest_for_user.return_value = [420]

        result = self.pef_service.get_reference_pef_for_user()
        self.assertEqual(result, [420])
        self.mock_pef_repository.get_latest_for_user.assert_called_once_with(
            "MockUser")

    def test_get_reference_pef_for_user_no_user(self):
        self.pef_service._user = None
        result = self.pef_service.get_reference_pef_for_user()
        self.assertEqual(result, [])

    def test_get_user_pef_with_user(self):
        user = User("MockUser", "pass")
        self.pef_service._user = user
        self.mock_pef_repository.find_by_user.return_value = ["pef1", "pef2"]

        result = self.pef_service.get_user_pef()
        self.assertEqual(result, ["pef1", "pef2"])
        self.mock_pef_repository.find_by_user.assert_called_once_with(user)

    def test_get_user_pef_no_user(self):
        self.pef_service._user = None
        result = self.pef_service.get_user_pef()
        self.assertIsNone(result)

    def test_get_warning_message_morning_evening(self):
        msg = self.pef_service.get_warning_message(25, 10, 5)
        self.assertIn("aamun ja illan välillä", msg)

    def test_get_warning_message_morning_before_after(self):
        msg = self.pef_service.get_warning_message(5, 18, 10)
        self.assertIn("aamun ennen ja jälkeen", msg)

    def test_get_warning_message_evening_before_after(self):
        msg = self.pef_service.get_warning_message(5, 10, 20)
        self.assertIn("illan ennen ja jälkeen", msg)

    def test_get_warning_message_no_warning(self):
        msg = self.pef_service.get_warning_message(5, 5, 5)
        self.assertEqual(msg, "")

    def test_calculate_pef_differences(self):
        # Sample input values
        morning_before = 300
        morning_after = 330  # 10% increase
        evening_before = 310
        evening_after = 350  # ~12.9% increase

        result = self.pef_service.calculate_pef_differences(
            morning_before, morning_after, evening_before, evening_after
        )

        # Expected differences
        expected_morning_evening = (
            (evening_before - morning_before) / morning_before) * 100
        expected_before_after_morning = (
            (morning_after - morning_before) / morning_before) * 100
        expected_before_after_evening = (
            (evening_after - evening_before) / evening_before) * 100

        self.assertAlmostEqual(
            result["morning_evening_diff"], expected_morning_evening, places=2)
        self.assertAlmostEqual(
            result["before_after_diff_morning"], expected_before_after_morning, places=2)
        self.assertAlmostEqual(
            result["before_after_diff_evening"], expected_before_after_evening, places=2)
        self.assertEqual(result["warning_message"], "")
