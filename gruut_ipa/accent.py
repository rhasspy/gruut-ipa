"""Methods for mapping phonemes from one language to another"""
import typing
import unicodedata
from copy import copy

from . import Phoneme, Phonemes, Pronunciation
from .constants import (
    Consonant,
    ConsonantPlace,
    ConsonantType,
    Vowel,
    VowelHeight,
    VowelPlacement,
)

# ---------------------------------------------------------------------

R_LIKE = ["ɹ", "ʁ", "r", "ʀ", "ɻ", "ɚ"]
SCHWA_PREFERRED = ["ə", "ɐ"]
GS = ["ɡ", "g"]

MATCHING_PHONEMES = typing.List[Phoneme]
PHONEMES_AND_DISTANCE = typing.Tuple[MATCHING_PHONEMES, typing.Optional[float]]


def guess_phonemes(
    from_phoneme: typing.Union[str, Phoneme],
    to_phonemes: Phonemes,
    return_distance: bool = False,
) -> typing.Union[MATCHING_PHONEMES, PHONEMES_AND_DISTANCE]:
    """Get best matching phonemes for a single phoneme"""
    best_phonemes: MATCHING_PHONEMES = []
    best_dist: typing.Optional[float] = None

    from_codepoints: typing.Optional[typing.Set[str]] = None

    if isinstance(from_phoneme, str):
        # Parse phoneme
        from_phoneme = Phoneme(from_phoneme)

    if from_phoneme.text in GS:
        # Correctly map two forms of "g"
        for maybe_g in GS:
            if maybe_g in to_phonemes:
                best_phonemes = [Phoneme(maybe_g)]
                best_dist = 0.0
                break

    if (not best_phonemes) and from_phoneme.schwa:
        if from_phoneme.schwa.r_coloured:
            # Try r-like
            for maybe_r_like in R_LIKE:
                if maybe_r_like in to_phonemes:
                    best_phonemes = [Phoneme(maybe_r_like)]
                    best_dist = 0.0
                    break

        if not best_phonemes:
            for maybe_schwa in SCHWA_PREFERRED:
                # Try known schwa preferences
                if maybe_schwa in to_phonemes:
                    best_phonemes = [Phoneme(maybe_schwa)]
                    best_dist = 0.0
                    break

        if not best_phonemes:
            # Treat as a mid-central vowel
            from_phoneme = copy(from_phoneme)
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

    if (not best_phonemes) and (from_phoneme.text in R_LIKE):
        # Map r-like consonant
        for maybe_r in R_LIKE:
            if maybe_r in to_phonemes:
                best_phonemes = [Phoneme(maybe_r)]
                best_dist = 0.0
                break

    if best_phonemes:
        if return_distance:
            return best_phonemes, best_dist

        return best_phonemes

    # Search through target phonemes
    for to_phoneme in to_phonemes:
        if from_phoneme.text == to_phoneme.text:
            # Easy case: exact match
            best_phonemes = [to_phoneme]
            best_dist = 0.0
            break

        if from_phoneme.letters == to_phoneme.letters:
            # Match except for elongation, accent
            if from_codepoints is None:
                from_codepoints = set(unicodedata.normalize("NFD", from_phoneme.text))

            # Compute a "distance" based on how many codepoints different between the two phonemes.
            # This should usually be < 1 so that it can be a better match than the vowel/consonant distances.
            to_codepoints = set(unicodedata.normalize("NFD", to_phoneme.text))

            # Divide by 10 to ensure this is usually < 1
            dist = abs(len(from_codepoints) - len(to_codepoints)) / 10.0

            if (best_dist is None) or (dist < best_dist):
                best_phonemes = [to_phoneme]
                best_dist = dist

            continue

        if from_phoneme.vowel and to_phoneme.vowel:
            # Vowel distance
            dist = vowel_distance(from_phoneme.vowel, to_phoneme.vowel)

            # Extra penalty for not matching elongation
            dist += 0.5 if from_phoneme.elongated != to_phoneme.elongated else 0

            if (best_dist is None) or (dist < best_dist):
                best_dist = dist
                best_phonemes = [to_phoneme]
                continue

        if from_phoneme.consonant and to_phoneme.consonant:
            # Consonant distance
            dist = consonant_distance(from_phoneme.consonant, to_phoneme.consonant)
            # Extra penalty for not matching elongation
            dist += 0.5 if from_phoneme.elongated != to_phoneme.elongated else 0

            if (best_dist is None) or (dist < best_dist):
                best_dist = dist
                best_phonemes = [to_phoneme]
                continue

        if len(from_phoneme.letters) > 1:
            # Split apart and match each letter separately
            best_split = []
            split_phonemes = Pronunciation.from_string(
                from_phoneme.text, keep_ties=False
            )
            dist = 1.0

            for split_phoneme in split_phonemes:
                guessed_split, dist_split = typing.cast(
                    PHONEMES_AND_DISTANCE,
                    guess_phonemes(
                        split_phoneme.text, to_phonemes, return_distance=True
                    ),
                )

                assert dist_split is not None
                dist += dist_split
                best_split.extend(guessed_split)

            if (best_dist is None) or (dist < best_dist):
                best_phonemes = best_split
                best_dist = dist
                continue

    if return_distance:
        return best_phonemes, best_dist

    return best_phonemes


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
