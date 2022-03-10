"""Classes for dealing with phones and phonemes"""
from gruut_ipa.accent import GuessedPhonemes, guess_phonemes  # noqa: F401
from gruut_ipa.constants import (  # noqa: F401
    CONSONANTS,
    FEATURE_COLUMNS,
    FEATURE_EMPTY,
    FEATURE_KEYS,
    FEATURE_ORDINAL_COLUMNS,
    IPA,
    LANG_ALIASES,
    SCHWAS,
    VOWELS,
    Accent,
    Break,
    BreakType,
    Consonant,
    ConsonantPlace,
    ConsonantType,
    Dipthong,
    Intonation,
    PhonemeLength,
    Schwa,
    Stress,
    Vowel,
    VowelHeight,
    VowelPlacement,
)
from gruut_ipa.distances import get_closest  # noqa: F401
from gruut_ipa.espeak import espeak_to_ipa, ipa_to_espeak  # noqa: F401
from gruut_ipa.features import from_vector, string_to_symbol, to_vector  # noqa: F401
from gruut_ipa.phonemes import Phone, Phoneme, Phonemes, Pronunciation  # noqa: F401
from gruut_ipa.sampa import ipa_to_sampa, sampa_to_ipa  # noqa: F401
from gruut_ipa.utils import resolve_lang  # noqa:F401
