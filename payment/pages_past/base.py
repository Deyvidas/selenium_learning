from __future__ import annotations

import datetime as dt
import sys
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from functools import wraps
from re import findall
from time import sleep
from typing import NamedTuple
from typing import NoReturn

from pydantic import BaseModel
from questionary import Choice
from questionary import confirm
from questionary import print as q_print
from questionary import text
from selenium.common import NoSuchElementException
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from payment.utils import FloatValidator
from payment.utils import float_is_valid
from payment.utils import multi_choice


more_that_one_found = '{name}(url={url}).find_element(location={location}) found multiple elements.'  # fmt: skip
elements_not_found = '{name}(url={url}).find_elements(location={location}) can\'t find elements.'  # fmt: skip
element_is_not_clickable = '{name}(url={url}).click_button(location={location}) is not clickable.'  # fmt: skip
element_not_have_attr_value = 'The DOM element {location} has no attribute \'value\'.'  # fmt: skip


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
            timeout=3,
            poll_frequency=0.5,
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
        click_script = 'arguments[0].click();'
        self.driver.execute_script(click_script, button)
        return button

    def find_child(self, location: str, parent: WebElement) -> WebElement:
        element = self.find_childs(location, parent)
        if len(element) == 1:
            return element[0]
        self.raise_more_than_one_found(location)

    def find_childs(self, location: str, parent: WebElement) -> list[WebElement]:  # fmt: skip
        locator = ('xpath', location)
        elements = parent.find_elements(*locator)
        return elements

    def get_parent(self, child: WebElement, depth: int = 1) -> WebElement:
        element = child
        while depth > 0:
            script = 'return arguments[0].parentNode;'
            element = self.driver.execute_script(script, element)
            depth -= 1
            if element.tag_name == 'html' and depth > 0:
                raise ValueError('The html element has not parents.')
        return element

    def find_element(self, location: str) -> WebElement:
        element = self.find_elements(location)
        if len(element) > 1:
            self.raise_more_than_one_found(location)
        elif len(element) == 0:
            self.raise_elements_not_found(location)
        return element[0]

    def find_elements(self, location: str) -> list[WebElement]:
        loc = ('xpath', location)
        elements = expected_conditions.presence_of_all_elements_located(loc)
        try:
            return self.driver_wait.until(elements)
        except TimeoutException:
            return list()

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

    def get_more_than_one_found_msg(self, location: str) -> str:
        return more_that_one_found.format(
            name=type(self).__name__,
            url=self.url,
            location=location,
        )

    def raise_more_than_one_found(self, location: str) -> NoReturn:
        msg = self.get_more_than_one_found_msg(location)
        raise ValueError(msg)

    def get_elements_not_found_msg(self, location: str) -> str:
        return elements_not_found.format(
            name=type(self).__name__,
            url=self.url,
            location=location,
        )

    def raise_elements_not_found(self, location: str) -> NoReturn:
        msg = self.get_elements_not_found_msg(location)
        raise NoSuchElementException(msg)


class Receipt(BaseModel):
    without_fees: float
    include_fees: float
    charged_fees: float


class CartLocator(NamedTuple):
    text_service_name: str
    button_cart: str
    cards_of_services: str
    button_remove_service: str


class AuthorizationLocator(NamedTuple):
    card_location: str
    input_account: str
    button_confirm: str
    text_check_account: str


class PayLocator(NamedTuple):
    input_period: str
    input_new_value: str
    text_old_value: str
    button_make_calc: str
    text_cost_without_fees: str
    text_cost_include_fees: str
    text_total_fees: str
    button_add_to_cart: str


cart_locator = CartLocator(
    text_service_name='//form[@name="PaymentForm"]//*[@class="block-title"]',
    button_cart='//a[@class="header-mobile-basket"]',
    cards_of_services='//table[contains(@class, "cart-inner-services-table")]',
    button_remove_service='//a[@class="cart-inner-remove-item"]',
)


auth_locator = AuthorizationLocator(
    card_location='//*[text()="Каталог услуг"]/..//b[text()=\'{service}\']',
    input_account='//input[@id="group-1-field-0-value"]',
    button_confirm='//button[text()="Проверить"]',
    text_check_account='//b[@class="account-header-number"]',
)


pay_locator = PayLocator(
    input_period='//input[@id="DatePeriod"]',
    input_new_value='//input[contains(@class, "newReading")]',
    text_old_value='//td[contains(@class, "oldReading")]',
    button_make_calc='//a[@id="calcButton"]',
    text_cost_without_fees='//input[@id="totalAmount"]',
    text_cost_include_fees='//b[@id="labelTotalSummComm"]',
    text_total_fees='//p[@class="payment-bottom-total-commission"]//span',
    button_add_to_cart='//*[contains(@class, "add-to-cart-btn")]',
)


def open_close_cart_page(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        self: BasePage = args[0]
        url_before = self.driver.current_url
        self.driver.get(self.cart_url)
        result = function(*args, **kwargs)
        self.driver.get(url_before)
        return result

    return wrapper


@dataclass(kw_only=True)
class BasePage(BaseDriver):
    account_number: str
    service_name: str
    service_card: str

    home_page: str = field(default='https://lk.ric-ul.ru/', init=False)
    auth_loc: AuthorizationLocator = field(default=auth_locator, init=False)
    cart_loc: CartLocator = field(default=cart_locator, init=False)
    pay_loc: PayLocator = field(default=pay_locator, init=False)

    @property
    def cart_url(self) -> str:
        return f'{self.home_page}Basket'

    def run(self) -> bool:
        self.process_started_message()
        if not self.continue_transfer_data():
            return True
        self.step_authorization()
        self.compare_accounts()
        return True

    def process_started_message(self) -> None:
        msg = f'\n[ {self.service_name} ]'
        q_print(msg, style="bold fg: green")

    @open_close_cart_page
    def continue_transfer_data(self) -> bool:
        service = self.get_service_from_cart(self.service_name)
        if service is None:
            return True
        elif self.ask_remove_service_from_cart() is False:
            return False
        self.remove_service_from_cart(service)
        return True

    @abstractmethod
    def step_authorization(self):
        raise NotImplementedError

    def compare_accounts(self) -> None:
        used_account = self.find_element(self.auth_loc.text_check_account).text
        assert used_account.replace('ЛС № ', '') == self.account_number

    @abstractmethod
    def step_collect_old_values(self):
        raise NotImplementedError

    def ask_remove_service_from_cart(self) -> bool:
        msg = 'This service was earlier added into the cart, remove it?'
        return confirm(msg).ask()

    def remove_service_from_cart(self, service: WebElement) -> None:
        location = f'.{self.cart_loc.button_remove_service}'
        button = self.find_child(location, service)
        click_script = 'arguments[0].click();'
        self.driver.execute_script(click_script, button)
        msg = 'The service has been successfully removed from the cart!'
        q_print(msg, style='fg:green')

    def click_service_card(self) -> WebElement:
        card = self.auth_loc.card_location.format(service=self.service_card)
        return self.click_button(card)

    def input_account_number(self) -> None:
        self.write_into(self.auth_loc.input_account, self.account_number)

    def input_payment_period(self) -> None:
        today_utc = dt.datetime.now(dt.UTC).date().strftime('%m.%Y')
        field = self.write_into(self.pay_loc.input_period, today_utc)
        field.send_keys(Keys.ENTER)

    def click_check_account(self) -> None:
        self.click_button(self.auth_loc.button_confirm)
        msg = f'The {self.service_name} account verification was successfully completed'  # fmt: skip
        q_print(msg, style='fg:green')

    def get_old_data(self) -> float:
        value = self.find_element(self.pay_loc.text_old_value).text
        if float_is_valid(value):
            return float(value.replace(',', '.'))
        m = f'Old value={repr(value)}, conversion to float is not possible.'
        raise ValueError(m)

    def ask_new_data(self, old_value: float) -> float:
        message = f'Previous value: {old_value}, enter the new value:'
        new_val = text(message, validate=FloatValidator(old_value)).ask()
        if not isinstance(new_val, str):
            m = f'Cant convert {type(new_val).__name__} to float type.'
            raise TypeError(m)
        new_val = float(new_val.replace(',', '.'))
        return round(new_val, 2)

    def input_new_value(self, new: float, old: float):
        self.write_into(self.pay_loc.input_new_value, str(new))
        msg = f'Consumed resources during the last period: {new - old}, continue?'
        response = confirm(msg).ask()
        if response is False:
            self.edit_form_values()
        self.click_button(self.pay_loc.button_make_calc)

    @property
    def user_can_change(self) -> list[Choice]:
        return [
            Choice('change passed counter value', self.input_new_value),
        ]

    def edit_form_values(self):
        msg = 'What you want to change?'
        user_choices = multi_choice(msg, self.user_can_change).ask()
        if not all(map(lambda f: callable(f), user_choices)):
            raise TypeError('Choice.value must be callable.')
        [func_to_run() for func_to_run in user_choices]

    def get_all_services_in_cart(self) -> list[WebElement]:
        self.click_button(self.cart_loc.button_cart)
        return self.find_elements(self.cart_loc.cards_of_services)

    def get_service_from_cart(self, service_name: str) -> WebElement | None:
        location = f'//td[text()=\'{service_name}\']'
        found = self.find_elements(location)

        if len(found) > 1:
            self.raise_more_than_one_found(location)
        elif len(found) == 0:
            return None

        table = self.get_parent(found[0], 3)
        assert table.tag_name == 'table'
        return table

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # def remove_service_from_cart(self):
    #     """Click the button that removes services that have a title that is
    #     identical to the form title of the current page.
    #     """
    #     s = self.get_service_card_in_cart()
    #     button = self.find_child(f'.{self.cart_loc.button_remove_service}', s)
    #     button.click()

    # def get_service_card_in_cart(self) -> WebElement:
    #     """Find a single cart that has a title that is identical to the form
    #     title of the current page.
    #     """
    #     service_name = self.find_element(self.cart_loc.text_service_name).text
    #     self.click_button(self.cart_loc.button_cart)
    #     services = self.find_elements(self.cart_loc.cards_of_services)
    #     for s in services:
    #         n = self.find_child('.//td[@class="cart-inner-services-name"]', s)
    #         if n.text.lower() in service_name.lower():
    #             return s
    #     raise NoSuchElementException(f'Service {service_name} not found.')

    # def skip_input(self) -> bool:
    #     """If the service is already in the cart, the client can choose to skip
    #     the process of entering new gas data, then function return True, also
    #     client can remove service from cart, and enter new data, then function
    #     return False and finally if the service not in cart function return
    #     False.
    #     """
    #     page_url = self.driver.current_url
    #     add_to_cart_button = self.find_element(self.pay_loc.button_add_to_cart)
    #     if add_to_cart_button.text == 'Добавить в корзину':
    #         return False

    #     msg = 'This service was earlier added into the cart, remove it?'
    #     resp = confirm(msg).ask()
    #     if resp is False:
    #         return True

    #     self.ask_remove_service_from_cart()
    #     self.driver.get(page_url)
    #     self.enter_account_number()
    #     return False

    # def enter_account_number(self):
    #     """Enter the account number of the user, press confirm, and check if the
    #     authorization has been passed correctly.
    #     """
    #     self.write_into(self.auth_loc.input_account, self.account_number)
    #     self.click_button(self.auth_loc.button_confirm)
    #     # Ensure that the account number on the next page corresponds with the
    #     # one in the profile.
    #     used_account = self.find_element(self.auth_loc.text_check_account).text
    #     assert used_account.replace('ЛС № ', '') == self.account_number

    # def enter_new_value(self):
    #     """Ask the user to provide the new value of the gas counter, and write
    #     it into the field.
    #     """
    #     old_val, new_val = self.ask_new_data()
    #     self.write_into(self.pay_loc.input_new_value, str(new_val))
    #     diff = round(new_val, 2) - round(old_val, 2)
    #     msg = f'Total volume of gas expended: {diff} m2, confirm?'  # TODO change message.
    #     resp = confirm(msg).ask()
    #     if resp is False:
    #         self.edit_form_values()
    #     self.click_button(self.pay_loc.button_make_calc)

    def run_payment_process(self):
        """Inform the customer of the payment amount. If the client wants to
        add this service to the cart, click the button 'Add to Cart'.
        """
        total_to_pay = self.build_receipt().include_fees
        msg = f'Total to pay: {total_to_pay}₽, add this service into the cart?'
        resp = confirm(msg).ask()
        if resp is False:
            # TODO WHAT TO DO IF CLIENT DOES NOT WANT TO ADD SERVICE INTO THE CART?
            msg = 'At this time, this choice has not been realized.'
            q_print(msg, style='italic fg:yellow')

        add_to_cart_button = self.find_element(self.pay_loc.button_add_to_cart)
        add_to_cart_button.click()
        msg = f'The service {self.service_name} is added into the cart!'
        q_print(msg, style='bold fg:green')

    # @property
    # def user_can_change(self) -> list[Choice]:
    #     return [
    #         Choice('change passed counter value', self.input_new_value),
    #     ]

    # def edit_form_values(self):
    #     """Provide a list of methods, that users can select to change already
    #     existing values, and execute all methods selected by the user.
    #     """
    #     msg = 'What you want to change?'
    #     user_choices = multi_choice(msg, self.user_can_change).ask()
    #     if not all(map(lambda f: callable(f), user_choices)):
    #         raise TypeError('Choice.value must be callable.')
    #     [func_to_run() for func_to_run in user_choices]

    # def ask_new_data(self) -> tuple[float, float]:
    #     """Propose to input a new value for the gas counter until the user
    #     enters a valid value that is greater or equal to the past value and
    #     return a `tuple(old_value: float, new_value: float)`.
    #     """
    #     old_val = self.get_old_data()
    #     message = f'Previous value: {old_val}, enter the new value:'
    #     new_val = text(message, validate=FloatValidator(old_val)).ask()
    #     if not isinstance(new_val, str):
    #         m = f'Cant convert {type(new_val).__name__} to float type.'
    #         raise TypeError(m)
    #     new_val = float(new_val.replace(',', '.'))
    #     return (old_val, round(new_val, 2))

    # def get_old_data(self) -> float:
    #     """Find the value that the user entered at the previous time, and then
    #     convert it to a float type. If the value cannot be converted, throw a
    #     ValueError.
    #     """
    #     value = self.find_element(self.pay_loc.text_old_value).text
    #     if float_is_valid(value):
    #         return float(value.replace(',', '.'))
    #     m = f'Old value={repr(value)}, conversion to float is not possible'
    #     raise ValueError(m)

    # def enter_payment_period(self):
    #     """Input the month and year of the current UTC time into the period
    #     field.
    #     """
    #     today_utc = dt.datetime.now(dt.UTC).date().strftime('%m.%Y')
    #     field = self.write_into(self.pay_loc.input_period, today_utc)
    #     field.send_keys(Keys.ENTER)

    def build_receipt(self) -> Receipt:
        """Sleep 2 seconds at the start, then create a pydantic model that
        contains all the information about the cost.
        """

        sleep(2)  # Receipt data are updated by script, wait 2 seconds.

        def check_price(price: str) -> float:
            """Return the float price if the price is convertible to a float."""
            price_regex = r'^[\d]+[,.]*[\d]{0,2}'
            msg = f'Price format not coincide with {price_regex} regex.'
            found = findall(price_regex, price)
            if len(found) == 0:
                raise ValueError(msg)
            return float(price.replace(',', '.').replace(' р.', ''))

        without_fees_elem = self.find_element(self.pay_loc.text_cost_without_fees)  # fmt: skip
        without_fees = without_fees_elem.get_attribute('value')
        if without_fees is None:
            msg = element_not_have_attr_value.format(location=self.pay_loc.text_cost_without_fees)  # fmt: skip
            raise AttributeError(msg)
        without_fees_float = check_price(without_fees)

        include_fees = self.find_element(self.pay_loc.text_cost_include_fees).text  # fmt: skip
        include_fees_float = check_price(include_fees)

        total_fees = self.find_element(self.pay_loc.text_total_fees).text
        total_fees_float = check_price(total_fees)

        return Receipt(
            without_fees=without_fees_float,
            include_fees=include_fees_float,
            charged_fees=total_fees_float,
        )
