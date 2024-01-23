from typing import NamedTuple
from typing import override

from pydantic import BaseModel
from questionary import Choice
from selenium.webdriver.remote.webelement import WebElement

from payment.pages_past.base import BasePage
from payment.utils import single_choice


element_not_have_attr_value = 'The DOM element {location} has no attribute \'value\'.'  # fmt: skip
choice_value_not_callable = 'Choice.value must be callable.'


class Receipt(BaseModel):
    without_fees: float
    include_fees: float
    charged_fees: float


class GasPayLocator(NamedTuple):
    available_rates: str


class GasPayPage(BasePage):
    loc = GasPayLocator(
        available_rates='//ul[@class="pay-gazul-rate-list"]//span',
    )

    @override
    def step_authorization(self):
        self.click_service_card()
        self.input_account_number()
        self.click_check_account()

    @override
    def step_collect_old_values(self):
        old = self.get_old_data()
        new = self.ask_new_data(old)
        self.input_new_value(new, old)

    @property
    @override
    def user_can_change(self) -> list[Choice]:
        new = [
            Choice('change selected rate', self.choice_rate),
        ]
        return super().user_can_change + new

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
