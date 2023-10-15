import re
from collections import namedtuple
from typing import Optional

from selenium.webdriver.remote.webelement import WebElement


def get_book_title(book_card: WebElement) -> str:
    """Return title of book."""
    title = book_card.find_element('xpath', './/h3/a').get_attribute('title')
    return title


def get_book_price(book_card: WebElement) -> int:
    """Return price of book."""
    # Get price with this format £51.77.
    price_with_currency = book_card.find_element(
        'xpath', './/div[@class="product_price"]/p[@class="price_color"]'
    ).text
    # Set price with this format 51.77 (as float) or None if incorrect.
    price_no_currency = _get_only_price(price_with_currency)
    return price_no_currency


def book_in_stock(book_card: WebElement) -> bool:
    """Return True if `string=In stock` else False."""
    book_in_stock_string = book_card.find_element(
        'xpath',
        './/div[@class="product_price"]/p[@class="instock availability"]'
    ).text
    return book_in_stock_string == 'In stock'


def _get_only_price(price_with_currency: str) -> Optional[float]:
    r"""
    Return float price if in passed string can find format `[\d]+[.,][\d]{2}`
    else return None.
    """
    # Replace ',' because Python cant convert to float('12,33') need '12.33'.
    price_with_currency = price_with_currency.replace(',', '.')
    price_clear = re.findall(r'[\d]+[.][\d]{2}', price_with_currency)
    if price_clear == list():
        return None
    return float(price_clear[0])


TestCase = namedtuple('TestCase', 'passed expected')

get_only_price_tests = [
    TestCase(passed='£51.77', expected=51.77),
    TestCase(passed='£51,77', expected=51.77),
    TestCase(passed='51.77£', expected=51.77),
    TestCase(passed='51,77£', expected=51.77),
    TestCase(passed='51.77', expected=51.77),
    TestCase(passed='51,77', expected=51.77),
    TestCase(passed='9999.99', expected=9999.99),
    TestCase(passed='0.99', expected=0.99),
    TestCase(passed='0.00', expected=0.00),
    TestCase(passed='0.996', expected=0.99),
    TestCase(passed='.99', expected=None),
    TestCase(passed='9.9', expected=None),
]

for test_case in get_only_price_tests:
    assert _get_only_price(test_case.passed) == test_case.expected
