import datetime as dt
from re import findall
from time import sleep
from typing import NamedTuple

from pydantic import BaseModel
from questionary import Choice
from questionary import confirm
from questionary import print as q_print
from questionary import text
from selenium.webdriver import Keys
from selenium.webdriver.remote.webelement import WebElement

from payment.config.profile import UserProfile
from payment.pages.base import BasePage
from payment.utils import FloatValidator
from payment.utils import float_is_valid
from payment.utils import multi_choice
from payment.utils import single_choice


element_not_have_attr_value = 'The DOM element {location} has no attribute \'value\'.'  # fmt: skip
choice_value_not_callable = 'Choice.value must be callable.'


class Receipt(BaseModel):
    without_fees: float
    include_fees: float
    charged_fees: float


class GasPayLocator(NamedTuple):
    # authorization with account number;
    card_location: str
    input_account: str
    button_confirm: str
    text_check_account: str
    # input new gas values;
    text_old_value: str
    input_period: str
    available_rates: str
    input_new_gas_val: str
    button_make_calc: str
    # payment process;
    text_cost_without_fees: str
    text_cost_include_fees: str
    text_total_fees: str
    button_add_to_cart: str


class GasPayPage(BasePage):
    loc = GasPayLocator(
        # authorization with account number;
        card_location='//b[text()=\'ООО "Газпром межрегионгаз Ульяновск"\']',
        input_account='//input[@id="group-1-field-0-value"]',
        button_confirm='//button[text()="Проверить"]',
        text_check_account='//b[@class="account-header-number"]',
        # input new gas values;
        text_old_value='//td[contains(@class, "pay-gazul-old")]',
        input_period='//input[@id="DatePeriod"]',
        available_rates='//ul[@class="pay-gazul-rate-list"]//span',
        input_new_gas_val='//input[contains(@class, "newReading")]',
        button_make_calc='//a[@id="calcButton"]',
        # payment process;
        text_cost_without_fees='//input[@id="totalAmount"]',
        text_cost_include_fees='//b[@id="labelTotalSummComm"]',
        text_total_fees='//p[@class="payment-bottom-total-commission"]//span',
        button_add_to_cart='//*[contains(@class, "add-to-cart-btn")]',
    )

    def pay_gas(self, profile: UserProfile) -> bool:
        self.click_button(self.loc.card_location)
        self.enter_gas_account_number(profile)
        if self.skip_input(profile) is True:
            return True
        self.enter_payment_period()
        self.choice_rate()
        self.enter_new_gas_value()
        self.run_payment_process()
        return False

    def enter_gas_account_number(self, profile: UserProfile):
        """Enter the gas account number of the user, press confirm, and check
        if the authorization has been passed correctly.
        """
        self.write_into(self.loc.input_account, profile.gas_account)
        self.click_button(self.loc.button_confirm)
        # Ensure that the account number on the next page corresponds with the
        # one in the profile.
        used_account = self.find_element(self.loc.text_check_account).text
        assert used_account.replace('ЛС № ', '') == profile.gas_account

    def skip_input(self, profile: UserProfile) -> bool:
        """If the service is already in the cart, the client can choose to skip
        the process of entering new gas data, then function return True, also
        client can remove service from cart, and enter new data, then function
        return False and finally if the service not in cart function return
        False.
        """
        page_url = self.driver.current_url
        add_to_cart_button = self.find_element(self.loc.button_add_to_cart)
        if add_to_cart_button.text == 'Добавить в корзину':
            return False

        msg = 'This service was earlier added into the cart, remove it?'
        resp = confirm(msg).ask()
        if resp is False:
            return True

        self.remove_service_from_cart()
        self.driver.get(page_url)
        self.enter_gas_account_number(profile)
        return False

    def enter_payment_period(self):
        """Input the month and year of the current UTC time into the period
        field.
        """
        today_utc = dt.datetime.now(dt.UTC).date().strftime('%m.%Y')
        self.write_into(self.loc.input_period, today_utc).send_keys(Keys.ENTER)

    def choice_rate(self):
        """Choose the single rate from the list of rates offered."""
        rates = self.find_elements(self.loc.available_rates)
        message = 'Choose the rate for calculating gas prices:'
        choices = [Choice(r.text, r) for r in rates]
        choice = single_choice(message, choices=choices).ask()
        if not isinstance(choice, WebElement):
            m = f'Choice.value must be WebElement not {type(choice).__name__}'
            raise TypeError(m)  # fmt: skip
        choice.click()

    def enter_new_gas_value(self):
        """Ask the user to provide the new value of the gas counter, and write
        it into the field.
        """
        old_val, new_val = self.ask_new_gas_data()
        self.write_into(self.loc.input_new_gas_val, str(new_val))
        diff = round(new_val, 2) - round(old_val, 2)
        msg = f'Total volume of gas expended: {diff} m2, confirm?'
        resp = confirm(msg).ask()
        if resp is False:
            self.edit_form_values()
        self.click_button(self.loc.button_make_calc)

    def run_payment_process(self):
        """Inform the customer of the payment amount. If the client wants to
        add this service to the cart, click the button 'Add to Cart'.
        """
        total_to_pay = self.build_receipt().include_fees
        msg = f'Total to pay: {total_to_pay}₽, add this service into the cart?'
        resp = confirm(msg).ask()
        if resp is False:
            # TODO WHAT TO DO IF CLIENT DOES NOT WANT TO ADD SERVICE INTO THE CART?
            msg = 'At this time, this choice has not been realized. Please wait for updates.'  # fmt: skip
            q_print(msg, style='bold italic fg:yellow')

        add_to_cart_button = self.find_element(self.loc.button_add_to_cart)
        add_to_cart_button.click()
        msg = 'The gas service is added into the cart successful!'
        q_print(msg, style='bold fg:green')

    def ask_new_gas_data(self) -> tuple[float, float]:
        """Propose to input a new value for the gas counter until the user
        enters a valid value that is greater or equal to the past value and
        return a `tuple(old_value: float, new_value: float)`.
        """
        old_val = self.get_old_gas_data()
        message = f'Previous gas value: {old_val}, enter the new value:'
        new_val = text(message, validate=FloatValidator(old_val)).ask()
        if not isinstance(new_val, str):
            m = f'Cant convert {type(new_val).__name__} to float type.'
            raise TypeError(m)
        new_val = float(new_val.replace(',', '.'))
        return (old_val, round(new_val, 2))

    def get_old_gas_data(self) -> float:
        """Find the value that the user entered at the previous time, and then
        convert it to a float type. If the value cannot be converted, throw a
        ValueError.
        """
        value = self.find_element(self.loc.text_old_value).text
        if float_is_valid(value):
            return float(value.replace(',', '.'))
        m = f'Old gas_value={repr(value)}, conversion to float is not possible'
        raise ValueError(m)

    def edit_form_values(self):
        """Provide a list of methods, that users can select to change already
        existing values, and execute all methods selected by the user.
        """
        choices = [
            Choice('change rate', self.choice_rate),
            Choice('change gas value', self.enter_new_gas_value),
        ]
        user_choices = multi_choice('What you want to change?', choices).ask()
        if not all(map(lambda f: callable(f), user_choices)):
            raise TypeError(choice_value_not_callable)
        [func_to_run() for func_to_run in user_choices]

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

        without_fees_elem = self.find_element(self.loc.text_cost_without_fees)
        without_fees = without_fees_elem.get_attribute('value')
        if without_fees is None:
            msg = element_not_have_attr_value.format(location=self.loc.text_cost_without_fees)  # fmt: skip
            raise AttributeError(msg)
        without_fees_float = check_price(without_fees)

        include_fees = self.find_element(self.loc.text_cost_include_fees).text
        include_fees_float = check_price(include_fees)

        total_fees = self.find_element(self.loc.text_total_fees).text
        total_fees_float = check_price(total_fees)

        return Receipt(
            without_fees=without_fees_float,
            include_fees=include_fees_float,
            charged_fees=total_fees_float,
        )
