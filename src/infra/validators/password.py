import re
import string

from ..defaults.exeptions.password import WeakPasswordError


def is_strong_pass(
    passwd: str,
    chars: int = 10,
    lowers: int = 3,
    uppers: int = 1,
    digits: int = 2,
    specials: int = 2,
):  # noqa
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

    def s(case):
        return 's' if case > 1 else ''

    if not is_strong:
        if len(passwd) < chars:
            raise WeakPasswordError(
                passwd, f'A senha deve ter pelo menos {chars} caracteres'
            )
        if len([char for char in passwd if char.isdigit()]) < digits:
            raise WeakPasswordError(
                passwd,
                f'A senha deve conter pelo menos {digits} dígito{s(digits)}',
            )
        if len([char for char in passwd if char.isupper()]) < uppers:
            raise WeakPasswordError(
                passwd,
                f'A senha deve conter pelo menos {uppers} letra{s(uppers)} maiúscula{s(uppers)}',
            )
        if len([char for char in passwd if char.islower()]) < lowers:
            raise WeakPasswordError(
                passwd,
                f'A senha deve conter pelo menos {lowers} letra{s(lowers)} minúscula{s(lowers)}',
            )
        if (
            len([char for char in passwd if char in string.punctuation])
            < specials
        ):
            end = 'ais' if 's' == s(lowers) else 'l'
            raise WeakPasswordError(
                passwd,
                f'A senha deve conter pelo menos {specials} caractere{s(specials)} especia{end}',
            )
    return True


def is_valid_document(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    def calc_digit(cpf, weights):
        return sum(int(cpf[i]) * weights[i] for i in range(len(weights))) % 11

    weights1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    digit1 = calc_digit(cpf, weights1)
    digit1 = 0 if digit1 < 2 else 11 - digit1

    weights2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    digit2 = calc_digit(cpf, weights2)
    digit2 = 0 if digit2 < 2 else 11 - digit2

    if cpf[-2:] == f'{digit1}{digit2}':
        return cpf
    return False
