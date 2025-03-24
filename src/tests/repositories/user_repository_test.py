import unittest
from repositories.user_repository import user_repository
from entities.user import User

class TestUserRepository(unittest.TestCase):
    def setUp(self):
        user_repository.delete_all()
        self.user_eva = User('Eva', 'Eva321')
        self.user_eino = User('Eino', 'Eino456')

    def test_create(self):
        user_repository.create(self.user_eva)
        users = user_repository.find_all()

        self.assertEqual(len(users), 1)
        self.assertEqual(str(users[0]), str(self.user_eva))