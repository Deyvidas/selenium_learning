import sys
from dataclasses import dataclass
from dataclasses import field
from typing import NamedTuple

from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


more_that_one_found = '{name}(url={url}).find_element(location={location}) found multiple elements.'  # fmt: skip
elements_not_found = '{name}(url={url}).find_elements(location={location}) can\'t find elements.'  # fmt: skip
element_is_not_clickable = '{name}(url={url}).click_button(location={location}) is not clickable.'  # fmt: skip


@dataclass(kw_only=True)
class BaseDriver:
    url: str
    driver: WebDriver
    action_chains: ActionChains = field(init=False)
    driver_wait: WebDriverWait = field(init=False)

    def __post_init__(self) -> None:
        self.action_chains = ActionChains(self.driver)
        self.driver_wait = WebDriverWait(
            driver=self.driver,
            timeout=10,
            poll_frequency=2,
        )
        self.driver.get(self.url)

    def write_into(self, location: str, string: str) -> WebElement:
        field = self.find_element(location)
        field = self.clear(field)
        field.send_keys(string)
        assert field.get_attribute('value') == string
        return field

    def click_button(self, location: str) -> WebElement:
        loc = ('xpath', location)
        condition = expected_conditions.element_to_be_clickable(loc)
        msg = element_is_not_clickable.format(
            name=type(self).__name__,
            url=self.url,
            location=location,
        )
        button = self.driver_wait.until(condition, message=msg)
        button.click()
        return button

    def find_child(self, location: str, parent: WebElement) -> WebElement:
        element = self.find_childs(location, parent)
        if len(element) == 1:
            return element[0]
        msg = more_that_one_found.format(
            name=type(self).__name__,
            url=self.url,
            location=location,
        )
        raise ValueError(msg)

    def find_childs(self, location: str, parent: WebElement) -> list[WebElement]:  # fmt: skip
        locator = ('xpath', location)
        elements = parent.find_elements(*locator)
        return elements

    def find_element(self, location: str) -> WebElement:
        element = self.find_elements(location)
        if len(element) == 1:
            return element[0]
        msg = more_that_one_found.format(
            name=type(self).__name__,
            url=self.url,
            location=location,
        )
        raise ValueError(msg)

    def find_elements(self, location: str) -> list[WebElement]:
        loc = ('xpath', location)
        elements = expected_conditions.presence_of_all_elements_located(loc)
        msg = elements_not_found.format(
            name=type(self).__name__,
            url=self.url,
            location=location,
        )
        return self.driver_wait.until(elements, message=msg)

    def clear(self, field: WebElement) -> WebElement:
        """Call the send_keys method with the arguments CTRL+'a' or CMD+'a' and
        assert that the field has been cleared and return it.

        - `CMD+'a'` - if platform.startswith('darwin');
        - `CTRL+'a'` - else.
        """
        select_all = Keys.CONTROL + 'a'
        if sys.platform.startswith('darwin'):
            select_all = Keys.COMMAND + 'a'
        field.send_keys(select_all + Keys.BACKSPACE)
        # Check if the field is empty;
        assert self.check_field_value(field, '')
        return field

    def check_field_value(self, field: WebElement, text: str) -> bool:
        """Compare the DOM element attribute 'value' with the passed 'text' or
        if the DOM element doest have a attribute 'value' compare the WebElement.text
        with the passed 'text'. Return True if are equal, else False.
        """
        value = field.get_attribute('value')
        if value is not None:
            return value == text
        else:
            return field.text == text


class CartLocator(NamedTuple):
    text_service_name: str
    button_cart: str
    cards_of_services: str
    button_remove_service: str


class BasePage(BaseDriver):
    cart_loc: CartLocator = CartLocator(
        text_service_name='//form[@name="PaymentForm"]//*[@class="block-title"]',
        button_cart='//a[@class="header-mobile-basket"]',
        cards_of_services='//table[contains(@class, "cart-inner-services-table")]',
        button_remove_service='//a[@class="cart-inner-remove-item"]',
    )

    def remove_service_from_cart(self):
        """Click the button that removes services that have a title that is
        identical to the form title of the current page.
        """
        s = self.get_service_card_in_cart()
        button = self.find_child(f'.{self.cart_loc.button_remove_service}', s)
        button.click()

    def get_service_card_in_cart(self) -> WebElement:
        """Find a single cart that has a title that is identical to the form
        title of the current page.
        """
        service_name = self.find_element(self.cart_loc.text_service_name).text
        self.click_button(self.cart_loc.button_cart)
        services = self.find_elements(self.cart_loc.cards_of_services)
        for s in services:
            n = self.find_child('.//td[@class="cart-inner-services-name"]', s)
            if n.text.lower() in service_name.lower():
                return s
        raise NoSuchElementException(f'Service {service_name} not found.')

    def print_success(self, message: str) -> None:
        print('+' * 100)
        print('{:+^100}'.format(f' {message} '))
        print('+' * 100)
