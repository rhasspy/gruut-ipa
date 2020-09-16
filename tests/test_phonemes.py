#!/usr/bin/env python3
"""Tests for Phonemes class"""
import unittest

from gruut_ipa import Phonemes


class PhonemesTestCase(unittest.TestCase):
    """Test cases for Phonemes class"""

    def test_split(self):
        """Test Phonemes.from_string"""
        # "Just a cow."
        pron_str = "/dʒʌst ə kˈaʊ/"

        lang_phonemes = Phonemes.from_language("en-us")
        pron_phonemes = lang_phonemes.split(pron_str, keep_stress=True)

        # Ensure "d ʒ" -> "d͡ʒ" and "a ʊ" -> "aʊ"
        phoneme_strs = [p.text for p in pron_phonemes]
        self.assertEqual(phoneme_strs, ["d͡ʒ", "ʌ", "s", "t", "ə", "k", "ˈaʊ"])


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
