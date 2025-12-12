import re
import string

from uuid6 import uuid7


def get_uuid():
    return str(uuid7())


def is_strong_pass(
    passwd: str,
    chars: int = 8,
    lowers: int = 2,
    uppers: int = 1,
    digits: int = 1,
    specials: int = 1,
):
    is_strong = re.search(
        (
            r'(?=^.{%i,}$)'
            r'(?=.*[a-z]{%i,})'
            r'(?=.*[A-Z]{%i})'
            r'(?=.*[0-9]{%i,})'
            r'(?=.*[%s}]{%i,})'
        )
        % (
            chars,
            lowers,
            uppers,
            digits,
            re.escape(string.punctuation),
            specials,
        ),
        passwd,
    )
    return is_strong
