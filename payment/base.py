from dataclasses import dataclass
from dataclasses import field

from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


element_not_found = (
    '{name}(url={url}).find_element(location={location}) cant find element.'
)


@dataclass(kw_only=True)
class BasePage:
    url: str
    driver: WebDriver
    action_chains: ActionChains = field(init=False)
    driver_wait: WebDriverWait = field(init=False)

    def __post_init__(self) -> None:
        self.action_chains = ActionChains(self.driver)
        self.driver_wait = WebDriverWait(
            driver=self.driver,
            timeout=10,
            poll_frequency=2,
        )
        self.driver.get(self.url)

    def find_element(self, location: str) -> WebElement:
        locator = ('xpath', location)
        element = expected_conditions.presence_of_element_located(locator)
        msg = element_not_found.format(
            name=type(self).__name__,
            url=self.url,
            location=location,
        )
        return self.driver_wait.until(element, message=msg)

    def write_into(self, location: str, string: str) -> None:
        field = self.find_element(location)
        field.clear()
        field.send_keys(string)

    def click_button(self, location: str) -> None:
        self.find_element(location).click()
