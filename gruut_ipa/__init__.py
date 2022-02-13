"""Classes for dealing with phones and phonemes"""
import dataclasses
import logging
import re
import typing
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

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
    BreakType,
    Consonant,
    ConsonantPlace,
    ConsonantType,
    Dipthong,
    Schwa,
    Stress,
    Vowel,
    VowelHeight,
    VowelPlacement,
    features_to_vector,
    vector_to_features,
    PhonemeLength,
)
from gruut_ipa.espeak import espeak_to_ipa, ipa_to_espeak  # noqa: F401
from gruut_ipa.sampa import ipa_to_sampa, sampa_to_ipa  # noqa: F401

# -----------------------------------------------------------------------------

_LOGGER = logging.getLogger("gruut_ipa")

_DIR = Path(__file__).parent

_DATA_DIR = _DIR / "data"

# -----------------------------------------------------------------------------


class Phone:
    """Single IPA phone with diacritics and suprasegmentals"""

    def __init__(
        self,
        letters: str,
        stress: typing.Optional[Stress] = None,
        accents: typing.Optional[typing.Iterable[Accent]] = None,
        is_long: bool = False,
        nasal: typing.Optional[typing.Set[int]] = None,
        raised: typing.Optional[typing.Set[int]] = None,
        diacritics: typing.Optional[typing.Dict[int, typing.Set[str]]] = None,
        suprasegmentals: typing.Optional[typing.Set[str]] = None,
        tone: str = "",
    ):
        self.letters: str = unicodedata.normalize("NFC", letters)
        self.stress = stress
        self.accents: typing.List[Accent] = list(accents or [])
        self.is_long: bool = is_long

        self.nasal: typing.Set[int] = nasal or set()
        self.is_nasal = bool(self.nasal)

        self.raised: typing.Set[int] = raised or set()
        self.is_raised = bool(self.raised)

        self.tone: str = tone

        self.diacritics: typing.Dict[int, typing.Set[str]] = diacritics or defaultdict(
            set
        )
        self.suprasegmentals: typing.Set[str] = suprasegmentals or set()

        # Decompose suprasegmentals and diacritics
        if self.stress == Stress.PRIMARY:
            self.suprasegmentals.add(IPA.STRESS_PRIMARY)
        elif self.stress == Stress.SECONDARY:
            self.suprasegmentals.add(IPA.STRESS_SECONDARY)

        if Accent.ACUTE in self.accents:
            self.suprasegmentals.add(IPA.ACCENT_ACUTE)

        if Accent.GRAVE in self.accents:
            self.suprasegmentals.add(IPA.ACCENT_GRAVE)

        if self.is_long:
            self.suprasegmentals.add(IPA.LONG)

        # Nasal
        for letter_index in self.nasal:
            letter_diacritics = self.diacritics.get(letter_index)
            if letter_diacritics is None:
                letter_diacritics = set()
                self.diacritics[letter_index] = letter_diacritics

            letter_diacritics.add(IPA.NASAL)

        # Raised
        for letter_index in self.raised:
            letter_diacritics = self.diacritics.get(letter_index)
            if letter_diacritics is None:
                letter_diacritics = set()
                self.diacritics[letter_index] = letter_diacritics

            letter_diacritics.add(IPA.RAISED)

        self._text: str = ""

        self.vowel: typing.Optional[Vowel] = VOWELS.get(self.letters)
        self.consonant: typing.Optional[Consonant] = CONSONANTS.get(self.letters)
        self.schwa: typing.Optional[Schwa] = SCHWAS.get(self.letters)

    @property
    def text(self) -> str:
        """Get textual representation of phone (NFC normalized)"""
        if self._text:
            return self._text

        # Pre-letter suprasegmentals
        for accent in self.accents:
            if accent == Accent.ACUTE:
                self._text += IPA.ACCENT_ACUTE
            elif accent == Accent.GRAVE:
                self._text += IPA.ACCENT_GRAVE

        if self.stress == Stress.PRIMARY:
            self._text += IPA.STRESS_PRIMARY
        elif self.stress == Stress.SECONDARY:
            self._text += IPA.STRESS_SECONDARY

        # Letters and diacritics
        for letter_index, letter in enumerate(self.letters):
            self._text += letter

            # Diacritics
            for diacritic in self.diacritics.get(letter_index, []):
                self._text += diacritic

        # Tone
        if self.tone:
            self._text += self.tone

        # Post-letter suprasegmentals
        if self.is_long:
            self._text += IPA.LONG

        # Re-normalize and combine
        self._text = unicodedata.normalize("NFC", self._text)

        return self._text

    @property
    def is_vowel(self) -> bool:
        """True if phone is a vowel"""
        return self.vowel is not None

    @property
    def is_consonant(self) -> bool:
        """True if phone is a consonant"""
        return self.consonant is not None

    @property
    def is_schwa(self) -> bool:
        """True if phone is a schwa"""
        return self.schwa is not None

    def __repr__(self) -> str:
        return self.text

    def __eq__(self, other):
        return isinstance(other, Phone) and self.text == other.text

    def __hash__(self):
        return hash(self.text)

    @staticmethod
    def from_string(phone_str: str) -> "Phone":
        """Parse phone from string"""
        # Decompose into base and combining characters
        codepoints = unicodedata.normalize("NFD", phone_str)
        kwargs: typing.Dict[str, typing.Any] = {
            "letters": "",
            "diacritics": defaultdict(set),
            "tone": "",
            "accents": [],
            "nasal": set(),
            "raised": set(),
        }

        in_tone = False
        new_letter = False
        letter_index = 0

        for c in codepoints:
            # Check for stress
            if (c == IPA.ACCENT_ACUTE) and not in_tone:
                kwargs["accents"].append(Accent.ACUTE)
            elif (c == IPA.ACCENT_GRAVE) and not in_tone:
                kwargs["accents"].append(Accent.GRAVE)
            elif c == IPA.STRESS_PRIMARY:
                kwargs["stress"] = Stress.PRIMARY
            elif c == IPA.STRESS_SECONDARY:
                kwargs["stress"] = Stress.SECONDARY
            elif in_tone and (c in {IPA.TONE_GLOTTALIZED, IPA.TONE_SHORT}):
                # Interpret as part of tone
                kwargs["tone"] += c
            elif IPA.is_long(c):
                # Check for elongation
                kwargs["is_long"] = True
            elif IPA.is_nasal(c):
                # Check for nasalation
                kwargs["nasal"].add(letter_index)
            elif IPA.is_raised(c):
                # Check for raised articulation
                kwargs["raised"].add(letter_index)
            elif IPA.is_bracket(c) or IPA.is_break(c):
                # Skip brackets/syllable breaks
                pass
            elif IPA.is_tie(c):
                # Keep ties in letters
                kwargs["letters"] += c
                letter_index += 1
            elif IPA.is_tone(c):
                # Tone numbers/letters
                kwargs["tone"] += c
                in_tone = True
            elif unicodedata.combining(c) > 0:
                # Stow some diacritics that we don't do anything with
                kwargs["diacritics"][letter_index].add(c)
            else:
                # Include all other characters in letters
                kwargs["letters"] += c
                if new_letter:
                    letter_index += 1

                new_letter = True

        return Phone(**kwargs)


@dataclass
class Break:
    """IPA break/boundary"""

    type: BreakType
    text: str = ""

    def __post_init__(self):
        if self.type == BreakType.MINOR:
            self.text = IPA.BREAK_MINOR
        elif self.type == BreakType.MAJOR:
            self.text = IPA.BREAK_MAJOR
        elif self.type == BreakType.WORD:
            self.text = IPA.BREAK_WORD
        else:
            raise ValueError(f"Unrecognized break type: {type}")

    @staticmethod
    def from_string(break_str: str) -> "Break":
        """Parse break from string"""
        if break_str == IPA.BREAK_MINOR:
            break_type = BreakType.MINOR
        elif break_str == IPA.BREAK_MAJOR:
            break_type = BreakType.MAJOR
        elif break_str == IPA.BREAK_WORD:
            break_type = BreakType.WORD
        else:
            raise ValueError(f"Unrecognized break type: {break_str}")

        return Break(break_type)


class Intonation:
    """IPA rising/falling intonation"""

    def __init__(self, rising: bool):
        self.rising = rising

        if self.rising:
            self.text = IPA.INTONATION_RISING
        else:
            self.text = IPA.INTONATION_FALLING

    def __repr__(self) -> str:
        return self.text

    @staticmethod
    def from_string(intonation_str: str) -> "Intonation":
        """Parse intonation from string"""
        if intonation_str == IPA.INTONATION_RISING:
            rising = True
        elif intonation_str == IPA.INTONATION_FALLING:
            rising = False
        else:
            raise ValueError(f"Unrecognized intonation type: {intonation_str}")

        return Intonation(rising)


# -----------------------------------------------------------------------------


class Pronunciation:
    """Collection of phones and breaks for some unit of text (word, sentence, etc.)"""

    def __init__(
        self, phones_and_others: typing.List[typing.Union[Phone, Break, Intonation]]
    ):
        self.phones_and_others = phones_and_others

        self.phones: typing.List[Phone] = []
        self.breaks: typing.List[Break] = []
        self.intonations: typing.List[Intonation] = []

        # Decompose into phones, breaks, and intonations
        for p in self.phones_and_others:
            if isinstance(p, Phone):
                self.phones.append(p)
            elif isinstance(p, Break):
                self.breaks.append(p)
            elif isinstance(p, Intonation):
                self.intonations.append(p)

        self._text = ""

    @property
    def text(self) -> str:
        """Get text representation of pronunciation (NFC normalized)"""
        if not self._text:
            self._text = "".join(p.text for p in self.phones_and_others)

        return self._text

    def __repr__(self) -> str:
        return self.text

    def __iter__(self):
        return iter(self.phones_and_others)

    def __getitem__(self, idx):
        return self.phones_and_others[idx]

    @staticmethod
    def from_string(
        pron_str: str,
        keep_stress: bool = True,
        keep_accents: typing.Optional[bool] = None,
        drop_tones: bool = False,
        keep_ties: bool = True,
    ) -> "Pronunciation":
        """Split an IPA pronunciation into phones.

        Stress/accent markers bind to the next non-combining codepoint (e.g., ˈa).
        Elongation markers bind to the previous non-combining codepoint (e.g., aː).
        Ties join two non-combining sequences (e.g. t͡ʃ).

        Whitespace and brackets are skipped.

        Returns list of phones.
        """
        if keep_accents is None:
            keep_accents = keep_stress

        clusters = []
        cluster = ""
        stress = ""
        is_stress = False
        accents = ""
        is_accent = False
        tone = ""
        in_tone = False
        skip_next_cluster = False

        codepoints = unicodedata.normalize("NFD", pron_str)

        for codepoint in codepoints:
            new_cluster = False
            is_stress = False
            is_accent = False

            if (
                codepoint.isspace()
                or IPA.is_bracket(codepoint)
                or (codepoint in {IPA.BREAK_SYLLABLE})
            ):
                # Skip whitespace, brackets, and syllable breaks
                continue

            if IPA.is_break(codepoint) or IPA.is_intonation(codepoint):
                # Keep minor/major/word breaks and intonation markers
                new_cluster = True

            if IPA.is_accent(codepoint) and not in_tone:
                is_accent = True
                if cluster:
                    new_cluster = True
                    skip_next_cluster = True
            elif IPA.is_stress(codepoint):
                is_stress = True
                if cluster:
                    new_cluster = True
                    skip_next_cluster = True
            elif in_tone and (codepoint in {IPA.TONE_GLOTTALIZED, IPA.TONE_SHORT}):
                # Interpret as part of tone
                if not drop_tones:
                    tone += codepoint

                continue
            elif IPA.is_long(codepoint):
                # Add to current cluster
                pass
            elif IPA.is_tie(codepoint):
                if keep_ties:
                    # Add next non-combining to current cluster
                    skip_next_cluster = True
                else:
                    # Ignore ties
                    continue
            elif IPA.is_tone(codepoint):
                # Add to end of current cluster
                if not drop_tones:
                    tone += codepoint

                in_tone = True
                continue
            elif unicodedata.combining(codepoint) == 0:
                # Non-combining character
                if skip_next_cluster:
                    # Add to current cluster
                    skip_next_cluster = False
                elif cluster:
                    # Start a new cluster
                    new_cluster = True

            if new_cluster and cluster:
                clusters.append(accents + stress + cluster + tone)
                accents = ""
                stress = ""
                cluster = ""
                tone = ""

            if is_accent:
                if keep_accents:
                    accents += codepoint
            elif is_stress:
                if keep_stress:
                    stress += codepoint
            else:
                cluster += codepoint

        if cluster:
            clusters.append(accents + stress + cluster + tone)

        phones_and_others: typing.List[typing.Union[Phone, Break, Intonation]] = []
        for cluster in clusters:
            if IPA.is_break(cluster):
                phones_and_others.append(Break.from_string(cluster))
            elif IPA.is_intonation(cluster):
                phones_and_others.append(Intonation.from_string(cluster))
            else:
                phones_and_others.append(Phone.from_string(cluster))

        return Pronunciation(phones_and_others)


# -----------------------------------------------------------------------------


class Phoneme:
    """Phoneme composed of international phonetic alphabet symbols"""

    def __init__(
        self,
        text: str,
        example: str = "",
        unknown: bool = False,
        tones: typing.Optional[typing.Iterable[str]] = None,
        is_ipa: bool = True,
    ):
        self._text = ""
        self._text_compare = ""
        self.example = example
        self.unknown = unknown

        # List of allowable tones for phoneme
        self.tones = list(tones or [])

        self.stress: typing.Optional[Stress] = None
        self.accents: typing.List[Accent] = []
        self.elongated: bool = False
        self.nasalated: typing.Set[int] = set()
        self.raised: typing.Set[int] = set()
        self._extra_combining: typing.Dict[int, typing.List[str]] = defaultdict(list)

        # Decompose into base and combining characters
        codepoints = unicodedata.normalize("NFD", text)
        self.letters = ""
        self.tone = ""

        if is_ipa:
            in_tone = False
            letter_index = 0
            new_letter = False

            for c in codepoints:
                # Check for stress
                if (c == IPA.ACCENT_ACUTE) and (not in_tone):
                    self.accents.append(Accent.ACUTE)
                elif (c == IPA.ACCENT_GRAVE) and (not in_tone):
                    self.accents.append(Accent.GRAVE)
                elif c == IPA.STRESS_PRIMARY:
                    self.stress = Stress.PRIMARY
                elif c == IPA.STRESS_SECONDARY:
                    self.stress = Stress.SECONDARY
                elif in_tone and (c in {IPA.TONE_GLOTTALIZED, IPA.TONE_SHORT}):
                    # Interpret as part of tone
                    self.tone += c
                elif IPA.is_long(c):
                    # Check for elongation
                    self.elongated = True
                elif IPA.is_nasal(c):
                    # Check for nasalation
                    self.nasalated.add(letter_index)
                elif IPA.is_raised(c):
                    # Check for raised articulation
                    self.raised.add(letter_index)
                elif IPA.is_bracket(c) or IPA.is_break(c):
                    # Skip brackets/syllable breaks
                    pass
                elif IPA.is_tone(c):
                    # Keep tone separate
                    self.tone += c
                    in_tone = True
                elif c in {IPA.SYLLABIC, IPA.NON_SYLLABIC, IPA.EXTRA_SHORT}:
                    # Stow some diacritics that we don't do anything with
                    self._extra_combining[letter_index].append(c)
                else:
                    # Include all other characters in base
                    self.letters += c

                    if new_letter:
                        letter_index += 1

                    new_letter = True
        else:
            self.letters = text

        # Re-normalize and combine letters
        self.letters = unicodedata.normalize("NFC", self.letters)
        self.letters_graphemes = IPA.graphemes(self.letters)

        # Categorize
        self.vowel: typing.Optional[Vowel] = VOWELS.get(self.letters)
        self.consonant: typing.Optional[Consonant] = CONSONANTS.get(self.letters)
        self.schwa: typing.Optional[Schwa] = SCHWAS.get(self.letters)
        self.dipthong: typing.Optional[Dipthong] = None

        if (
            (not self.vowel)
            and (not self.consonant)
            and (not self.schwa)
            and (len(self.letters) == 2)
        ):
            # Check if dipthong (two vowels)
            vowel1 = VOWELS.get(self.letters[0])
            vowel2 = VOWELS.get(self.letters[1])
            if vowel1 and vowel2:
                self.dipthong = Dipthong(vowel1, vowel2)

    @property
    def text(self) -> str:
        """Return letters with stress and elongation (NFC normalized)"""
        if self._text:
            return self._text

        for accent in self.accents:
            if accent == Accent.ACUTE:
                self._text += IPA.ACCENT_ACUTE
            elif accent == Accent.GRAVE:
                self._text += IPA.ACCENT_GRAVE

        if self.stress == Stress.PRIMARY:
            self._text += IPA.STRESS_PRIMARY
        elif self.stress == Stress.SECONDARY:
            self._text += IPA.STRESS_SECONDARY

        for letter_index, letter in enumerate(self.letters):
            self._text += letter

            if letter_index in self.nasalated:
                self._text += IPA.NASAL

            if letter_index in self.raised:
                self._text += IPA.RAISED

            for c in self._extra_combining[letter_index]:
                self._text += c

        if self.tone:
            self._text += self.tone

        if self.elongated:
            self._text += IPA.LONG

        # Re-normalize and combine
        self._text = unicodedata.normalize("NFC", self._text)

        return self._text

    @property
    def text_compare(self) -> str:
        """Return letters and elongation with no stress/tones (NFC normalized)"""
        if self._text_compare:
            return self._text_compare

        for letter_index, letter in enumerate(self.letters):
            self._text_compare += letter

            if letter_index in self.nasalated:
                self._text_compare += IPA.NASAL

            if letter_index in self.raised:
                self._text_compare += IPA.RAISED

            for c in self._extra_combining[letter_index]:
                self._text_compare += c

        if self.elongated:
            self._text_compare += IPA.LONG

        # Re-normalize and combine
        self._text_compare = unicodedata.normalize("NFC", self._text_compare)

        return self._text_compare

    def copy(self) -> "Phoneme":
        """Create a copy of this phonemes"""
        return Phoneme(text=self.text, example=self.example, unknown=self.unknown)

    def __repr__(self) -> str:
        """Return symbol with stress and elongation."""
        return self.text

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """Return properties of phoneme as a dict"""
        type_name = "Phoneme"
        props: typing.Dict[str, typing.Any] = {
            "text": repr(self),
            "letters": self.letters,
            "tone": self.tone,
            "tones": self.tones,
        }

        if self.unknown:
            props["unknown"] = True

        if self.example:
            props["example"] = self.example

        props["accents"] = [a.value for a in self.accents]
        props["stress"] = self.stress.value if self.stress is not None else ""

        if self.vowel:
            type_name = "Vowel"
            props["height"] = self.vowel.height.value
            props["placement"] = self.vowel.placement.value
            props["rounded"] = self.vowel.rounded
        elif self.consonant:
            type_name = "Consonant"
            props["type"] = self.consonant.type.value
            props["place"] = self.consonant.place.value
            props["voiced"] = self.consonant.voiced
        elif self.dipthong:
            type_name = "Dipthong"
        elif self.schwa:
            type_name = "Schwa"
            props["r_coloured"] = self.schwa.r_coloured

        props["type"] = type_name

        props["nasalated"] = list(self.nasalated)
        props["raised"] = list(self.raised)
        props["elongated"] = self.elongated

        return props

    def to_string(self) -> str:
        """Return descriptive string of phoneme"""
        props = self.to_dict()
        type_name = props.get("type", "Phoneme")

        prop_strs = [f"{k}={v}" for k, v in props.items()]

        return f"{type_name}(" + ", ".join(prop_strs) + ")"


# -----------------------------------------------------------------------------


class Phonemes:
    """Set of phonemes and allophones for a language"""

    COMMENT_STR = "#"

    def __init__(self, phonemes=None, ipa_map=None):
        self.phonemes = phonemes or []
        self.ipa_map = ipa_map or {}

        # Regex for replacing IPA
        self._ipa_map_regex = None

        # Phonemes sorted by descreasing length
        self._phonemes_sorted = None

        # Map from original phoneme to gruut IPA
        self.gruut_ipa_map: typing.Dict[str, str] = {}

        self.phoneme_texts: typing.Set[str] = {}
        self.update()

    def __iter__(self):
        return iter(self.phonemes)

    def __len__(self):
        return len(self.phonemes)

    def __getitem__(self, key):
        return self.phonemes[key]

    def __contains__(self, item):
        if isinstance(item, str):
            # Compare IPA text
            return item in self.phoneme_texts

        return item in self.phonemes

    @staticmethod
    def from_language(language: str) -> "Phonemes":
        """Load phonemes for a given language"""
        language = resolve_lang(language)

        # Load phonemes themselves
        phonemes_path = _DATA_DIR / language / "phonemes.txt"
        with open(phonemes_path, "r", encoding="utf-8") as phonemes_file:
            phonemes = Phonemes.from_text(phonemes_file)

        # Try to load optional map from original phoneme to gruut IPA
        gruut_ipa_map: typing.Optional[typing.Dict[str, str]] = None
        map_path = _DATA_DIR / language / "ipa_map.txt"
        if map_path.is_file():
            gruut_ipa_map = {}
            with open(map_path, "r", encoding="utf-8") as map_file:
                for line in map_file:
                    line = line.strip()
                    if not line:
                        continue

                    from_phoneme, to_ipa = line.split(maxsplit=1)
                    gruut_ipa_map[from_phoneme] = to_ipa

        if gruut_ipa_map:
            phonemes.gruut_ipa_map = gruut_ipa_map

        return phonemes

    @staticmethod
    def from_text(text_file) -> "Phonemes":
        """Load text file with phonemes, examples, and allophones"""
        lang = Phonemes()

        for line in text_file:
            # Remove comments
            line, *_ = line.split(Phonemes.COMMENT_STR, maxsplit=1)
            line = line.strip()
            if line:
                # phoneme [example] [allophone] [allophone] ! [tone] [tone]...
                parts = line.split()
                phoneme_ipa = parts[0]
                example = ""

                if len(parts) > 1:
                    example = parts[1]

                tones = []
                if len(parts) > 2:
                    in_tone = False

                    # Map allophone back to phoneme
                    for part in parts[2:]:
                        if part == "!":
                            # Begin possible tones for this phoneme
                            in_tone = True
                        elif in_tone:
                            tones.append(part)
                        else:
                            lang.ipa_map[part] = phoneme_ipa

                lang.phonemes.append(
                    Phoneme(text=phoneme_ipa, example=example, tones=tones)
                )

        lang.update()

        return lang

    def update(self):
        """Call after modifying phonemes or IPA map to re-sort"""
        # Create single regex that will be used to replace IPA.
        # The final regex is of the form (AAA|BB|C) where each case is in
        # decreasing length order.
        #
        # If the replacement is not a substring of any phonemes, then the
        # replacement is straightforward.
        #
        # If it is a substring of some phoneme, however, we need to be careful.
        # For example, naively replacing "e" with "eɪ" in the string "beɪ" will
        # produce "beeɪ" when we want it to be "beɪ".
        #
        # So the substring case becomes "e(?!ɪ)" which uses a negative lookahead
        # to avoid the problem.
        cases = []
        for match_text in sorted(self.ipa_map.keys(), key=len, reverse=True):
            if match_text.startswith(","):
                # Raw regex
                cases.append(match_text[1:])
                continue

            # Check against all of the phonemes
            case_added = False
            for phoneme in self.phonemes:
                num_extra = len(phoneme.text) - len(match_text)
                if (num_extra > 0) and phoneme.text.startswith(match_text):
                    # Use negative lookahead to avoid replacing part of a valid
                    # phoneme.
                    cases.append(
                        "{}(?!{})".format(
                            re.escape(match_text[:num_extra]),
                            re.escape(phoneme.text[num_extra:]),
                        )
                    )

                    case_added = True
                    break

            if not case_added:
                # No substring problem
                cases.append(re.escape(match_text))

        ipa_map_regex_str = "({})".format("|".join(cases))
        self._ipa_map_regex = re.compile(ipa_map_regex_str)

        # Split phonemes and sort by reverse length
        split_phonemes = [
            ([pb.text for pb in Pronunciation.from_string(p.text)], p)
            for p in self.phonemes
        ]

        self._phonemes_sorted = sorted(
            split_phonemes, key=lambda kp: len(kp[0]), reverse=True
        )

        # Update IPA texts set for phonemes
        self.phoneme_texts = set(p.text for p in self.phonemes)

    def split(
        self,
        pron_str: typing.Union[str, Pronunciation],
        keep_stress: bool = True,
        keep_accents: typing.Optional[bool] = None,
        drop_tones: bool = False,
        is_ipa: bool = True,
    ) -> typing.List[Phoneme]:
        """Split an IPA pronunciation into phonemes"""
        if not self._ipa_map_regex:
            self.update()

        if keep_accents is None:
            keep_accents = keep_stress

        word_phonemes: typing.List[Phoneme] = []

        if self.ipa_map:
            if isinstance(pron_str, Pronunciation):
                pron_str = "".join(p.text for p in pron_str)

            def handle_replace(match):
                text = match.group(1)
                return self.ipa_map.get(text, text)

            pron_str = self._ipa_map_regex.sub(handle_replace, pron_str)

        # Get text for IPA phones
        if isinstance(pron_str, Pronunciation):
            # Use supplied pronunication
            ipas = [pb.text for pb in pron_str]
        elif is_ipa:
            # Split string into pronunciation
            pron = Pronunciation.from_string(
                pron_str,
                keep_stress=keep_stress,
                keep_accents=keep_accents,
                drop_tones=drop_tones,
            )
            ipas = [pb.text for pb in pron]
        else:
            ipas = IPA.graphemes(pron_str)

        # Keep stress and tones separate to make phoneme comparisons easier
        ipa_stress: typing.Dict[int, str] = defaultdict(str)
        ipa_tones: typing.Dict[int, str] = defaultdict(str)

        if is_ipa:
            in_tone = False
            for ipa_idx, ipa in enumerate(ipas):
                if ipa:
                    keep_ipa = ""
                    for codepoint in ipa:
                        if IPA.is_accent(codepoint) and (not in_tone):
                            if keep_accents:
                                ipa_stress[ipa_idx] += codepoint
                        elif IPA.is_stress(codepoint):
                            if keep_stress:
                                ipa_stress[ipa_idx] += codepoint
                        elif in_tone and (
                            codepoint in {IPA.TONE_GLOTTALIZED, IPA.TONE_SHORT}
                        ):
                            # Interpret as part of time
                            if not drop_tones:
                                ipa_tones[ipa_idx] += codepoint
                        elif IPA.is_tone(codepoint):
                            if not drop_tones:
                                ipa_tones[ipa_idx] += codepoint

                            in_tone = True
                        else:
                            keep_ipa += codepoint

                    ipas[ipa_idx] = keep_ipa

        num_ipas: int = len(ipas)

        # ---------------------------------------------------------------------

        # pylint: disable=consider-using-enumerate
        for ipa_idx in range(len(ipas)):
            ipa = ipas[ipa_idx]
            if ipa is None:
                # Skip replaced piece
                continue

            phoneme_match = False
            for phoneme_ipas, phoneme in self._phonemes_sorted:
                if ipa_idx <= (num_ipas - len(phoneme_ipas)):
                    phoneme_match = True
                    phoneme_stress = ""
                    phoneme_tones = ""

                    # Look forward into sequence
                    for phoneme_idx in range(len(phoneme_ipas)):
                        phoneme_stress += ipa_stress[ipa_idx + phoneme_idx]
                        phoneme_tones += ipa_tones[ipa_idx + phoneme_idx]

                        if phoneme_ipas[phoneme_idx] != ipas[ipa_idx + phoneme_idx]:
                            phoneme_match = False
                            break

                    if phoneme_match:
                        # Successful match
                        if phoneme_stress or phoneme_tones:
                            # Create a copy of the phoneme with applied stress/tones
                            phoneme = Phoneme(
                                text=(phoneme_stress + phoneme.text + phoneme_tones),
                                example=phoneme.example,
                            )

                        word_phonemes.append(phoneme)

                        # Patch ipas to skip replaced pieces
                        for phoneme_idx in range(1, len(phoneme_ipas)):
                            ipas[ipa_idx + phoneme_idx] = None

                        break

            if not phoneme_match:
                # Add unknown phoneme
                word_phonemes.append(Phoneme(text=ipa, unknown=True))

        return word_phonemes


# -----------------------------------------------------------------------------


def resolve_lang(lang: str) -> str:
    """Resolve language with known aliases"""
    if "/" in lang:
        lang, rest = lang.split("/", maxsplit=1)
        lang = LANG_ALIASES.get(lang, lang)
        return f"{lang}/{rest}"

    return LANG_ALIASES.get(lang, lang)


# -----------------------------------------------------------------------------


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
