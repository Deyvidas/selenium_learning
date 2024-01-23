from dataclasses import dataclass
from time import sleep
from typing import NamedTuple

from questionary import print as q_print
from selenium.webdriver.remote.webelement import WebElement

from payment.config.user_profile import UserProfile
from payment.pages_past.base import BaseDriver


class AuthenticationLocators(NamedTuple):
    button_login: str
    input_login: str
    input_password: str
    button_authenticate: str
    invalid_auth: str


@dataclass(kw_only=True)
class AuthenticationPage(BaseDriver):
    loc = AuthenticationLocators(
        button_login='//a[@class="profile-login-btn"]',
        input_login='//input[@id="Input_Login"]',
        input_password='//input[@id="Input_Password"]',
        button_authenticate='//button[@id="loginBtn"]',
        invalid_auth='//div[@class="alert alert-danger"]',
    )

    def authenticate(self, profile: UserProfile) -> bool:
        """Run the authentication process and return True if authentication is
        successful, else False.
        """
        self.click_button(self.loc.button_login)
        self.enter_auth_data(profile)

        self.click_button(self.loc.button_authenticate)
        sleep(2)
        cookies = self.driver.get_cookies()
        cookies_ = [c for c in cookies if c['secure'] is True]

        if len(cookies_) > 1:
            msg = 'The authentication was successful!'
            q_print(msg, style='bold fg:green')
            return True
        element = self.find_element(self.loc.invalid_auth)
        q_print(element.text, 'bold fg:red')
        return False

    def enter_auth_data(self, profile: UserProfile) -> WebElement:
        """Enter the authentication data (login and password) into the
        authentication form and return the latest filled field.
        """
        self.write_into(self.loc.input_login, profile.login)
        return self.write_into(self.loc.input_password, profile.password)
