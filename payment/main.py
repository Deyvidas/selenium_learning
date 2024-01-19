from payment.config.drivers import firefox_driver as driver
from payment.config.profile import user_profile as profile
from payment.pages.authentication import AuthenticationPage
from payment.pages.gas_payment import GasPayPage
from payment.pages.water_report import WaterReportPage


def main():
    auth = AuthenticationPage(url=profile.auth_url, driver=driver)
    auth.authenticate(profile)

    water_report = WaterReportPage(url='https://lk.ric-ul.ru/', driver=driver)
    water_report.send_report(profile)

    gas_pay = GasPayPage(url='https://lk.ric-ul.ru/', driver=driver)
    gas_pay.pay_gas(profile)


if __name__ == '__main__':
    main()
