import unittest
from unittest.mock import patch, mock_open
from repositories.pef_repository import PefRepository
from entities.pef import Pef


class TestPefRepository(unittest.TestCase):
    def setUp(self):
        # Create a mock user directly for testing
        class MockUser:
            def __init__(self, username):
                self.username = username

        # Manually creating a mock user "Eva"
        self.user_eva = MockUser("Eva")

        # Create a Pef object for the test
        self.pef_eva = Pef(value=500, user=self.user_eva)

        # Initialize the repository with a mock file path
        self.pef_repository = PefRepository("mock_pef_file.txt")

    def test_create(self):
        # Test the create method to save a new PEF reference for a user
        new_pef = Pef(value=600, user=self.user_eva)

        # Mock the file read operation to simulate the file content
        with patch("builtins.open", new_callable=mock_open, read_data="1;500;Eva\n"):
            # Mock the _write method to prevent actual file writing
            with patch.object(self.pef_repository, "_write", return_value=None) as mock_write:
                saved_pefs = self.pef_repository.create(new_pef)

                # Assert that the new PEF is added to the list
                self.assertEqual(saved_pefs[-1].value, 600)
                self.assertEqual(saved_pefs[-1].user.username, "Eva")

                # Ensure that the _write method is called
                mock_write.assert_called_once()
