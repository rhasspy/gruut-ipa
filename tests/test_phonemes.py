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

    def test_split_substring(self):
        """Test Phonemes.split with a substring replacement"""
        pron_str = "/viːtɛt͡ʃnaː/"

        lang_phonemes = Phonemes.from_language("cs-cz")
        pron_phonemes = lang_phonemes.split(pron_str, keep_stress=False)

        # Ensure iː doesn't get transformed into ɪː
        phoneme_strs = [p.text for p in pron_phonemes]
        self.assertEqual(phoneme_strs, ["v", "iː", "t", "ɛ", "t͡ʃ", "n", "aː"])

    def test_split_diacritics(self):
        """Test Phonemes.split with a diacritic substring replacement"""
        pron_str = "/ɑɑ̃/"

        lang_phonemes = Phonemes.from_language("fr-fr")
        pron_phonemes = lang_phonemes.split(pron_str, keep_stress=False)

        # Ensure first ɑ is transformed into a, but not the second
        phoneme_strs = [p.text for p in pron_phonemes]
        self.assertEqual(phoneme_strs, ["a", "ɑ̃"])

    def test_dipthong(self):
        """Test Phonemes.from_string with a dipthong"""
        # ampliam
        pron_str = "/ɐ̃pliɐ̃w̃/"

        lang_phonemes = Phonemes.from_language("pt")
        pron_phonemes = lang_phonemes.split(pron_str)

        # Ensure "ɐ̃" and "ɐ̃w̃" are kept
        phoneme_strs = [p.text for p in pron_phonemes]
        self.assertEqual(phoneme_strs, ["ɐ̃", "p", "l", "i", "ɐ̃w̃"])

    def test_split_dipthong(self):
        """Test Phonemes.split with a dipthong"""
        pron_str = "/neu̯rt͡ʃɪtou̯/"

        lang_phonemes = Phonemes.from_language("cs-cz")
        pron_phonemes = lang_phonemes.split(pron_str, keep_stress=False)

        # Ensure eu̯ ends up as eu̯
        phoneme_strs = [p.text for p in pron_phonemes]
        self.assertEqual(phoneme_strs, ["n", "eu̯", "r", "t͡ʃ", "ɪ", "t", "ou̯"])

    def test_tones(self):
        """Test Phonemes.split with tones"""
        # á khôi
        pron_str = "/a˨˦xoj˧˧/"

        lang_phonemes = Phonemes.from_language("vi-n")
        pron_phonemes = lang_phonemes.split(pron_str)

        # Ensure tones are kept
        phoneme_strs = [p.text for p in pron_phonemes]
        self.assertEqual(phoneme_strs, ["a˨˦", "x", "oj˧˧"])


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
