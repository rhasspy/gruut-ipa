#!/usr/bin/env python3
"""Tests for phoneme features"""
import dataclasses
import unittest

from gruut_ipa import (
    CONSONANTS,
    SCHWAS,
    VOWELS,
    Break,
    BreakType,
    PhonemeLength,
    Stress,
    from_vector,
    string_to_symbol,
    to_vector,
)


class FeaturesTestCase(unittest.TestCase):
    """Test cases for phoneme features"""

    def test_vowels(self):
        """Test to/from feature vector for vowels"""
        for vowel in VOWELS.values():
            if vowel.alias_of:
                continue

            feat_vec = to_vector(vowel)
            self.assertEqual(vowel, from_vector(feat_vec))

            # Test with stress
            for stress in Stress:
                vowel_stressed = dataclasses.replace(vowel, stress=stress)
                feat_vec = to_vector(vowel_stressed)
                self.assertEqual(vowel_stressed, from_vector(feat_vec))

    def test_consonants(self):
        """Test to/from feature vector for consonants"""
        for consonant in CONSONANTS.values():
            if consonant.alias_of:
                continue

            feat_vec = to_vector(consonant)
            self.assertEqual(consonant, from_vector(feat_vec))

    def test_schwas(self):
        """Test to/from feature vector for schwas"""
        for schwa in SCHWAS.values():
            if schwa.alias_of:
                continue

            feat_vec = to_vector(schwa)
            self.assertEqual(schwa, from_vector(feat_vec))

    def test_breaks(self):
        """Test to/from feature vector for breaks"""
        for break_type in BreakType:
            ipa_break = Break(break_type)
            feat_vec = to_vector(ipa_break)
            self.assertEqual(ipa_break, from_vector(feat_vec))

    def test_string_to_symbol(self):
        """Test symbol parsing"""
        self.assertEqual(
            string_to_symbol("ˈãː"),
            dataclasses.replace(
                VOWELS["ã"], stress=Stress.PRIMARY, length=PhonemeLength.LONG
            ),
        )

        self.assertEqual(
            string_to_symbol("ɫː"),
            dataclasses.replace(CONSONANTS["ɫ"], length=PhonemeLength.LONG),
        )

        self.assertEqual(
            string_to_symbol("ɚː"),
            dataclasses.replace(SCHWAS["ɚ"], length=PhonemeLength.LONG),
        )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
