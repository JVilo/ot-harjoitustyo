import unittest
from unittest.mock import MagicMock, patch
from entities.pef import Pef
from entities.user import User
from entities.pef_monitoring import PefMonitoring
from services.pef_service import PefService, InvalidCredentialsError, UsernameExistsError, PasswordsDoNotMatch


class TestPefService(unittest.TestCase):

    def setUp(self):
        # Initialize a mock PefService
        self.pef_service = PefService()

        # Create mock repositories
        self.mock_pef_repository = MagicMock()
        self.mock_user_repository = MagicMock()
        self.mock_pef_monitoring_repository = MagicMock()

        # Set the PefService to use the mock repositories
        self.pef_service._pef_repository = self.mock_pef_repository
        self.pef_service._user_repository = self.mock_user_repository
        self.pef_service._pef_monitoring_repository = self.mock_pef_monitoring_repository

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

        ref_pef = self.pef_service.count_reference_pef(180, 30, 'male').value

        expected = (((1.8 * 5.48) + 1.58) - (30 * 0.041)) * 60
        self.assertAlmostEqual(ref_pef, expected, places=2)

    def test_count_reference_pef_child(self):
        user = User('ChildUser', 'pass')
        self.pef_service._user = user
        self.mock_pef_repository.create = MagicMock()

        ref_pef = self.pef_service.count_reference_pef(140, 10, 'male').value

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
        self.assertIn("Aamun ja illan välinen PEF-erotus ylittää 20 % tai 60 L/min", msg)

    def test_get_warning_message_morning_before_after(self):
        msg = self.pef_service.get_warning_message(5, 18, 10)
        self.assertIn("Aamun ennen ja jälkeen lääkityksen välinen PEF-erotus ylittää 15 % tai 60 L/min!", msg)

    def test_get_warning_message_evening_before_after(self):
        msg = self.pef_service.get_warning_message(5, 10, 20)
        self.assertIn("Illan ennen ja jälkeen lääkityksen välinen PEF-erotus ylittää 15 % tai 60 L/min!", msg)

    def test_get_warning_message_no_warning(self):
        msg = self.pef_service.get_warning_message(5, 5, 5)
        self.assertEqual(msg, "")

    def test_calculate_pef_differences(self):
        # Sample input values
        morning_before = 300
        morning_after = 330  # 10% increase
        evening_before = 310
        evening_after = 350  # ~12.9% increase

        # Call the method to calculate differences
        result = self.pef_service.calculate_pef_differences(
            morning_before, morning_after, evening_before, evening_after
        )

        # Expected values based on the same logic in the service
        expected_morning_evening = abs(
            (evening_before - morning_before) / ((morning_before + evening_before) / 2) * 100)
        expected_before_after_morning = self.pef_service.calculate_percentage_difference(
            morning_before, morning_after)
        expected_before_after_evening = self.pef_service.calculate_percentage_difference(
            evening_before, evening_after)

        # Assert the differences with an acceptable tolerance for floating-point errors
        self.assertAlmostEqual(
            result["morning_evening_diff"], expected_morning_evening, places=3)
        self.assertAlmostEqual(
            result["before_after_diff_morning"], expected_before_after_morning, places=3)
        self.assertAlmostEqual(
            result["before_after_diff_evening"], expected_before_after_evening, places=3)

        # Assert the warning message (based on the logic from the service)
        self.assertEqual(result["warning_message"], "")

    def test_calculate_monitoring_difference(self):
        # Sample input data for a monitoring session
        pefs = [
            {"date": "2025-04-01", "value1": 300, "value2": 310, "value3": 305, "state": "ENNEN LÄÄKETTÄ",
             "time": "AAMU"},
            {"date": "2025-04-01", "value1": 295, "value2": 315, "value3": 300, "state": "ENNEN LÄÄKETTÄ",
             "time": "ILTA"},
            {"date": "2025-04-02", "value1": 305, "value2": 310, "value3": 300, "state": "LÄÄKKEEN JÄLKEEN",
             "time": "AAMU"},
            {"date": "2025-04-02", "value1": 310, "value2": 325, "value3": 315, "state": "LÄÄKKEEN JÄLKEEN",
             "time": "ILTA"}
        ]

        # Mock the PefMonitoring repository's `get_pef_entries_for_session` method to return our sample data
        self.mock_pef_monitoring_repository.get_pef_entries_for_session.return_value = pefs

        # Call the method to calculate the differences
        result = self.pef_service.calculate_monitoring_difference_for_session(
            "MockUser", "2025-04-01", "2025-04-02")

        # Validate that the returned result contains the correct summary data
        self.assertIn("over_20", result)
        self.assertIn("over_15", result)
        self.assertIn("highest", result)
        self.assertIn("lowest", result)
        self.assertIn("average", result)
        self.assertIn("warning_message", result)

    def test_get_warning_message_with_invalid_thresholds(self):
        # Test for values exceeding the thresholds
        msg = self.pef_service.get_warning_message(25, 16, 5)
        # Threshold exceeded for morning-evening
        self.assertIn(
            "Aamun ja illan välinen PEF-erotus ylittää 20 % tai 60 L/min\nAamun ennen ja jälkeen lääkityksen välinen PEF-erotus ylittää 15 % tai 60 L/min!",
            msg
        )

        msg = self.pef_service.get_warning_message(5, 18, 5)
        # Threshold exceeded for morning-before-after
        self.assertIn("Aamun ennen ja jälkeen lääkityksen välinen PEF-erotus ylittää 15 % tai 60 L/min!", msg)

        msg = self.pef_service.get_warning_message(5, 5, 20)
        # Threshold exceeded for evening-before-after
        self.assertIn("Illan ennen ja jälkeen lääkityksen välinen PEF-erotus ylittää 15 % tai 60 L/min!", msg)

        msg = self.pef_service.get_warning_message(5, 5, 5)
        self.assertEqual(msg, "")  # No warning if no thresholds are exceeded

    def test_add_value_to_monitoring(self):
        # Sample data for monitoring entry
        date = "2025-04-01"
        username = "test_user"
        value1 = 300
        value2 = 310
        value3 = 305
        state = "ENNEN LÄÄKETTÄ"
        time = "AAMU"

        # Mock the repository call to verify the add_value method is called
        self.mock_pef_monitoring_repository.add_value.return_value = PefMonitoring(
            username, date, value1, value2, value3, state, time
        )

        # Add the value
        self.pef_service.add_value_to_monitoring(
            date, username, value1, value2, value3, state, time)

        # Get the actual call arguments passed to add_value
        args = self.mock_pef_monitoring_repository.add_value.call_args[0][0]

        # Verify the values are correctly passed to add_value (compare attributes)
        self.assertEqual(args.username, username)
        self.assertEqual(args.date, date)
        self.assertEqual(args.value1, value1)
        self.assertEqual(args.value2, value2)
        self.assertEqual(args.value3, value3)
        self.assertEqual(args.state, state)
        self.assertEqual(args.time, time)
