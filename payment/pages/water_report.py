from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

from selenium.common import NoSuchAttributeException

from payment.base import BasePage
from payment.config.profile import UserProfile
from payment.utils import is_float


send_report_failed = (
    'In the time of sending the report of water, something went wrong.'
)


class Water(str, Enum):
    hot = 'hot'
    cold = 'cold'


class WaterReportLocators(NamedTuple):
    # authorization with account number;
    card_report: str
    flag_use_account: str
    input_account: str
    button_confirm: str
    text_check_account: str
    # input new water values;
    block_old_hot: str
    block_old_cold: str
    input_hot: str
    diff_hot: str
    input_cold: str
    diff_cold: str
    button_send_report: str
    text_report_success: str
    button_close_result: str


@dataclass(kw_only=True)
class WaterReportPage(BasePage):
    loc = WaterReportLocators(
        # authorization with account number;
        card_report='//b[text()="Ввод показаний ЖКУ"]',
        flag_use_account='//span[text()="По лицевому счету"]',
        input_account='//input[@id="AccountNumberValue"]',
        button_confirm='//button[text()="Проверить"]',
        text_check_account='//p[text()="Лицевой счет: "]/b',
        # input new water values;
        block_old_hot='(//div[@class="indication-table-last-indic"])[1]',
        input_hot='(//input[contains(@class, "new-indication")])[1]',
        diff_hot='(//input[contains(@class, "sum-indication")])[1]',
        block_old_cold='(//div[@class="indication-table-last-indic"])[2]',
        input_cold='(//input[contains(@class, "new-indication")])[2]',
        diff_cold='(//input[contains(@class, "sum-indication")])[2]',
        button_send_report='//button[text()="Отправить показания"]',
        text_report_success='//span[@class="ok-result"]',
        button_close_result='//button[text()="ОК"]',  # 'OK' on cyrillic.
    )

    def send_report(self, profile: UserProfile) -> bool:
        """Run the process of reporting of water meters and return True if it
        is successful, else False.
        """
        self.click_button(self.loc.card_report)
        self.enter_water_account_number(profile)
        self.enter_water_data(
            block_old=self.loc.block_old_hot,
            input_=self.loc.input_hot,
            diff=self.loc.diff_hot,
            water=Water.hot,
        )
        self.enter_water_data(
            block_old=self.loc.block_old_cold,
            input_=self.loc.input_cold,
            diff=self.loc.diff_cold,
            water=Water.cold,
        )
        self.click_button(self.loc.button_send_report)

        elements = self.find_elements(self.loc.text_report_success)
        self.click_button(self.loc.button_close_result)
        if len(elements) == 2:
            self.print_success('The water report was successful!')
            return True
        print(send_report_failed)
        return False

    def enter_water_account_number(self, profile: UserProfile):
        """Select authentication by account number, then input it into the
        field, press send, and check if the authorization has been passed
        correctly.
        """
        self.click_button(self.loc.flag_use_account)
        self.write_into(self.loc.input_account, profile.water_account)
        self.click_button(self.loc.button_confirm)
        # Ensure that the account number on the next page corresponds with the
        # one in the profile.
        used_account = self.find_element(self.loc.text_check_account).text
        assert used_account == profile.water_account

    def enter_water_data(
        self, block_old: str, input_: str, diff: str, water: Water
    ):
        """Ask and enter into the fields, the new values of the water counter,
        that the user has entered.
        """
        old_val, new_val = self.ask_new_water_data(block_old, water)
        self.write_into(input_, str(new_val))
        self.find_element(diff)
        print(f'Consumed {water.value} water {round(new_val - old_val, 3)}.')

        msg = 'Press ENTER to confirm or TYPE SOME to change passed data.'
        res = input(msg)
        if len(res) != 0:
            print()
            self.enter_water_data(block_old, input_, diff, water)
        print()

    def ask_new_water_data(
        self, locator: str, water: Water
    ) -> tuple[float, float]:
        """Propose to input a new value for the water counter until the user
        enters a valid value that is greater or equal to the past value and
        return a `tuple(old_value: float, new_value: float)`.
        """
        value, date = self.get_old_water_data(locator)
        print(f'{water.value.capitalize()}: {date} -> {value}')
        message = f'New value of {water.value.upper()} water:\n>>> '
        new = input(message).replace(',', '.')
        while not is_float(new) or float(new) < float(value):
            new = input(message).replace(',', '.')
        return (value, float(new))

    def get_old_water_data(self, locator: str) -> tuple[float, str]:
        """Find the value that the user entered at the previous time and the
        date of the previous report.
        """
        block = self.find_element(locator)

        date = self.find_child('.//label', block).text
        if len(date) == 0:
            raise ValueError(f'{locator}.//label return an empty string.')

        value = self.find_child('.//input', block).get_attribute('value')
        if value is None:
            raise NoSuchAttributeException(f'{locator}.//input has not attribute \'value\'.')  # type: ignore
        elif not is_float(value):
            raise ValueError(f'Cant convert {value} into the float type.')

        return (float(value.replace(',', '.')), date)
