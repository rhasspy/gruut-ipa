#!/usr/bin/env python3
"""Command-line interface to gruut-ipa"""
import argparse
import itertools
import json
import logging
import os
import sys
import typing
from pathlib import Path

# -----------------------------------------------------------------------------

_LOGGER = logging.getLogger("gruut_ipa")

_DIR = Path(__file__).parent
_DATA_DIR = _DIR / "data"

# -----------------------------------------------------------------------------


def main():
    """Main entry point"""
    args = get_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    _LOGGER.debug(args)

    # Dispatch to sub-command
    args.func(args)


# -----------------------------------------------------------------------------


def do_print(args):
    """Print known IPA phones"""
    from . import Phoneme, Phonemes, VOWELS, CONSONANTS, SCHWAS
    from .espeak import ipa_to_espeak
    from .sampa import ipa_to_sampa

    allowed_phonemes: typing.Set[str] = set()

    if args.language:
        # Load phonemes using language code
        phonemes_path = _DATA_DIR / args.language / "phonemes.txt"

        _LOGGER.debug("Loading phonemes from %s", phonemes_path)
        with open(phonemes_path, "r") as phonemes_file:
            phonemes = Phonemes.from_text(phonemes_file)

        allowed_phonemes.update(p.text for p in phonemes)

    for phone_str in sorted(itertools.chain(VOWELS, CONSONANTS, SCHWAS)):
        phone = Phoneme(phone_str)

        if allowed_phonemes and (phone.text not in allowed_phonemes):
            # Skip phoneme outside language
            continue

        description = ""
        if phone.vowel:
            v = phone.vowel
            description = (
                v.height.value
                + " "
                + v.placement.value
                + " "
                + ("rounded" if v.rounded else "unrounded")
                + " vowel"
            )
        elif phone.consonant:
            c = phone.consonant
            description = (
                ("voiced" if c.voiced else "voiceless")
                + " "
                + c.place.value
                + " "
                + c.type.value
            )
        elif phone.schwa:
            s = phone.schwa
            if s.r_coloured:
                description = "r-coloured schwa"
            else:
                description = "schwa"

        phone_dict = phone.to_dict()
        phone_dict["description"] = description

        # Add espeak/sampa
        phone_dict["espeak"] = ipa_to_espeak(phone_str)
        phone_dict["sampa"] = ipa_to_sampa(phone_str)

        phone_dict_str = json.dumps(phone_dict, ensure_ascii=False)
        print(phone_dict_str)


# -----------------------------------------------------------------------------


def do_describe(args):
    """Describe IPA phones"""
    from . import Phoneme

    if args.phone:
        # From arguments
        phones = args.phone
    else:
        # From stdin
        phones = sys.stdin

        if os.isatty(sys.stdin.fileno()):
            print("Reading phones from stdin...", file=sys.stderr)

    for line in phones:
        line = line.strip()
        if line:
            line_phone = Phoneme(text=line)
            phone_str = json.dumps(line_phone.to_dict(), ensure_ascii=False)
            print(phone_str)
            sys.stdout.flush()


# -----------------------------------------------------------------------------


def do_phones(args):
    """Group phones in IPA pronunciation"""
    from . import Pronunciation

    if args.pronunciation:
        # From arguments
        pronunciations = args.pronunciation
    else:
        # From stdin
        pronunciations = sys.stdin

        if os.isatty(sys.stdin.fileno()):
            print("Reading pronunciations from stdin...", file=sys.stderr)

    for line in pronunciations:
        line = line.strip()
        if line:
            line_pron = Pronunciation.from_string(line)
            phones_str = args.separator.join(p.text for p in line_pron if p.text)
            print(phones_str)
            sys.stdout.flush()


# -----------------------------------------------------------------------------


def do_phonemes(args):
    """Group phones in IPA pronuncation according to language phonemes"""
    from . import Phonemes

    if args.pronunciation:
        # From arguments
        pronunciations = args.pronunciation
    else:
        # From stdin
        pronunciations = sys.stdin

        if os.isatty(sys.stdin.fileno()):
            print("Reading pronunciations from stdin...", file=sys.stderr)

    if args.phonemes_file:
        # Load phonemes from file
        phonemes_path = Path(args.phonemes_file)
    else:
        # Load phonemes using language code
        phonemes_path = _DATA_DIR / args.language / "phonemes.txt"

        # Check language support
        if not phonemes_path.is_file():
            supported_languages = [d.name for d in _DATA_DIR.iterdir() if d.is_dir()]
            _LOGGER.fatal("Unsupported language: %s", args.language)
            _LOGGER.fatal("Supported languages: %s", supported_languages)
            sys.exit(1)

    _LOGGER.debug("Loading phonemes from %s", phonemes_path)
    with open(phonemes_path, "r") as phonemes_file:
        phonemes = Phonemes.from_text(phonemes_file)

    for line in pronunciations:
        line = line.strip()
        if line:
            line_phonemes = phonemes.split(
                line, keep_stress=args.keep_stress, drop_tones=args.drop_tones
            )
            phonemes_str = args.separator.join(p.text for p in line_phonemes if p.text)
            print(phonemes_str)
            sys.stdout.flush()


# -----------------------------------------------------------------------------


def do_convert(args):
    """Convert pronunciations between different representations"""
    from . import Phoneme, Phonemes
    from .espeak import espeak_to_ipa, ipa_to_espeak
    from .sampa import ipa_to_sampa, sampa_to_ipa

    fixed_src_dest = {"ipa", "espeak", "sampa"}
    src_phonemes: typing.Optional[Phonemes] = None
    dest_phonemes: typing.Optional[Phonemes] = None

    if args.src not in fixed_src_dest:
        src_phonemes = Phonemes.from_language(args.src)

    if args.dest not in fixed_src_dest:
        dest_phoneme_map = Phonemes.from_language(args.dest).gruut_ipa_map

        # ipa -> original phoneme
        dest_phonemes = Phonemes()
        for k, v in dest_phoneme_map.items():
            if v in dest_phonemes.gruut_ipa_map:
                continue

            dest_phonemes.phonemes.append(Phoneme(text=k, is_ipa=False))
            dest_phonemes.ipa_map[v] = k

        dest_phonemes.update()

    if args.pronunciation:
        # From arguments
        pronunciations = args.pronunciation
    else:
        # From stdin
        pronunciations = sys.stdin

        if os.isatty(sys.stdin.fileno()):
            print("Reading pronunciations from stdin...", file=sys.stderr)

    for line in pronunciations:
        line = line.strip()
        if line:
            if args.src == "ipa":
                src_ipa = line
            elif args.src == "espeak":
                src_ipa = espeak_to_ipa(line)
            elif args.src == "sampa":
                src_ipa = sampa_to_ipa(line)
            else:
                assert src_phonemes is not None
                src_ipa = args.separator.join(
                    src_phonemes.gruut_ipa_map.get(p.text, p.text)
                    for p in src_phonemes.split(line)
                )

            if args.dest == "ipa":
                dest_pron = src_ipa
            elif args.dest == "espeak":
                dest_pron = "[[" + ipa_to_espeak(src_ipa) + "]]"
            elif args.dest == "sampa":
                dest_pron = ipa_to_sampa(src_ipa)
            else:
                assert dest_phonemes is not None
                dest_pron = args.separator.join(
                    p.text for p in dest_phonemes.split(src_ipa, is_ipa=False)
                )

            print(dest_pron)
            sys.stdout.flush()


# -----------------------------------------------------------------------------


def get_args() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(prog="gruut_ipa")

    # Create subparsers for each sub-command
    sub_parsers = parser.add_subparsers()
    sub_parsers.required = True
    sub_parsers.dest = "command"

    # -----
    # print
    # -----
    print_parser = sub_parsers.add_parser("print", help="Print all known IPA phones")
    print_parser.add_argument(
        "--language", help="Only print phones from a specific language or language/set"
    )
    print_parser.set_defaults(func=do_print)

    # --------
    # describe
    # --------
    describe_parser = sub_parsers.add_parser("describe", help="Describe IPA phone(s)")
    describe_parser.set_defaults(func=do_describe)
    describe_parser.add_argument(
        "phone", nargs="*", help="IPA phones (read from stdin if not provided)"
    )

    # --------
    # phones
    # --------
    phones_parser = sub_parsers.add_parser(
        "phones", help="Group phones in IPA pronunciation"
    )
    phones_parser.set_defaults(func=do_phones)
    phones_parser.add_argument(
        "pronunciation",
        nargs="*",
        help="IPA pronunciations (read from stdin if not provided)",
    )
    phones_parser.add_argument(
        "--separator",
        default=" ",
        help="Separator to add between phones in output (default: space)",
    )

    # --------
    # phonemes
    # --------
    phonemes_parser = sub_parsers.add_parser(
        "phonemes",
        help="Group phones in IPA pronunciation according to language phonemes",
    )
    phonemes_parser.set_defaults(func=do_phonemes)
    phonemes_parser.add_argument("language", help="Language code (e.g., en-us)")
    phonemes_parser.add_argument(
        "pronunciation",
        nargs="*",
        help="IPA pronunciations (read from stdin if not provided)",
    )
    phonemes_parser.add_argument(
        "--separator",
        default=" ",
        help="Separator to add between phonemes in output (default: space)",
    )
    phonemes_parser.add_argument(
        "--keep-stress",
        action="store_true",
        help="Keep primary/secondary stress markers",
    )
    phonemes_parser.add_argument(
        "--drop-tones", action="store_true", help="Remove tone numbers/letters"
    )
    phonemes_parser.add_argument(
        "--phonemes-file", help="Load phonemes from file instead of using language code"
    )

    # -------
    # convert
    # -------
    convert_parser = sub_parsers.add_parser(
        "convert", help="Convert pronunciations between ipa, espeak, and sampa"
    )
    convert_parser.set_defaults(func=do_convert)
    convert_parser.add_argument(
        "src", help="Source format (language, language/set, ipa, espeak, sampa)"
    )
    convert_parser.add_argument(
        "dest", help="Destination format (language, language/set, ipa, espeak, sampa)"
    )
    convert_parser.add_argument(
        "pronunciation",
        nargs="*",
        help="Pronunciations (read from stdin if not provided)",
    )
    convert_parser.add_argument(
        "--separator", default=" ", help="Separator between phonemes (default: space)"
    )

    # Shared arguments
    for sub_parser in [
        print_parser,
        describe_parser,
        phones_parser,
        phonemes_parser,
        convert_parser,
    ]:
        sub_parser.add_argument(
            "--debug", action="store_true", help="Print DEBUG messages to console"
        )

    return parser.parse_args()


# -----------------------------------------------------------------------------


if __name__ == "__main__":
    main()
