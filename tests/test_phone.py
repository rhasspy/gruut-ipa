#!/usr/bin/env python3
"""Tests for Phone class"""
import unicodedata
import unittest

from gruut_ipa import IPA, Phone, Stress, VowelHeight, VowelPlacement


class PhoneTestCase(unittest.TestCase):
    """Test cases for Phone class"""

    def test_from_string(self):
        """Test Phone.from_string"""
        # ˈãː
        codepoints = [IPA.STRESS_PRIMARY, "a", IPA.NASAL, IPA.LONG]
        ipa = "".join(codepoints)

        phone = Phone.from_string(ipa)

        # Important: text is NFC normalized, so combining characters are
        # elimiated if possible.
        self.assertEqual(phone.text, unicodedata.normalize("NFC", "ˈãː"))

        self.assertEqual(phone.letters, "a")
        self.assertEqual(phone.diacritics[0], {IPA.NASAL})
        self.assertEqual(phone.suprasegmentals, {IPA.STRESS_PRIMARY, IPA.LONG})

        self.assertEqual(phone.stress, Stress.PRIMARY)
        self.assertTrue(phone.is_nasal)
        self.assertTrue(phone.is_long)

        self.assertTrue(phone.is_vowel)
        self.assertEqual(phone.vowel.height, VowelHeight.OPEN)
        self.assertEqual(phone.vowel.placement, VowelPlacement.FRONT)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
