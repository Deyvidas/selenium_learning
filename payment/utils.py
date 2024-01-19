import re
from dataclasses import dataclass

from prompt_toolkit.document import Document
from questionary import Choice
from questionary import Question
from questionary import ValidationError
from questionary import Validator
from questionary import checkbox
from questionary import select


def single_choice(question: str, choices: list[Choice]) -> Question:
    form = select(message=question, choices=choices)
    return form


def multi_choice(question: str, choices: list[Choice]) -> Question:
    form = checkbox(message=question, choices=choices)
    return form


@dataclass(frozen=True)
class FloatValidator(Validator):
    old_value: float

    def validate(self, document: Document) -> None:
        number = document.text

        if self.is_invalid_float(number):
            raise ValidationError(
                cursor_position=len(number),
                message='Please enter correct float e.g. X,XX or X.XX',
            )
        elif self.is_lt_old_value(number):
            raise ValidationError(
                cursor_position=len(number),
                message=f'Please enter value not less than {self.old_value}',
            )

    def is_lt_old_value(self, value: str) -> bool:
        """If the value of 'value' is less than'self.old_value', return True,
        else return False.
        """
        return float(value.replace(',', '.')) < self.old_value

    def is_invalid_float(self, number: str, *, decimals: int = 6) -> bool:
        """Return True if signs after `.` or `,` exceed value of decimals attr,
        or if it is not possible to convert the string to float. Otherwise,
        return False.
        """
        regex = rf'^[\d]+[,.]?[\d]{{0,{decimals}}}$'
        return re.fullmatch(regex, number) is None


def float_is_valid(number: str, *, decimals: int = 6) -> bool:
    """Return False if signs after `.` or `,` exceed value of decimals attr, or
    if it is not possible to convert the string to float. Otherwise, return
    True.
    """
    regex = rf'^[\d]+[,.]?[\d]{{0,{decimals}}}$'
    return not re.fullmatch(regex, number) is None
