import os, sys

sys.path.append(
    os.path.dirname(os.path.abspath(os.path.join(__file__, os.path.pardir))))

import unittest
import common.utils as utils

class UtilsTest(unittest.TestCase):
    def test_byte_to_binary_string(self):
        self.assertEqual(utils.byte_to_binary_string(0b10101010), "10101010")
        self.assertEqual(utils.byte_to_binary_string(0), "00000000")
        self.assertEqual(utils.byte_to_binary_string(0xff), "11111111")

    def test_get_mask(self):
        self.assertEqual(utils._get_mask(0,5), 0b00111111)
        self.assertEqual(utils._get_mask(2,3), 0b00001100)
        self.assertEqual(utils._get_mask(7,7), 0b10000000)

    def test_extract_bits(self):
        self.assertEqual(utils.extract_bits(0b11111111, 0, 5), 0b00111111)
        self.assertEqual(utils.extract_bits(0b11111111, 2, 3), 0b11)
        self.assertEqual(utils.extract_bits(0b11111111, 7, 7,), 0b1)

    def test_inject_bits(self):
        self.assertEqual(utils.inject_bits(0b11111111, 0b00001010, 3, 6),
                         0b11010111)

    def test_inject_mirrors_extract(self):
        original_bits = 0b11110101

        extracted = utils.extract_bits(0b11110101, 2, 5)

        self.assertEqual(extracted, 0b1101)

        new_bits = 0

        new_bits = utils.inject_bits(new_bits, extracted, 2, 5)

        self.assertEqual(new_bits, 0b00110100)

if __name__ == "__main__":
    unittest.main()
