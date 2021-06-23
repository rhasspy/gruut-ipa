"""Mapping between IPA and Espeak"""
import re
import unicodedata

# http://espeak.sourceforge.net/phonemes.html


def ipa_to_espeak(ipa: str, keep_whitespace: bool = True) -> str:
    """Convert IPA string to eSpeak phonemes"""
    ipa_codepoints = unicodedata.normalize("NFD", ipa)

    return IPA_PATTERN.sub(
        lambda match: IPA_TO_ESPEAK.get(match.group(1), ""), ipa_codepoints
    )


def espeak_to_ipa(espeak: str) -> str:
    """Convert eSpeak phonemes to IPA phones"""
    # Remove brackets
    espeak_codepoints = "".join(
        c for c in unicodedata.normalize("NFD", espeak) if c not in {"[", "]"}
    )

    return ESPEAK_PATTERN.sub(
        lambda match: ESPEAK_TO_IPA.get(match.group(1), ""), espeak_codepoints
    )


# -----------------------------------------------------------------------------

IPA_TO_ESPEAK = {
    "\u00e6": "a",
    "\u0061": "a",
    "\u0251": "A",
    "\u0252": "A.",
    "\u028c": "V",
    "\u0250": "V",
    "\u0062": "b",
    "\u0253": "b`",
    "\u0299": "b<trl>",
    "\u03b2": "B",
    "\u0063": "c",
    "\u00e7": "C",
    "\u0063\u0327": "C",
    "\u0255": "S;",
    "\u0064": "d",
    "\u0257": "d`",
    "\u0256": "d.",
    "\u00f0": "D",
    "\u0065": "e",
    "\u0259": "@",
    "\u025a": "3",
    "\u0258": "@",
    "\u025b": "E",
    "\u025c": 'V"',
    "\u025d": "3",
    "\u025e": 'O"',
    "\u0066": "f",
    "\u0261": "g",
    "\u0067": "g",
    "\u0260": "g`",
    "\u0262": "G",
    "\u029b": "G`",
    "\u0263": "Q",
    "\u02e0": "~",
    "\u0264": "o-",
    "\u0068": "h",
    "\u02b0": "<h>",
    "\u0127": "H",
    "\u0266": "h<?>",
    "\u0267": "",
    "\u0265": "j<rnd>",
    "\u029c": "",
    "\u0069": "i",
    "\u0268": 'i"',
    "\u026a": "I",
    "\u006a": "j",
    "\u02b2": ";",
    "\u029d": "C<vcd>",
    "\u025f": "J",
    "\u0284": "J`",
    "\u006b": "k",
    "\u006c": "l",
    "\u026b": "l",
    "\u026c": "s<lat>",
    "\u026d": "l.",
    "\u026e": "z<lat>",
    "\u029f": "L",
    "\u006d": "m",
    "\u0271": "M",
    "\u026f": "u-",
    "\u0270": "Q",
    "\u006e": "n",
    "\u0272": "n^",
    "\u014b": "N",
    "\u0273": "n.",
    "\u0274": 'n"',
    "\u006f": "o",
    "\u0298": "p!",
    "\u0275": "@.",
    "\u00f8": "Y",
    "\u0153": "W",
    "\u0276": "W",
    "\u0254": "O",
    "\u0070": "p",
    "\u0278": "F",
    "\u0071": "q",
    "\u0072": "r<trl>",
    "\u027e": "R",
    "\u027c": "",
    "\u027d": "*.",
    "\u0279": "r",
    "\u027b": "r.",
    "\u027a": "*<lat>",
    "\u0280": 'r"',
    "\u0281": "r",
    "\u0073": "s",
    "\u0282": "s.",
    "\u0283": "S",
    "\u0074": "t",
    "\u0288": "t.",
    "\u03b8": "T",
    "\u0075": "u",
    "\u0289": 'u"',
    "\u028a": "U",
    "\u0076": "v",
    "\u028b": "v#",
    "\u0077": "w",
    "\u02b7": "<w>",
    "\u028d": "w<vls>",
    "\u0078": "x",
    "\u03c7": "X",
    "\u0079": "y",
    "\u028e": "l^",
    "\u028f": "I.",
    "\u007a": "z",
    "\u0291": "Z;",
    "\u0290": "z.",
    "\u0292": "Z",
    "\u0294": "?",
    "\u02a1": "",
    "\u0295": "H<vcd>",
    "\u02a2": "",
    "\u02e4": "<H>",
    "\u01c3": "c!",
    "\u01c0": "t!",
    "\u01c2": "c!",
    "\u01c1": "l!",
    "\u0320": "",
    "\u032a": "",
    "\u033a": "",
    "\u031f": "",
    "\u031d": "",
    "\u031e": "",
    "\u02c8": "'",
    "\u02cc": ",",
    "\u0329": "-",
    "\u031a": "<o>",
    "\u002e": "",
    "\u02d1": "",
    "\u0308": "",
    "\u0324": "<?>",
    "\u02d0": ":",
    "\u02bc": "`",
    "\u0325": "<o>",
    "\u030a": "",
    "\u031c": "",
    "\u0339": "",
    "\u0303": "~",
    "\u0334": "~",
    "\u0330": "",
    "\u032c": "",
    "\u0306": "",
    "\u032f": "",
    "\u033d": "",
    "\u02de": "<r>",
    "\u033b": "",
    "\u0318": "",
    "\u0319": "",
    "\u033c": "",
    "\u2197": "",
    "\u2191": "",
    "\u2198": "",
    "\u2193": "",
    #
    # Ties
    "\u0361": "",
    "\u035C": "",
    #
    # Tied symbols
    "\u0288\u0361\u0282": "tS",
    "\u0256\u0361\u0290": "dz",
    #
    # Breaks
    "|": "_::",
    "\u2016": "_::_::",
    "#": "",
}

ESPEAK_TO_IPA = {v: k for k, v in IPA_TO_ESPEAK.items() if v}

# Regex disjunction in descending length order
ESPEAK_PATTERN = re.compile(
    "({})".format(
        "|".join(re.escape(espeak) for espeak in sorted(ESPEAK_TO_IPA, reverse=True))
    )
)

IPA_PATTERN = re.compile(
    "({})".format(
        "|".join(re.escape(ipa) for ipa in sorted(IPA_TO_ESPEAK, key=len, reverse=True))
    )
)
