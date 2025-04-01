import unittest
from repositories.pef_repository import pef_repository
from entities.pef import Pef

class TestPefRepository(unittest.TestCase):
    def setUp(self):
        self.pef_eva = Pef(500,'Eva')
    
    def test_count_reference_man(self):
        # Test for male PEF calculation
        height = 180  # cm
        age = 30
        gender = "male"
        
        expected_pef = (((height / 100 * 5.48) + 1.58) - (age * 0.041)) * 60
        reference_pef = pef_repository.count_reference(height, age, gender)
        
        self.assertAlmostEqual(reference_pef, expected_pef, delta=1)

    def test_count_reference_woman(self):
        # Test for female PEF calculation
        height = 165  # cm
        age = 30
        gender = "female"
        
        expected_pef = (((height / 100 * 3.72) + 2.24) - (age * 0.03)) * 60
        reference_pef = pef_repository.count_reference(height, age, gender)
        
        self.assertAlmostEqual(reference_pef, expected_pef, delta=1)

    def test_count_reference_child(self):
        # Test for child PEF calculation
        height = 120  # cm
        age = 10
        gender = "other"  # Using "other" for child
        
        expected_pef = ((height - 100) * 5) + 100
        reference_pef = pef_repository.count_reference(height, age, gender)
        
        self.assertEqual(reference_pef, expected_pef)
