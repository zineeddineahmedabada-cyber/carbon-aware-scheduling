
import unittest

from src.emissions import calculate_emissions


class TestCalculateEmissions(unittest.TestCase):

    def test_known_example(self):
        result = calculate_emissions(4, 2, 200)
        self.assertEqual(result, 1600)

    def test_zero_duration(self):
        result = calculate_emissions(4, 0, 200)
        self.assertEqual(result, 0)

    def test_negative_power_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_emissions(-4, 2, 200)


if __name__ == "__main__":
    unittest.main()
