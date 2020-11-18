"""Enums, vowels, and consonants for gruut-ipa"""
import typing
import unicodedata
from dataclasses import dataclass
from enum import Enum


class IPA(str, Enum):
    """International phonetic alphabet characters"""

    STRESS_PRIMARY = "\u02C8"  # ˈ
    STRESS_SECONDARY = "\u02CC"  # ˌ

    ACCENT_ACUTE = "'"
    ACCENT_GRAVE = "²"

    LONG = "\u02D0"  # ː
    HALF_LONG = "\u02D1"  # eˑ
    EXTRA_SHORT = "\u0306"  # ə̆
    NASAL = "\u0303"  # ẽ
    RAISED = "\u031D"  # r̝
    TIE_ABOVE = "\u0361"  # ͡
    TIE_BELOW = "\u035C"  # ͜

    SYLLABIC = "\u0329"
    NON_SYLLABIC = "\u032F"

    BREAK_SYLLABLE = "."
    BREAK_MINOR = "|"
    BREAK_MAJOR = "\u2016"  # ‖
    BREAK_WORD = "#"

    INTONATION_RISING = "\u2197"  # ↗
    INTONATION_FALLING = "\u2198"  # ↘

    TONE_1 = "¹"
    TONE_2 = "²"
    TONE_3 = "³"
    TONE_4 = "⁴"
    TONE_5 = "⁵"
    TONE_6 = "⁶"
    TONE_7 = "⁷"
    TONE_8 = "⁸"
    TONE_9 = "⁹"

    TONE_EXTRA_HIGH = "˥"
    TONE_HIGH = "˦"
    TONE_MID = "˧"
    TONE_LOW = "˨"
    TONE_EXTRA_LOW = "˩"

    TONE_GLOTTALIZED = "ˀ"
    TONE_SHORT = "ʔ"

    BRACKET_PHONETIC_LEFT = "["
    BRACKET_PHONETIC_RIGHT = "]"
    BRACKET_PHONEMIC_LEFT = "/"
    BRACKET_PHONEMIC_RIGHT = "/"
    BRACKET_PROSODIC_LEFT = "{"
    BRACKET_PROSODIC_RIGHT = "}"
    BRACKET_OPTIONAL_LEFT = "("
    BRACKET_OPTIONAL_RIGHT = ")"

    @staticmethod
    def is_long(codepoint: str) -> bool:
        """True if elongated symbol"""
        return codepoint == IPA.LONG

    @staticmethod
    def is_nasal(codepoint: str) -> bool:
        """True if nasalated diacritic"""
        return codepoint == IPA.NASAL

    @staticmethod
    def is_raised(codepoint: str) -> bool:
        """True if rased diacritic"""
        return codepoint == IPA.RAISED

    @staticmethod
    def is_stress(codepoint: str) -> bool:
        """True if primary/secondary stress symbol"""
        return codepoint in (IPA.STRESS_PRIMARY, IPA.STRESS_SECONDARY)

    @staticmethod
    def is_accent(codepoint: str) -> bool:
        """True if accent symbol"""
        return codepoint in {IPA.ACCENT_ACUTE, IPA.ACCENT_GRAVE}

    @staticmethod
    def is_tie(codepoint: str) -> bool:
        """True if above/below tie symbol"""
        return codepoint in (IPA.TIE_ABOVE, IPA.TIE_BELOW)

    @staticmethod
    def is_bracket(codepoint: str) -> bool:
        """True if any IPA bracket symbol"""
        return codepoint in {
            IPA.BRACKET_PHONETIC_LEFT,
            IPA.BRACKET_PHONETIC_RIGHT,
            IPA.BRACKET_PHONEMIC_LEFT,
            IPA.BRACKET_PHONEMIC_RIGHT,
            IPA.BRACKET_PROSODIC_LEFT,
            IPA.BRACKET_PROSODIC_RIGHT,
            IPA.BRACKET_OPTIONAL_LEFT,
            IPA.BRACKET_OPTIONAL_RIGHT,
        }

    @staticmethod
    def is_break(codepoint: str) -> bool:
        """True if any IPA break symbol"""
        return codepoint in {
            IPA.BREAK_SYLLABLE,
            IPA.BREAK_MINOR,
            IPA.BREAK_MAJOR,
            IPA.BREAK_WORD,
        }

    @staticmethod
    def is_intonation(codepoint: str) -> bool:
        """True if a rising or falling IPA intonation symbol"""
        return codepoint in {IPA.INTONATION_RISING, IPA.INTONATION_FALLING}

    @staticmethod
    def is_tone(codepoint: str) -> bool:
        """True if any IPA tone symbol"""
        return codepoint in {
            IPA.TONE_1,
            IPA.TONE_2,
            IPA.TONE_3,
            IPA.TONE_4,
            IPA.TONE_5,
            IPA.TONE_6,
            IPA.TONE_7,
            IPA.TONE_8,
            IPA.TONE_9,
            IPA.TONE_EXTRA_HIGH,
            IPA.TONE_HIGH,
            IPA.TONE_MID,
            IPA.TONE_LOW,
            IPA.TONE_EXTRA_LOW,
        }

    @staticmethod
    def graphemes(codepoints: str) -> typing.List[str]:
        """Split a string into graphemes"""
        codepoints = unicodedata.normalize("NFD", codepoints)

        graphemes = []
        grapheme = ""

        for c in codepoints:
            if unicodedata.combining(c) > 0:
                grapheme += c
            elif grapheme:
                # Next grapheme
                graphemes.append(unicodedata.normalize("NFC", grapheme))
                grapheme = c
            else:
                # Start of grapheme
                grapheme = c

        if grapheme:
            # Final grapheme
            graphemes.append(unicodedata.normalize("NFC", grapheme))

        return graphemes

    @staticmethod
    def without_stress(codepoints: str, drop_accent: bool = True) -> str:
        """Return string without primary/secondary stress"""
        return "".join(
            c
            for c in codepoints
            if (not IPA.is_stress(c) and (not drop_accent or not IPA.is_accent(c)))
        )


class Stress(str, Enum):
    """Applied stress"""

    NONE = "none"
    PRIMARY = "primary"
    SECONDARY = "secondary"


class Accent(str, Enum):
    """Applied accent"""

    NONE = "none"
    ACUTE = "acute"  # '
    GRAVE = "grave"  # ²


class BreakType(str, Enum):
    """Type of break"""

    MINOR = "minor"  # |
    MAJOR = "major"  # ‖
    WORD = "word"  # '#'


# -----------------------------------------------------------------------------


class VowelHeight(str, Enum):
    """Height of a vowel"""

    CLOSE = "close"
    NEAR_CLOSE = "near-close"
    CLOSE_MID = "close-mid"
    MID = "mid"
    OPEN_MID = "open-mid"
    NEAR_OPEN = "near-open"
    OPEN = "open"


class VowelPlacement(str, Enum):
    """Front/back placement of a vowel"""

    FRONT = "front"
    NEAR_FRONT = "near-front"
    CENTRAL = "central"
    NEAR_BACK = "near-back"
    BACK = "back"


@dataclass
class Vowel:
    """Necessary information for a vowel"""

    ipa: str
    height: VowelHeight
    placement: VowelPlacement
    rounded: bool


# -----------------------------------------------------------------
# Vowels        Front    Near-Front    Central    Near-Back    Back
# -----------------------------------------------------------------
# Close         i/y                    ɨ/ʉ                     ɯ/u
# Near-Close             ɪ/ʏ                      ʊ
# Close-Mid     e/ø                    ɘ/ɵ                     ɤ/o
# Mid                                  ə
# Open-Mid      ɛ/œ                    ɜ/ɞ                     ʌ/ɔ
# Near-Open     æ                      ɐ
# Open          a/ɶ                                            ɑ/ɒ
# -----------------------------------------------------------------


_VOWELS = [
    Vowel("i", VowelHeight.CLOSE, VowelPlacement.FRONT, False),
    Vowel("y", VowelHeight.CLOSE, VowelPlacement.FRONT, True),
    Vowel("ɨ", VowelHeight.CLOSE, VowelPlacement.CENTRAL, False),
    Vowel("ʉ", VowelHeight.CLOSE, VowelPlacement.CENTRAL, True),
    Vowel("ɯ", VowelHeight.CLOSE, VowelPlacement.BACK, False),
    Vowel("u", VowelHeight.CLOSE, VowelPlacement.BACK, True),
    #
    Vowel("ɪ", VowelHeight.NEAR_CLOSE, VowelPlacement.NEAR_FRONT, False),
    Vowel("ʏ", VowelHeight.NEAR_CLOSE, VowelPlacement.NEAR_FRONT, True),
    Vowel("ʊ", VowelHeight.NEAR_CLOSE, VowelPlacement.NEAR_BACK, True),
    #
    Vowel("e", VowelHeight.CLOSE_MID, VowelPlacement.FRONT, False),
    Vowel("ø", VowelHeight.CLOSE_MID, VowelPlacement.FRONT, True),
    Vowel("ɘ", VowelHeight.CLOSE_MID, VowelPlacement.CENTRAL, False),
    Vowel("ɵ", VowelHeight.CLOSE_MID, VowelPlacement.CENTRAL, True),
    Vowel("ɤ", VowelHeight.CLOSE_MID, VowelPlacement.BACK, False),
    Vowel("o", VowelHeight.CLOSE_MID, VowelPlacement.BACK, True),
    #
    # Represented as a schwa
    # Vowel("ə", VowelHeight.MID, VowelPlacement.CENTRAL, False),
    #
    Vowel("ɛ", VowelHeight.OPEN_MID, VowelPlacement.FRONT, False),
    Vowel("œ", VowelHeight.OPEN_MID, VowelPlacement.FRONT, True),
    Vowel("ɜ", VowelHeight.OPEN_MID, VowelPlacement.CENTRAL, False),
    Vowel("ɞ", VowelHeight.OPEN_MID, VowelPlacement.CENTRAL, True),
    Vowel("ʌ", VowelHeight.OPEN_MID, VowelPlacement.BACK, False),
    Vowel("ɔ", VowelHeight.OPEN_MID, VowelPlacement.BACK, True),
    #
    Vowel("æ", VowelHeight.NEAR_OPEN, VowelPlacement.FRONT, False),
    Vowel("ɐ", VowelHeight.NEAR_OPEN, VowelPlacement.CENTRAL, False),
    #
    Vowel("a", VowelHeight.OPEN, VowelPlacement.FRONT, False),
    Vowel("ɶ", VowelHeight.OPEN, VowelPlacement.FRONT, True),
    Vowel("ɑ", VowelHeight.OPEN, VowelPlacement.BACK, False),
    Vowel("ɒ", VowelHeight.OPEN, VowelPlacement.BACK, True),
]

VOWELS = {v.ipa: v for v in _VOWELS}

# -----------------------------------------------------------------------------


@dataclass
class Dipthong:
    """Combination of two vowels"""

    vowel1: Vowel
    vowel2: Vowel


# -----------------------------------------------------------------------------


@dataclass
class Schwa:
    """Vowel-like sound"""

    ipa: str
    r_coloured: bool


_SCHWAS = [Schwa("ə", False), Schwa("ɚ", True), Schwa("ɝ", True), Schwa("ɹ̩", True)]

SCHWAS = {s.ipa: s for s in _SCHWAS}

# -----------------------------------------------------------------------------


class ConsonantType(str, Enum):
    """Type of a consonant"""

    NASAL = "nasal"
    PLOSIVE = "plosive"
    AFFRICATE = "affricate"
    FRICATIVE = "fricative"
    APPROXIMANT = "approximant"
    FLAP = "flap"
    TRILL = "trill"
    LATERAL_APPROXIMANT = "lateral-approximant"


class ConsonantPlace(str, Enum):
    """Place of articulation"""

    BILABIAL = "bilabial"
    LABIO_DENTAL = "labio-dental"
    DENTAL = "dental"
    ALVEOLAR = "alveolar"
    POST_ALVEOLAR = "post-alveolar"
    RETROFLEX = "retroflex"
    PALATAL = "palatal"
    VELAR = "velar"
    UVULAR = "uvular"
    PHARYNGEAL = "pharyngeal"
    GLOTTAL = "glottal"


@dataclass
class Consonant:
    """Necessary information for a consonant"""

    ipa: str
    type: ConsonantType
    place: ConsonantPlace
    voiced: bool


# --------------------------------------------------------------------------------------------------------------------------------------------
# Type         Bilabial    Labiodental    Dental    Alveolar    Postalveolar    Retroflex  Palatal    Velar    Uvular    Pharyngeal    Glottal
# --------------------------------------------------------------------------------------------------------------------------------------------
# Nasal        m           ɱ                        n                           ɳ          ɲ          ŋ        ɴ
# Plosive      p/b                                  t/d                         ʈ/ɖ        c/ɟ        k/ɡ      q/ɢ       ʡ             ʔ
# Affricate                p͡f/b͡v          t̪͡s̪/b͡v̪     t͡s/d͡z       t͡ʃ/d͡ʒ           ʈ͡ʂ/ɖ͡ʐ      t͡ɕ/d͡ʑ      k͡x
# Fricative    ɸ/β         f/v            θ/ð       s/z         ʃ/ʒ             ʂ/ʐ        ç/ʝ        x/ɣ      χ/ʁ       ħ             h ɦ
# Approximant  w           ʋ                        ɹ                           ɻ          j          ɰ
# Flap                     ⱱ                        ɾ                           ɽ
# Trill        ʙ                                    r                                                          ʀ
# Lateral App                                       l                           ɭ          ʎ          ʟ
# --------------------------------------------------------------------------------------------------------------------------------------------

_CONSONANTS = [
    Consonant("m", ConsonantType.NASAL, ConsonantPlace.BILABIAL, True),
    Consonant("ɱ", ConsonantType.NASAL, ConsonantPlace.LABIO_DENTAL, True),
    Consonant("n", ConsonantType.NASAL, ConsonantPlace.ALVEOLAR, True),
    Consonant("ɳ", ConsonantType.NASAL, ConsonantPlace.RETROFLEX, True),
    Consonant("ɲ", ConsonantType.NASAL, ConsonantPlace.PALATAL, True),
    Consonant("ŋ", ConsonantType.NASAL, ConsonantPlace.VELAR, True),
    Consonant("ɴ", ConsonantType.NASAL, ConsonantPlace.UVULAR, True),
    #
    Consonant("p", ConsonantType.PLOSIVE, ConsonantPlace.BILABIAL, False),
    Consonant("b", ConsonantType.PLOSIVE, ConsonantPlace.BILABIAL, True),
    Consonant("t", ConsonantType.PLOSIVE, ConsonantPlace.ALVEOLAR, False),
    Consonant("d", ConsonantType.PLOSIVE, ConsonantPlace.ALVEOLAR, True),
    Consonant("ʈ", ConsonantType.PLOSIVE, ConsonantPlace.RETROFLEX, False),
    Consonant("ɖ", ConsonantType.PLOSIVE, ConsonantPlace.RETROFLEX, True),
    Consonant("c", ConsonantType.PLOSIVE, ConsonantPlace.PALATAL, False),
    Consonant("ɟ", ConsonantType.PLOSIVE, ConsonantPlace.PALATAL, True),
    Consonant("k", ConsonantType.PLOSIVE, ConsonantPlace.VELAR, False),
    Consonant("ɡ", ConsonantType.PLOSIVE, ConsonantPlace.VELAR, True),
    Consonant("g", ConsonantType.PLOSIVE, ConsonantPlace.VELAR, True),
    Consonant("q", ConsonantType.PLOSIVE, ConsonantPlace.UVULAR, False),
    Consonant("ɢ", ConsonantType.PLOSIVE, ConsonantPlace.UVULAR, True),
    Consonant("ʡ", ConsonantType.PLOSIVE, ConsonantPlace.PHARYNGEAL, False),
    Consonant("ʔ", ConsonantType.PLOSIVE, ConsonantPlace.GLOTTAL, False),
    #
    Consonant("p͡f", ConsonantType.AFFRICATE, ConsonantPlace.LABIO_DENTAL, False),
    Consonant("b͡v", ConsonantType.AFFRICATE, ConsonantPlace.LABIO_DENTAL, True),
    Consonant("t̪͡s", ConsonantType.AFFRICATE, ConsonantPlace.DENTAL, False),
    Consonant("b͡v", ConsonantType.AFFRICATE, ConsonantPlace.DENTAL, True),
    Consonant("t͡s", ConsonantType.AFFRICATE, ConsonantPlace.ALVEOLAR, False),
    Consonant("d͡z", ConsonantType.AFFRICATE, ConsonantPlace.ALVEOLAR, True),
    Consonant("t͡ʃ", ConsonantType.AFFRICATE, ConsonantPlace.POST_ALVEOLAR, False),
    Consonant("d͡ʒ", ConsonantType.AFFRICATE, ConsonantPlace.POST_ALVEOLAR, True),
    Consonant("ʈ͡ʂ", ConsonantType.AFFRICATE, ConsonantPlace.RETROFLEX, False),
    Consonant("ɖ͡ʐ", ConsonantType.AFFRICATE, ConsonantPlace.RETROFLEX, True),
    Consonant("t͡ɕ", ConsonantType.AFFRICATE, ConsonantPlace.PALATAL, False),
    Consonant("d͡ʑ", ConsonantType.AFFRICATE, ConsonantPlace.PALATAL, True),
    Consonant("k͡x", ConsonantType.AFFRICATE, ConsonantPlace.VELAR, False),
    #
    Consonant("ɸ", ConsonantType.FRICATIVE, ConsonantPlace.BILABIAL, False),
    Consonant("β", ConsonantType.FRICATIVE, ConsonantPlace.BILABIAL, True),
    Consonant("f", ConsonantType.FRICATIVE, ConsonantPlace.LABIO_DENTAL, False),
    Consonant("v", ConsonantType.FRICATIVE, ConsonantPlace.LABIO_DENTAL, True),
    Consonant("θ", ConsonantType.FRICATIVE, ConsonantPlace.DENTAL, False),
    Consonant("ð", ConsonantType.FRICATIVE, ConsonantPlace.DENTAL, True),
    Consonant("s", ConsonantType.FRICATIVE, ConsonantPlace.ALVEOLAR, False),
    Consonant("z", ConsonantType.FRICATIVE, ConsonantPlace.ALVEOLAR, True),
    Consonant("ʃ", ConsonantType.FRICATIVE, ConsonantPlace.POST_ALVEOLAR, False),
    Consonant("ʒ", ConsonantType.FRICATIVE, ConsonantPlace.POST_ALVEOLAR, True),
    Consonant("ʂ", ConsonantType.FRICATIVE, ConsonantPlace.RETROFLEX, False),
    Consonant("ʐ", ConsonantType.FRICATIVE, ConsonantPlace.RETROFLEX, True),
    Consonant("ç", ConsonantType.FRICATIVE, ConsonantPlace.PALATAL, False),
    Consonant("ʐ", ConsonantType.FRICATIVE, ConsonantPlace.PALATAL, True),
    Consonant("x", ConsonantType.FRICATIVE, ConsonantPlace.VELAR, False),
    Consonant("ɣ", ConsonantType.FRICATIVE, ConsonantPlace.VELAR, True),
    Consonant("χ", ConsonantType.FRICATIVE, ConsonantPlace.UVULAR, False),
    Consonant("ʁ", ConsonantType.FRICATIVE, ConsonantPlace.UVULAR, True),
    Consonant("ħ", ConsonantType.FRICATIVE, ConsonantPlace.PHARYNGEAL, False),
    Consonant("h", ConsonantType.FRICATIVE, ConsonantPlace.GLOTTAL, False),
    Consonant("ɦ", ConsonantType.FRICATIVE, ConsonantPlace.GLOTTAL, True),
    #
    Consonant("w", ConsonantType.APPROXIMANT, ConsonantPlace.BILABIAL, True),
    Consonant("ʋ", ConsonantType.APPROXIMANT, ConsonantPlace.LABIO_DENTAL, True),
    Consonant("ɹ", ConsonantType.APPROXIMANT, ConsonantPlace.ALVEOLAR, True),
    Consonant("ɻ", ConsonantType.APPROXIMANT, ConsonantPlace.RETROFLEX, True),
    Consonant("j", ConsonantType.APPROXIMANT, ConsonantPlace.PALATAL, True),
    Consonant("ɰ", ConsonantType.APPROXIMANT, ConsonantPlace.VELAR, True),
    #
    Consonant("ⱱ", ConsonantType.FLAP, ConsonantPlace.LABIO_DENTAL, True),
    Consonant("ɾ", ConsonantType.FLAP, ConsonantPlace.ALVEOLAR, True),
    Consonant("ɽ", ConsonantType.FLAP, ConsonantPlace.RETROFLEX, True),
    #
    Consonant("ʙ", ConsonantType.TRILL, ConsonantPlace.BILABIAL, True),
    Consonant("r", ConsonantType.TRILL, ConsonantPlace.ALVEOLAR, True),
    Consonant("ʀ", ConsonantType.TRILL, ConsonantPlace.UVULAR, True),
    #
    Consonant("l", ConsonantType.LATERAL_APPROXIMANT, ConsonantPlace.ALVEOLAR, True),
    Consonant("ɫ", ConsonantType.LATERAL_APPROXIMANT, ConsonantPlace.ALVEOLAR, True),
    Consonant("ɭ", ConsonantType.LATERAL_APPROXIMANT, ConsonantPlace.RETROFLEX, True),
    Consonant("ʎ", ConsonantType.LATERAL_APPROXIMANT, ConsonantPlace.PALATAL, True),
    Consonant("ʟ", ConsonantType.LATERAL_APPROXIMANT, ConsonantPlace.VELAR, True),
]

CONSONANTS = {c.ipa: c for c in _CONSONANTS}
