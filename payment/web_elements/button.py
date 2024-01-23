from payment.web_elements.base import ElementBase
from payment.web_elements.base import ElementClickable


class ButtonBase(ElementBase):
    @property
    def href(self) -> str | None:
        self.raise_if_stub()
        return self.element.get_attribute('href')


class ButtonClickable(ElementClickable, ButtonBase):
    def click(self) -> None:
        self.raise_if_stub()
        click_script = 'arguments[0].click();'
        self.driver.execute_script(click_script, self.element)
