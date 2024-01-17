from dataclasses import dataclass
from typing import NamedTuple

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
    locators = AuthenticationLocators(
        button_login='//a[@class="profile-login-btn"]',
        input_login='//input[@id="Input_Login"]',
        input_password='//input[@id="Input_Password"]',
        button_authenticate='//button[@id="loginBtn"]',
        invalid_auth='//div[@class="alert alert-danger"]',
    )

    def enter_auth_data(self, profile: UserProfile) -> None:
        """Enter the authentication data (login and password) into the
        authentication form.
        """
        self.write_into(self.locators.input_login, profile.login)
        self.write_into(self.locators.input_password, profile.password)

    def authenticate(self, profile: UserProfile) -> bool:
        """Run the authentication process and return True if authentication is
        successful else False.
        """
        self.click_button(self.locators.button_login)
        self.enter_auth_data(profile)

        url_before = self.driver.current_url
        self.click_button(self.locators.button_authenticate)
        url_after = self.driver.current_url

        if url_before != url_after:
            return True
        else:
            element = self.find_element(self.locators.invalid_auth)
            print(element.text)
            return False
