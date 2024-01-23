from typing import Any
from typing import NotRequired
from typing import Required
from typing import TypedDict
from typing import Unpack


class KwargsBasePageError(TypedDict):
    url: Required[str]
    location: NotRequired[str]
    details: Required[str]


class BasePageError(Exception):
    message: str

    def __init__(self, **kwargs: Unpack[KwargsBasePageError]) -> None:
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


class ErrorPageCantFindElement(BasePageError):
    message = 'The element is not present on the current web page.'
