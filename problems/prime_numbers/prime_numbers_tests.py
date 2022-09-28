import unittest

from prime_numbers import prime_list

"""This is the test file for the prime number optimisation exercise. 
The original implemented function is the most naive functional approach we found. 
Different caching and mathematics solutions can improve the perofrmances"""

class TestPrimeNumbersMethod(unittest.TestCase):

    def test_negatives(self):
        self.assertEqual(prime_list(-2), [])

    def test_none(self):
        self.assertEqual(prime_list(1), [])

    def test_multiple(self):
        self.assertEqual(prime_list(15), [2, 3, 5, 7, 11, 13])

    def test_one(self):
        self.assertEqual(prime_list(2), [2])

if __name__ == '__main__':
    unittest.main()