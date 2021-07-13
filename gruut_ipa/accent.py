"""Methods for mapping phonemes from one language to another"""
import typing

from . import Phoneme, Phonemes
from .constants import (
    Consonant,
    ConsonantPlace,
    ConsonantType,
    Vowel,
    VowelHeight,
    VowelPlacement,
)

# ---------------------------------------------------------------------

R_LIKE = ["ɹ", "ʁ", "r", "ʀ", "ɻ"]
SCHWA_PREFERRED = ["ə", "ɐ"]
GS = ["ɡ", "g"]


def guess_phonemes(
    from_phoneme: typing.Union[str, Phoneme], to_phonemes: Phonemes
) -> typing.Optional[typing.Union[str, typing.List[str]]]:
    """Get best single phoneme match"""
    best_to_phoneme: typing.Optional[str] = None
    min_dist: typing.Optional[float] = None

    if isinstance(from_phoneme, str):
        from_phoneme = Phoneme(from_phoneme)

    if from_phoneme.text in GS:
        # Correctly map two forms of "g"
        for maybe_g in GS:
            if maybe_g in to_phonemes:
                return maybe_g

    if from_phoneme.schwa:
        for maybe_schwa in SCHWA_PREFERRED:
            # Try known schwa preferences
            if maybe_schwa in to_phonemes:
                return maybe_schwa

        if from_phoneme.schwa.r_coloured:
            # Try r-like
            for maybe_r_like in R_LIKE:
                if maybe_r_like in to_phonemes:
                    return maybe_r_like

        # Treat as a mid-central vowel
        setattr(
            from_phoneme,
            "vowel",
            Vowel(
                ipa="ə",
                height=VowelHeight.MID,
                placement=VowelPlacement.CENTRAL,
                rounded=False,
            ),
        )

    for to_phoneme in to_phonemes:
        if from_phoneme.text == to_phoneme.text:
            # Easy case
            return to_phoneme.text

        if (not from_phoneme.dipthong) and (from_phoneme.letters == to_phoneme.letters):
            # Match except for elongation, accent
            return to_phoneme.text

        if from_phoneme.vowel and to_phoneme.vowel:
            # Vowel distance
            dist = vowel_distance(from_phoneme.vowel, to_phoneme.vowel)
            dist += 0.5 if from_phoneme.elongated != to_phoneme.elongated else 0

            if (min_dist is None) or (dist < min_dist):
                min_dist = dist
                best_to_phoneme = to_phoneme.text

        elif from_phoneme.consonant and to_phoneme.consonant:
            # Consonant distance
            dist = consonant_distance(from_phoneme.consonant, to_phoneme.consonant)
            dist += 0.5 if from_phoneme.elongated != to_phoneme.elongated else 0

            if (min_dist is None) or (dist < min_dist):
                min_dist = dist
                best_to_phoneme = to_phoneme.text

        elif from_phoneme.dipthong:
            # Split dithong apart and match
            best_to_phoneme_1 = None
            best_to_phoneme_1_dist = None

            best_to_phoneme_2 = None
            best_to_phoneme_2_dist = None

            for to_phoneme_vowel in to_phonemes:
                if not to_phoneme_vowel.vowel:
                    continue

                dist1 = vowel_distance(
                    from_phoneme.dipthong.vowel1, to_phoneme_vowel.vowel
                )
                dist2 = vowel_distance(
                    from_phoneme.dipthong.vowel2, to_phoneme_vowel.vowel
                )

                if (best_to_phoneme_1_dist is None) or (dist1 < best_to_phoneme_1_dist):
                    # First vowel
                    best_to_phoneme_1 = to_phoneme_vowel
                    best_to_phoneme_1_dist = dist1

                if (best_to_phoneme_2_dist is None) or (dist2 < best_to_phoneme_2_dist):
                    # Second vowel
                    best_to_phoneme_2 = to_phoneme_vowel
                    best_to_phoneme_2_dist = dist2

            if (best_to_phoneme_1 is not None) and (best_to_phoneme_2 is not None):
                return [best_to_phoneme_1.text, best_to_phoneme_2.text]

    return best_to_phoneme


def guess_phoneme_map(
    from_phonemes: typing.Union[str, Phonemes], to_phonemes: typing.Union[str, Phonemes]
) -> typing.Dict[str, typing.Union[str, typing.List[str]]]:
    """Guess a phoneme mapping from one language to another"""
    if isinstance(from_phonemes, str):
        from_phonemes = Phonemes.from_language(from_phonemes)

    if isinstance(to_phonemes, str):
        to_phonemes = Phonemes.from_language(to_phonemes)

    # Guess mapping
    mapping = {}
    for from_phoneme in from_phonemes:
        to_phoneme_str = guess_phonemes(from_phoneme, to_phonemes)
        if to_phoneme_str is None:
            continue

        if (from_phoneme.text in R_LIKE) and (to_phoneme_str not in R_LIKE):
            # Re-map r-like
            for maybe_r in R_LIKE:
                if maybe_r in to_phonemes:
                    to_phoneme_str = maybe_r
                    break

        mapping[from_phoneme.text] = to_phoneme_str

    return mapping


# ---------------------------------------------------------------------

VOWEL_HEIGHT_NUM = {h: i for i, h in enumerate(VowelHeight)}
VOWEL_PLACE_NUM = {p: i for i, p in enumerate(VowelPlacement)}


def vowel_distance(vowel_1: Vowel, vowel_2: Vowel) -> float:
    """Return a distance measure between two vowels"""
    dist_height = (
        abs(VOWEL_HEIGHT_NUM[vowel_1.height] - VOWEL_HEIGHT_NUM[vowel_2.height]) * 2
    )
    dist_place = abs(
        VOWEL_PLACE_NUM[vowel_1.placement] - VOWEL_PLACE_NUM[vowel_2.placement]
    )
    dist_rounded = 1 if vowel_1.rounded != vowel_2.rounded else 0

    return dist_height + dist_place + dist_rounded


CONSONANT_TYPE_NUM = {t: i for i, t in enumerate(ConsonantType)}
CONSONANT_PLACE_NUM = {p: i for i, p in enumerate(ConsonantPlace)}


def consonant_distance(consonant_1: Consonant, consonant_2: Consonant) -> float:
    """Return a distance measure between two consonants"""
    dist_type = abs(
        CONSONANT_TYPE_NUM[consonant_1.type] - CONSONANT_TYPE_NUM[consonant_2.type]
    )
    # dist_type = 1 if consonant_1.type != consonant_2.type else 0
    dist_place = abs(
        CONSONANT_PLACE_NUM[consonant_1.place] - CONSONANT_PLACE_NUM[consonant_2.place]
    )
    dist_voiced = 1 if consonant_1.voiced != consonant_2.voiced else 0

    return dist_type + dist_place + dist_voiced
