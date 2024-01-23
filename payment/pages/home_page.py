from payment.pages.base import PageBase
from payment.pages.exceptions import ErrorPageCantFindElement
from payment.web_elements.button import ButtonClickable
from payment.web_elements.item import ItemVisible


class PageHome(PageBase):
    @property
    def profile(self) -> ItemVisible:
        location = '(//div[contains(@class, "profile")])[1]'
        return ItemVisible(location=location, driver=self.driver)

    @property
    def has_login_btn(self) -> bool:
        return 'profile-login' in self.profile.get_html_attr('class')

    @property
    def login_btn(self) -> ButtonClickable:
        location = '//a[@class="profile-login-btn"]'
        if self.has_login_btn:
            return self.profile.get_child(ButtonClickable, location)
        msg = 'Cant find the login button, because user is already authenticated.'
        raise ErrorPageCantFindElement(url=self.url, location=location, details=msg)  # fmt: skip
