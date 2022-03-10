#!/usr/bin/env python3
"""Utility methods"""

from gruut_ipa.constants import LANG_ALIASES


def resolve_lang(lang: str) -> str:
    """Resolve language with known aliases"""
    if "/" in lang:
        lang, rest = lang.split("/", maxsplit=1)
        lang = LANG_ALIASES.get(lang, lang)
        return f"{lang}/{rest}"

    return LANG_ALIASES.get(lang, lang)
