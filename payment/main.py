from typing import override

from payment.config.driver.firefox import DriverFirefox
from payment.config.user_profile import user_profile as _profile
from payment.pages_past.authentication import AuthenticationPage
from payment.pages_past.base import BasePage
from payment.pages_past.base import pay_locator


class EnergyPayPage(BasePage):
    pay_loc = pay_locator._replace(
        input_period='//input[@id="group-1-field-1-value"]',
    )

    @override
    def step_authorization(self):
        self.click_service_card()
        self.input_account_number()
        self.input_payment_period()
        self.click_check_account()

    @override
    def step_collect_old_values(self):
        old = self.get_old_data()
        new = self.ask_new_data(old)
        self.input_new_value(new, old)


def main():
    with DriverFirefox() as driver:
        url = 'https://lk.ric-ul.ru/'
        auth = AuthenticationPage(url=_profile.auth_url, driver=driver)
        auth.authenticate(_profile)

        # water_report = WaterReportPage(url=url, driver=driver)
        # water_report.send_report(profile)

        # GasPayPage(
        #     url=url,
        #     driver=driver,
        #     account_number=_profile.gas_account,
        #     service_name='Газпром межрегионгаз (Ульяновская обл.)',
        #     service_card='ООО "Газпром межрегионгаз Ульяновск"',
        # ).run()

        # EnergyPayPage(
        #     url=url,
        #     driver=driver,
        #     account_number=_profile.energy_account,
        #     service_name='АО "Ульяновскэнерго"',
        #     service_card='АО "Ульяновскэнерго"',
        # ).run()


if __name__ == '__main__':
    main()
