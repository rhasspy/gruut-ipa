#!/usr/bin/env python3
"""Functions for converting IPA symbols to and from feature vectors."""
import dataclasses
import typing

from gruut_ipa.constants import (
    CONSONANTS,
    FEATURE_COLUMNS,
    FEATURE_EMPTY,
    FEATURE_KEYS,
    FEATURE_ORDINAL_COLUMNS,
    IPA,
    SCHWAS,
    VOWELS,
    Break,
    BreakType,
    Consonant,
    ConsonantPlace,
    ConsonantType,
    PhonemeLength,
    Schwa,
    Stress,
    Vowel,
    VowelHeight,
    VowelPlacement,
)


def to_vector(
    symbol: typing.Union[Vowel, Consonant, Schwa, Break]
) -> typing.Sequence[float]:
    """Converts a symbol into a feature vector"""
    features: typing.Dict[str, str] = {}

    if isinstance(symbol, Vowel):
        features["symbol_type"] = "phoneme"
        features["phoneme_type"] = "vowel"
        features["vowel_height"] = symbol.height.value
        features["vowel_place"] = symbol.placement.value
        features["vowel_rounded"] = "rounded" if symbol.rounded else "unrounded"
        features["phoneme_length"] = symbol.length.value

        if symbol.nasalated:
            features["diacritic"] = "nasalated"

        if symbol.stress is not None:
            features["vowel_stress"] = symbol.stress.value

    elif isinstance(symbol, Consonant):
        features["symbol_type"] = "phoneme"
        features["phoneme_type"] = "consonant"
        features["consonant_voiced"] = "voiced" if symbol.voiced else "unvoiced"
        features["consonant_type"] = symbol.type.value
        features["consonant_place"] = symbol.place.value
        features["consonant_sounds_like"] = symbol.sounds_like.value
        features["phoneme_length"] = symbol.length.value

        if symbol.velarized:
            features["diacritic"] = "velarized"

    elif isinstance(symbol, Schwa):
        features["symbol_type"] = "phoneme"
        features["phoneme_type"] = "schwa"
        features["phoneme_length"] = symbol.length.value

        if symbol.r_coloured:
            features["consonant_sounds_like"] = "r"

    elif isinstance(symbol, Break):
        features["symbol_type"] = "break"
        features["break_type"] = symbol.type.value
    else:
        # Unsupported symbol type
        raise ValueError(symbol)

    return features_to_vector(features)


def from_vector(
    vector: typing.Sequence[float],
) -> typing.Union[Vowel, Consonant, Schwa, Break]:
    """Converts a feature vector back into a symbol"""
    features = vector_to_features(vector)
    if features["symbol_type"] == "break":
        break_type = BreakType(features["break_type"])
        return Break(break_type)

    if features["symbol_type"] == "phoneme":
        if features["phoneme_type"] == "vowel":
            height = VowelHeight(features["vowel_height"])
            placement = VowelPlacement(features["vowel_place"])
            rounded = features["vowel_rounded"] == "rounded"
            nasalated = features["diacritic"] == "nasalated"
            length = PhonemeLength(features["phoneme_length"])

            stress: typing.Optional[Stress] = None
            stress_val = features["vowel_stress"]
            if stress_val != FEATURE_EMPTY:
                stress = Stress(stress_val)

            for vowel in VOWELS.values():
                if (
                    (vowel.height == height)
                    and (vowel.placement == placement)
                    and (vowel.rounded == rounded)
                    and (vowel.nasalated == nasalated)
                ):
                    if (stress is None) and (length == PhonemeLength.NORMAL):
                        # Don't need to make a copy
                        return vowel

                    return dataclasses.replace(vowel, stress=stress)

            raise ValueError(f"Unknown vowel: {features}")

        if features["phoneme_type"] == "consonant":
            c_type = ConsonantType(features["consonant_type"])
            place = ConsonantPlace(features["consonant_place"])
            voiced = features["consonant_voiced"] == "voiced"
            velarized = features["diacritic"] == "velarized"
            length = PhonemeLength(features["phoneme_length"])

            for consonant in CONSONANTS.values():
                if (
                    (consonant.type == c_type)
                    and (consonant.place == place)
                    and (consonant.voiced == voiced)
                    and (consonant.velarized == velarized)
                ):
                    if length == PhonemeLength.NORMAL:
                        # Don't need to make a copy
                        return consonant

                    return dataclasses.replace(consonant, length=length)

            raise ValueError(f"Unknown vowel: {features}")

        if features["phoneme_type"] == "schwa":
            r_coloured = features["consonant_sounds_like"] == "r"
            length = PhonemeLength(features["phoneme_length"])

            for schwa in SCHWAS.values():
                if schwa.r_coloured == r_coloured:
                    if length == PhonemeLength.NORMAL:
                        # Don't need to make a copy
                        return schwa

                    return dataclasses.replace(schwa, length=length)

            raise ValueError(f"Unknown vowel: {features}")

        # Unsupported phoneme type
        raise ValueError(f"Unknown phoneme type: {features}")

    # Unsupported symbol type
    raise ValueError(f"Unknown symbol type: {features}")


def string_to_symbol(symbol_str: str) -> typing.Union[Vowel, Consonant, Schwa, Break]:
    """Get gruut IPA object for IPA symbol"""
    if not symbol_str:
        raise ValueError("Empty symbol")

    # Check break first
    if symbol_str == IPA.BREAK_WORD:
        return Break(BreakType.WORD)

    if symbol_str == IPA.BREAK_MINOR:
        return Break(BreakType.MINOR)

    if symbol_str == IPA.BREAK_MAJOR:
        return Break(BreakType.MAJOR)

    # Strip stress
    maybe_stress: typing.Optional[Stress] = None
    if symbol_str[0] == IPA.STRESS_PRIMARY:
        maybe_stress = Stress.PRIMARY
        symbol_str = symbol_str[1:]
    elif symbol_str[0] == IPA.STRESS_SECONDARY:
        maybe_stress = Stress.SECONDARY
        symbol_str = symbol_str[1:]

    if not symbol_str:
        raise ValueError("No letters")

    # Strip length
    length = PhonemeLength.NORMAL
    if symbol_str[-1] == IPA.HALF_LONG:
        length = PhonemeLength.SHORT
        symbol_str = symbol_str[:-1]
    elif symbol_str[-1] == IPA.LONG:
        length = PhonemeLength.LONG
        symbol_str = symbol_str[:-1]

    if not symbol_str:
        raise ValueError("No letters")

    # Look up
    maybe_vowel = VOWELS.get(symbol_str)
    if maybe_vowel is not None:
        return dataclasses.replace(maybe_vowel, stress=maybe_stress, length=length)

    maybe_consonant = CONSONANTS.get(symbol_str)
    if maybe_consonant is not None:
        return dataclasses.replace(maybe_consonant, length=length)

    maybe_schwa = SCHWAS.get(symbol_str)
    if maybe_schwa is not None:
        return dataclasses.replace(maybe_schwa, length=length)

    raise ValueError(f"Unsupported symbol type: {symbol_str}")


def features_to_vector(features: typing.Mapping[str, str]) -> typing.Sequence[float]:
    """Create phoneme feature vector from mapping"""
    vector: typing.List[float] = []

    for col, values in FEATURE_COLUMNS.items():
        value = features.get(col, FEATURE_EMPTY)

        if col in FEATURE_ORDINAL_COLUMNS:
            # Single value normalized by number of possible values
            vector.append(values.index(value) / len(values))
        else:
            # One-hot vector
            for v in values:
                vector.append(1.0 if (v == value) else 0.0)

    return vector


def vector_to_features(vector: typing.Sequence[float]) -> typing.Mapping[str, str]:
    """Create mapping from phoneme feature vector"""
    features: typing.Dict[str, str] = {}

    for col_name, values in FEATURE_COLUMNS.items():
        col_key = FEATURE_KEYS[col_name]
        if col_name in FEATURE_ORDINAL_COLUMNS:
            # Single value normalized by number of possible values
            assert isinstance(col_key, int)
            val_idx = int(vector[col_key] * len(values))
        else:
            # One-hot vector
            assert isinstance(col_key, slice)
            if 1.0 not in vector[col_key]:
                assert False, (col_name, col_key, vector[col_key])
            val_idx = vector[col_key].index(1.0)

        features[col_name] = values[val_idx]

    return features
