from typing import Any
from typing import NotRequired
from typing import Required
from typing import TypedDict
from typing import Unpack


class KwargsBaseError(TypedDict):
    class_name: Required[str]
    url: Required[str]
    location: Required[str]
    attribute: NotRequired[str]
    original_error: NotRequired[str]


class BaseError(Exception):
    message: str

    def __init__(self, **kwargs: Unpack[KwargsBaseError]) -> None:
        message = self.get_message(**kwargs)
        super().__init__(message)

    def get_message(self, **kwargs: Any) -> str:
        sep = f'\n{'-' * len(self.message)}\n'  # fmt: skip
        message = f'{sep}{self.message}{sep}'
        message = f'{message}{self.join_kwargs(**kwargs)}\n'
        return message

    def join_kwargs(self, **kwargs: Any) -> str:
        width = max(len(a) for a in kwargs)
        strings = list()
        for key, value in kwargs.items():
            string = '{key:{align}{width}}: {value}'.format(
                key=key, value=value, width=width, align='>'
            )
            strings.append(string)
        return '\n'.join(strings)


class ErrorElementDoesNotFound(BaseError):
    message = 'There is no WebElement present on the page.'


class ErrorFoundMultipleElements(BaseError):
    message = 'The page contains more than one WebElement.'


class ErrorElementNotClickable(BaseError):
    message = 'The WebElement can be present in the DOM, but it is not clickable.'  # fmt: skip


class ErrorElementNotVisible(BaseError):
    message = 'The WebElement can be present in the DOM, but it is not visible.'  # fmt: skip


class ErrorElementNotWritable(BaseError):
    message = 'The selected WebElement does not support writing to it.'


class ErrorElementDoesNotHaveAttribute(BaseError):
    message = 'The HTML element related to WebElement has not requested attribute.'  # fmt: skip


class ErrorStubIsNotAccessible(BaseError):
    message = 'The stub is not accessible for interaction.'
