from payment.config.driver.firefox import DriverFirefox
from payment.pages.base import PageBase
from payment.web_elements.button import ButtonClickable
from payment.web_elements.input import InputVisible
from payment.web_elements.item import ItemHidden
from payment.web_elements.item import ItemVisible


class PageAuthentication(PageBase):
    @property
    def form_authentication(self) -> ItemVisible:
        location = '//div[@id="authForm"]'
        return ItemVisible(location=location, driver=self.driver)

    @property
    def field_login(self) -> InputVisible:
        location = '//input[@id="Input_Login"]'
        return self.form_authentication.get_child(InputVisible, location)

    @property
    def field_password(self) -> InputVisible:
        location = '//input[@id="Input_Password"]'
        return self.form_authentication.get_child(InputVisible, location)

    @property
    def button_authenticate(self) -> ButtonClickable:
        location = '//button[@id="loginBtn"]'
        return self.form_authentication.get_child(ButtonClickable, location)

    @property
    def item_login_error(self) -> ItemHidden:
        common_element = self.field_login.get_parent(ItemHidden)
        location = '//span[contains(@class, "text-danger")]'
        return common_element.get_child(ItemHidden, location)

    @property
    def item_password_error(self) -> ItemHidden:
        common_element = self.field_password.get_parent(ItemHidden)
        location = '//span[contains(@class, "text-danger")]'
        return common_element.get_child(ItemHidden, location)


# url = 'https://lk.ric-ul.ru/'


def main():
    with DriverFirefox() as driver:
        # page_home_url = 'http://127.0.0.1:5500/hp_unauthorized/'
        # page_home = PageHome(driver=driver, url=page_home_url)
        # if not page_home.has_login_btn:
        #     return
        # page_home.login_btn.click()
        # print(driver.current_url)

        page_auth_url = 'http://127.0.0.1:5500/authorization_page/'
        page_auth = PageAuthentication(driver=driver, url=page_auth_url)
        page_auth.item_login_error.element
        ...


if __name__ == '__main__':
    main()

"""
@dataclass
class Cookie:
    name: str
    value: str
    path: str
    domain: str
    secure: bool
    httpOnly: bool
    sameSite: str | None
    expiry: int = field(default=0)

    def __post_init__(self) -> None:
        if self.sameSite == 'None':
            self.sameSite = None

    @property
    def netscape_format(self) -> str:
        s = '{domain}\t{httpOnly}\t{path}\t{secure}\t{expiry}\t{name}\t{value}'
        return s.format(
            domain=self.domain,
            httpOnly=str(self.httpOnly).upper(),
            path=self.path,
            secure=str(self.secure).upper(),
            expiry=self.expiry,
            name=self.name,
            value=self.value,
        )


with DriverFirefox() as driver:
    driver.get('https://lk.ric-ul.ru/')
    input('Continue')
    sleep(10)
    cookies = driver.get_cookies()
    file = Path('/home/devid/dev/lk_riz_site/cookies.txt')
    with file.open('a') as f:
        text = '\n'.join([Cookie(**c).netscape_format for c in cookies])
        f.write(text)
    ...
"""
