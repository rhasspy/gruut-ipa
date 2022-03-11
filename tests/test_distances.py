#!/usr/bin/env python3
"""Tests for phoneme distances"""
import unittest

from gruut_ipa import get_closest


class DistancesTestCase(unittest.TestCase):
    """Test cases for phoneme distances"""

    def test_vowels(self):
        """Test distances for vowels"""
        self.assertEqual(get_closest("p")[0], "t")

    def test_consonants(self):
        """Test distances for consonants"""
        self.assertEqual(get_closest("ɑ")[0], "ɒ")
        self.assertEqual(get_closest("ʝ")[0], "ç")

    def test_schwas(self):
        """Test distances for schwas"""
        self.assertEqual(get_closest("ɝ")[0], "ɚ")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
