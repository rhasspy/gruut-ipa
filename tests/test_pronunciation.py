#!/usr/bin/env python3
"""Tests for Pronunciation class"""
import unittest

from gruut_ipa import IPA, Pronunciation


class PronunciationTestCase(unittest.TestCase):
    """Test cases for Pronunciation class"""

    def test_from_string(self):
        """Test Pronuncation.from_string"""
        # "Yes, choose IPA."
        pron_str = "↗ˈjɛs|ˈt͡ʃuːz#↘aɪpiːeɪ‖"

        pron = Pronunciation.from_string(pron_str, keep_stress=False)

        phone_strs = [p.text for p in pron.phones]
        self.assertEqual(
            phone_strs, ["j", "ɛ", "s", "t͡ʃ", "uː", "z", "a", "ɪ", "p", "iː", "e", "ɪ"]
        )

        phone_strs = [p.text for p in pron]
        self.assertEqual(
            phone_strs,
            [
                IPA.INTONATION_RISING,
                "j",
                "ɛ",
                "s",
                IPA.BREAK_MINOR,
                "t͡ʃ",
                "uː",
                "z",
                IPA.BREAK_WORD,
                IPA.INTONATION_FALLING,
                "a",
                "ɪ",
                "p",
                "iː",
                "e",
                "ɪ",
                IPA.BREAK_MAJOR,
            ],
        )

    def test_diacritics(self):
        """Test Pronuncation.from_string with extra diacritics"""
        pron_str = "ɔʊ̯"
        pron = Pronunciation.from_string(pron_str)

        self.assertEqual(pron.text, pron_str)

    def test_tones(self):
        """Test Pronuncation.from_string with tone numbers"""
        pron_str = "/hwiən˧˨ ziəw˨ˀ˩ʔ/"
        pron = Pronunciation.from_string(pron_str)

        phone_strs = [p.text for p in pron]
        self.assertEqual(
            phone_strs, ["h", "w", "i", "ə", "n˧˨", "z", "i", "ə", "w˨ˀ˩ʔ"]
        )

    def test_accents(self):
        """Test Pronuncation.from_string with accents"""
        pron_str = "/²'alːdɑːglɪg/"
        pron = Pronunciation.from_string(pron_str)

        phone_strs = [p.text for p in pron]
        self.assertEqual(phone_strs, ["²'a", "lː", "d", "ɑː", "g", "l", "ɪ", "g"])


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
