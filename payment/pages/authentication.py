from dataclasses import dataclass
from typing import NamedTuple

from selenium.webdriver.remote.webelement import WebElement

from payment.base import BasePage
from payment.config.profile import UserProfile


class AuthenticationLocators(NamedTuple):
    button_login: str
    input_login: str
    input_password: str
    button_authenticate: str
    invalid_auth: str


@dataclass(kw_only=True)
class AuthenticationPage(BasePage):
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

        url_before = self.driver.current_url
        self.click_button(self.loc.button_authenticate)
        url_after = self.driver.current_url

        if url_before != url_after:
            self.print_success('The authentication was successful!')
            return True
        element = self.find_element(self.loc.invalid_auth)
        print(element.text)
        return False

    def enter_auth_data(self, profile: UserProfile) -> WebElement:
        """Enter the authentication data (login and password) into the
        authentication form and return the latest filled field.
        """
        self.write_into(self.loc.input_login, profile.login)
        return self.write_into(self.loc.input_password, profile.password)
