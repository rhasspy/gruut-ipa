"""Mapping between IPA and Sampa"""
import re
import unicodedata

# http://www.blahedo.org/ascii-ipa.html


def ipa_to_sampa(ipa: str) -> str:
    """Convert IPA string to sampa phonemes"""
    ipa_codepoints = unicodedata.normalize("NFD", ipa)

    return IPA_PATTERN.sub(
        lambda match: IPA_TO_SAMPA.get(match.group(1), ""), ipa_codepoints
    )


def sampa_to_ipa(sampa: str) -> str:
    """Convert sampa phonemes to IPA phones"""
    sampa_codepoints = unicodedata.normalize("NFD", sampa)

    return SAMPA_PATTERN.sub(
        lambda match: SAMPA_TO_IPA.get(match.group(1), ""), sampa_codepoints
    )


# -----------------------------------------------------------------------------

IPA_TO_SAMPA = {
    "\u0061": "a",
    "\u0250": "6",
    "\u0251": "A",
    "\u0252": "Q",
    "\u00e6": "{",
    "\u028c": "V",
    "\u0062": "b",
    "\u0253": "",
    "\u0299": "B\\",
    "\u03b2": "B",
    "\u0063": "c",
    "\u00e7": "C",
    "\u0063\u0327": "C",
    "\u0255": "s\\",
    "\u0064": "d",
    "\u0257": "",
    "\u0256": "d`",
    "\u00f0": "D",
    "\u0065": "e",
    "\u0259": "@",
    "\u025a": "@`",
    "\u0258": "@\\",
    "\u025b": "E",
    "\u025c": "3",
    "\u025d": "@`",
    "\u025e": "3\\",
    "\u0066": "f",
    "\u0261": "g",
    "\u0067": "g",
    "\u0260": "",
    "\u0262": "G\\",
    "\u029b": "G\\_<",
    "\u0263": "G",
    "\u02e0": "_G",
    "\u0264": "7",
    "\u0068": "h",
    "\u02b0": "_h",
    "\u0127": "X\\",
    "\u0266": "h\\",
    "\u0267": "x\\",
    "\u0265": "H",
    "\u029c": "H\\",
    "\u0069": "i",
    "\u0268": "1",
    "\u026a": "I",
    "\u006a": "j",
    "\u02b2": "', _j",
    "\u029d": "j\\",
    "\u025f": "J\\",
    "\u0284": "J\\_<",
    "\u006b": "k",
    "\u006c": "l",
    "\u026b": "5",
    "\u026c": "K",
    "\u026d": "l`",
    "\u026e": "K\\",
    "\u029f": "L\\",
    "\u006d": "m",
    "\u0271": "F",
    "\u026f": "M",
    "\u0270": "M\\",
    "\u006e": "n",
    "\u0272": "J",
    "\u014b": "N",
    "\u0273": "n`",
    "\u0274": "N\\",
    "\u006f": "o",
    "\u0298": "O\\",
    "\u0275": "8",
    "\u00f8": "2",
    "\u0153": "9",
    "\u0276": "&",
    "\u0254": "O",
    "\u0070": "p",
    "\u0278": "p\\",
    "\u0071": "q",
    "\u0072": "r",
    "\u027e": "4",
    "\u027c": "",
    "\u027d": "r`",
    "\u0279": "r\\",
    "\u027b": "r\\`",
    "\u027a": "l\\",
    "\u0280": "R\\",
    "\u0281": "R",
    "\u0073": "s",
    "\u0282": "s`",
    "\u0283": "S",
    "\u0074": "t",
    "\u0288": "t`",
    "\u03b8": "T",
    "\u0075": "u",
    "\u0289": "}",
    "\u028a": "U",
    "\u0076": "v",
    "\u028b": "v\\",
    "\u0077": "w",
    "\u02b7": "_w",
    "\u028d": "W",
    "\u0078": "x",
    "\u03c7": "X",
    "\u0079": "y",
    "\u028e": "L",
    "\u028f": "Y",
    "\u007a": "z",
    "\u0291": "z\\",
    "\u0290": "z`",
    "\u0292": "Z",
    "\u0294": "?",
    "\u02a1": ">\\",
    "\u0295": "?\\",
    "\u02a2": "<\\",
    "\u02e4": "_?\\",
    "\u01c3": "!\\",
    "\u01c0": "|\\",
    "\u01c1": "|\\|\\",
    "\u0320": "_-",
    "\u032a": "_d",
    "\u033a": "_a",
    "\u031f": "_+",
    "\u031d": "_r",
    "\u031e": "_o",
    "\u02c8": '"',
    "\u02cc": "%",
    "\u031a": "_}",
    "\u002e": "",
    "\u02d1": ":\\",
    "\u0308": '_"',
    "\u0324": "_t",
    "\u02d0": ":",
    "\u02bc": "",
    "\u0325": "_0",
    "\u030a": "",
    "\u031c": "_c",
    "\u0339": "_O",
    "\u0303": "~, _~",
    "\u0334": "_e",
    "\u0330": "_k",
    "\u032c": "_v",
    "\u0306": "_X",
    "\u032f": "_^",
    "\u033d": "",
    "\u02de": "`",
    "\u033b": "_m",
    "\u0318": "_A",
    "\u0319": "_q",
    "\u033c": "_N",
    "\u2197": "<R>",
    "\u2191": "^",
    "\u2198": "",
    "\u2193": "!",
    "\u030f": "_B",
    "\u0300": "_L",
    "\u0304": "_M",
    "\u0301": "_H",
    "\u030b": "_T",
    #
    # Ties
    "\u0361": "",
    "\u035C": "",
    #
    # Tied symbols
    "\u0288\u0361\u0282": "ts`",
    "\u0256\u0361\u0290": "dz`",
    "\u006b\u0361\u0078": "k_x",
    #
    # Breaks
    "|": "",
    "\u2016": "",
    "#": "",
}

SAMPA_TO_IPA = {v: k for k, v in IPA_TO_SAMPA.items() if v}

# Regex disjunctions in descending length order
SAMPA_PATTERN = re.compile(
    "({})".format(
        "|".join(
            re.escape(sampa) for sampa in sorted(SAMPA_TO_IPA, key=len, reverse=True)
        )
    )
)

IPA_PATTERN = re.compile(
    "({})".format(
        "|".join(re.escape(ipa) for ipa in sorted(IPA_TO_SAMPA, key=len, reverse=True))
    )
)
