#!/usr/bin/env python3
"""Tests for phoneme conversion between languages"""
import unittest

from gruut_ipa import Phonemes
from gruut_ipa.accent import guess_phonemes


class AccentTestCase(unittest.TestCase):
    """Test cases for phoneme conversion between languages"""

    @classmethod
    def setUpClass(cls):
        cls.de_phonemes = Phonemes.from_language("de-de")

    def test_exact(self):
        """Test exact match"""
        guessed = guess_phonemes("k", self.de_phonemes)

        self.assertEqual(len(guessed), 1)
        self.assertEqual(guessed[0].text, "k")

    def test_letters(self):
        """Test matching letters"""
        guessed = guess_phonemes("ɐ̯ː", self.de_phonemes)

        self.assertEqual(len(guessed), 1)
        self.assertEqual(guessed[0].text, "ɐ")

    def test_close_vowel(self):
        """Test nearby vowel"""
        guessed = guess_phonemes("ɑ", self.de_phonemes)

        self.assertEqual(len(guessed), 1)

        # Placement is more important that height
        self.assertEqual(guessed[0].text, "a")

    def test_close_consonant(self):
        """Test nearby consonant"""
        guessed = guess_phonemes("ð", self.de_phonemes)

        self.assertEqual(len(guessed), 1)

        # Should match a nearby voiced consonant
        self.assertIn(guessed[0].text, {"v", "z"})

    def test_dipthong_letters_match(self):
        """Test dipthong (two vowels) with matching letters"""
        guessed = guess_phonemes("aʊ", self.de_phonemes)

        self.assertEqual(len(guessed), 1)
        self.assertEqual(guessed[0].text, "aʊ̯")

    def test_dipthong_split(self):
        """Test dipthong (two vowels) split into two phonemes"""
        guessed = guess_phonemes("oʊ", self.de_phonemes)

        self.assertEqual(len(guessed), 2)
        self.assertEqual(guessed[0].text, "oː")
        self.assertEqual(guessed[1].text, "ʊ")

    def test_g(self):
        """Test ɡ/g mapping"""
        from gruut_ipa.accent import GS

        for g in GS:
            guessed = guess_phonemes(g, self.de_phonemes)

            self.assertEqual(len(guessed), 1)
            self.assertIn(guessed[0].text, GS)

    def test_r(self):
        """Test r-like mapping"""
        from gruut_ipa.accent import R_LIKE

        for r in R_LIKE:
            guessed = guess_phonemes(r, self.de_phonemes)

            self.assertEqual(len(guessed), 1)
            self.assertIn(guessed[0].text, R_LIKE)

    def test_schwa(self):
        """Test schwa mapping"""
        from gruut_ipa.constants import SCHWAS
        from gruut_ipa.accent import R_LIKE, SCHWA_PREFERRED

        for s in SCHWAS:
            guessed = guess_phonemes(s, self.de_phonemes)

            self.assertEqual(len(guessed), 1)
            self.assertIn(guessed[0].text, SCHWA_PREFERRED + R_LIKE)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
