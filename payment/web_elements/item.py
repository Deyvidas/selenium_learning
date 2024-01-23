from typing import override

from selenium.webdriver.remote.webelement import WebElement

from payment.web_elements.base import ElementBase
from payment.web_elements.base import ElementHidden
from payment.web_elements.base import ElementVisible
from payment.web_elements.exceptions import ErrorElementDoesNotFound


class ItemBase(ElementBase):
    ...


class ItemHidden(ElementHidden, ItemBase):
    ...


class ItemVisible(ElementVisible, ItemBase):
    ...


class ItemHiddenOptional(ElementHidden, ItemBase):
    @property
    @override
    def element(self) -> WebElement:
        try:
            return super().element
        except ErrorElementDoesNotFound:
            return self._get_web_element_one_or_stub()
