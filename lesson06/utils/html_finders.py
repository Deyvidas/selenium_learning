from typing import Required
from typing import TypedDict
from typing import Unpack

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class FindKwargs(TypedDict):
    root: Required[WebDriver | WebElement]
    xpath: Required[str]


def find_element(**kwargs: Unpack[FindKwargs]) -> WebElement:
    root = kwargs['root']
    xpath = kwargs['xpath']
    return root.find_element(by='xpath', value=xpath)


def find_elements(**kwargs: Unpack[FindKwargs]) -> list[WebElement]:
    root = kwargs['root']
    xpath = kwargs['xpath']
    return root.find_elements(by='xpath', value=xpath)
