#!/usr/bin/env python3
"""Functions for comparing phonemes by a distance metric"""
import gzip
import itertools
import json
import sys
import threading
import typing

import numpy as np

from gruut_ipa.constants import (
    _CONSONANTS,
    _DATA_DIR,
    _SCHWAS,
    _VOWELS,
    FEATURE_KEYS,
    Consonant,
    Schwa,
    Vowel,
)
from gruut_ipa.features import to_vector

_CLOSEST_TYPE = typing.Mapping[str, typing.Sequence[str]]
_CLOSEST: typing.Optional[_CLOSEST_TYPE] = None


def create_closest(
    symbols: typing.Optional[
        typing.Iterable[typing.Union[Vowel, Consonant, Schwa]]
    ] = None
) -> _CLOSEST_TYPE:
    """Create mapping from each IPA symbol to a list of other IPA symbols reverse ordered by feature distance"""
    import sklearn.metrics

    if not symbols:
        symbols = itertools.chain(_VOWELS, _CONSONANTS, _SCHWAS,)

    symbol_list = list(symbols)
    vectors = {}
    for symbol in symbol_list:
        if symbol.ipa in vectors:
            continue

        vectors[symbol.ipa] = to_vector(symbol)

    matrix = np.vstack(list(vectors.values()))

    w = np.ones(matrix.shape[1])

    # Adjust feature weights
    w[FEATURE_KEYS["vowel_place"]] = 0.5
    w[FEATURE_KEYS["vowel_height"]] = 1
    w[FEATURE_KEYS["vowel_rounded"]] = 0.01

    w[FEATURE_KEYS["consonant_place"]] = 0.15
    w[FEATURE_KEYS["consonant_voiced"]] = 0.5
    w[FEATURE_KEYS["consonant_sounds_like"]] = 0.5

    dist = sklearn.metrics.pairwise_distances(matrix, metric="minkowski", p=2, w=w)

    dist_symbols = list(vectors.keys())
    closest = {
        s: [dist_symbols[j] for j in dist[i].argsort() if s != dist_symbols[j]]
        for i, s in enumerate(dist_symbols)
    }

    return closest


_CLOSEST_LOCK = threading.Lock()


def get_closest(ipa: str) -> typing.Optional[typing.Sequence[str]]:
    """Get a list of IPA symbols that are closest, ordered by increasing distance."""
    global _CLOSEST

    with _CLOSEST_LOCK:
        if _CLOSEST is None:
            closest_path = _DATA_DIR / "phoneme_distances.json.gz"
            with gzip.open(closest_path, "r") as closest_file:
                _CLOSEST = json.load(closest_file)

    assert _CLOSEST is not None

    return _CLOSEST.get(ipa)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # {
    #   "<symbol>": ["<closest symbol>", "<next closest symbol>", ...],
    #   ...
    # }
    json.dump(create_closest(), sys.stdout, indent=4, ensure_ascii=False)
