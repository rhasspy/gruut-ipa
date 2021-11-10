#!/usr/bin/env python3
import itertools
import json
import sys

import gruut_ipa
from gruut_ipa.constants import (
    IPA,
    VowelHeight,
    VowelPlacement,
    ConsonantType,
    ConsonantPlace,
    BreakType,
    Stress,
)

import numpy as np
import sklearn.metrics
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder


def main():
    """Main entry point"""

    feature_cols = {
        "symbol_type": ["phoneme", "break"],
        "phoneme_type": ["NONE", "vowel", "consonant", "schwa"],
        "diacritic": ["NONE", "nasalated", "velarized"],
        "vowel_height": ["NONE"] + [v.value for v in VowelHeight],
        "vowel_place": ["NONE"] + [v.value for v in VowelPlacement],
        "vowel_rounded": ["NONE", "rounded", "unrounded"],
        "consonant_voiced": ["NONE", "voiced", "unvoiced"],
        "consonant_type": ["NONE"] + [v.value for v in ConsonantType],
        "consonant_place": ["NONE"] + [v.value for v in ConsonantPlace],
        "consonant_sounds_like": ["NONE", "r", "l", "g", ""],
        "break_type": ["NONE"] + [v.value for v in BreakType],
        "stress": ["NONE"] + [v.value for v in Stress],
    }

    ordinal_cols = {
        "vowel_height": VowelHeight,
        "vowel_place": VowelPlacement,
        "consonant_type": ConsonantType,
        "consonant_place": ConsonantPlace,
        "break_type": BreakType,
        "stress": Stress,
    }

    feature_keys = {}
    offset = 0
    for feature_col, feature_values in feature_cols.items():
        if feature_col in ordinal_cols:
            continue

        feature_keys[feature_col] = slice(offset, offset + len(feature_values))
        offset += len(feature_values)

    for feature_col in ordinal_cols:
        feature_keys[feature_col] = offset
        offset += 1

    ordinal_enc = OrdinalEncoder(categories=[feature_cols[col] for col in ordinal_cols])
    onehot_enc = OneHotEncoder(
        categories=[
            feature_cols[col] for col in feature_cols if col not in ordinal_cols
        ]
    )

    symbol_features = {}

    for break_symbol, break_type in [
        (IPA.BREAK_WORD, BreakType.WORD),
        (IPA.BREAK_MINOR, BreakType.MINOR),
        (IPA.BREAK_MAJOR, BreakType.MAJOR),
    ]:
        features = {"symbol_type": "break", "break_type": str(break_type.value)}
        symbol_features[break_symbol] = features

    for s in itertools.chain(gruut_ipa.VOWELS, gruut_ipa.CONSONANTS, gruut_ipa.SCHWAS):
        if s in symbol_features:
            continue

        p = gruut_ipa.Phoneme(s)
        features = {"symbol_type": "phoneme"}

        if p.vowel:
            features["phoneme_type"] = "vowel"
            features["vowel_height"] = p.vowel.height.value
            features["vowel_place"] = p.vowel.placement.value
            features["vowel_rounded"] = "rounded" if p.vowel.rounded else "unrounded"

            if p.nasalated:
                features["diacritic"] = "nasalated"
        elif p.consonant:
            features["phoneme_type"] = "consonant"
            features["consonant_voiced"] = (
                "voiced" if p.consonant.voiced else "unvoiced"
            )
            features["consonant_type"] = p.consonant.type.value
            features["consonant_place"] = p.consonant.place.value
            features["consonant_sounds_like"] = p.consonant.sounds_like.value

            if p.consonant.velarized:
                features["diacritic"] = "velarized"
        elif p.schwa:
            features["phoneme_type"] = "schwa"
            if p.schwa.r_coloured:
                features["consonant_sounds_like"] = "r"

        symbol_features[s] = features

    vectors = {}
    for s, features in symbol_features.items():
        onehot_features = []
        ordinal_features = []

        assert "symbol_type" in feature_cols

        for col in feature_cols:
            if col not in features:
                features[col] = "NONE"

            if col in ordinal_cols:
                ordinal_features.append(features[col])
            else:
                onehot_features.append(features[col])

        onehot_vector = onehot_enc.fit_transform([onehot_features]).toarray()[0]
        ordinal_vector = ordinal_enc.fit_transform([ordinal_features])[0]

        for col_i, (_col_name, col_val) in enumerate(ordinal_cols.items()):
            ordinal_vector[col_i] /= len(col_val)

        vectors[s] = np.hstack((onehot_vector, ordinal_vector))

    matrix = np.vstack(list(vectors.values()))

    w = np.ones(matrix.shape[1])
    w[feature_keys["vowel_place"]] = 0.5
    w[feature_keys["vowel_rounded"]] = 0.5
    w[feature_keys["consonant_place"]] = 0.05
    w[feature_keys["consonant_sounds_like"]] = 0.5

    dist = sklearn.metrics.pairwise_distances(matrix, metric="minkowski", p=2, w=w)

    symbols = list(vectors.keys())

    json.dump(
        {
            "symbols": symbols,
            "columns": list(feature_cols.items()),
            "features": matrix.tolist(),
            "closest": {
                s: list(symbols[j] for j in dist[i].argsort())[1:]
                for i, s in enumerate(symbols)
            },
            "distances": dist.tolist(),
        },
        sys.stdout,
        indent=4,
        ensure_ascii=False,
    )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
