import sys

from selenium.common import ElementNotInteractableException
from selenium.webdriver import Keys

from payment.web_elements.base import ElementBase
from payment.web_elements.base import ElementVisible
from payment.web_elements.exceptions import ErrorElementNotWritable


class InputBase(ElementBase):
    @property
    def placeholder(self) -> str | None:
        self.raise_if_stub()
        return self.element.get_attribute('placeholder')


class InputVisible(ElementVisible, InputBase):
    def send_keys(self, text: str) -> None:
        self.raise_if_stub()
        try:
            self.element.send_keys(text)
        except ElementNotInteractableException:
            raise ErrorElementNotWritable(**self.error_required_kwargs)

    def clear(self) -> None:
        self.raise_if_stub()
        assert isinstance(self.text, str), 'The text is expected to be only string.'  # fmt: skip
        if self.text == '':
            return
        select_all = Keys.CONTROL + 'a'
        if sys.platform.startswith('darwin'):
            select_all = Keys.COMMAND + 'a'
        self.send_keys(select_all + Keys.BACK_SPACE)
        # Check if the field is empty;
        assert self.element.text == ''

    def send_keys_with_clear(self, text: str) -> None:
        self.raise_if_stub()
        self.clear()
        self.send_keys(text)
