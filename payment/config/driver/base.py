from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait


class DriverBase(WebDriver):
    @property
    def action_chains(self) -> ActionChains:
        return ActionChains(self)

    @property
    def driver_wait(self) -> WebDriverWait:
        return WebDriverWait(driver=self, timeout=3, poll_frequency=0.2)
