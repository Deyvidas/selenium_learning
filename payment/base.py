from dataclasses import dataclass
from dataclasses import field

from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


more_that_one_found = '{name}(url={url}).find_element(location={location}) found multiple elements.'
elements_not_found = '{name}(url={url}).find_elements(location={location}) can\'t find elements.'


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

    def find_child(self, location: str, parent: WebElement) -> WebElement:
        locator = ('xpath', location)
        element = parent.find_element(*locator)
        return element

    def write_into(self, location: str, string: str) -> WebElement:
        field = self.find_element(location)
        field.clear()
        field.send_keys(string)
        return field

    def click_button(self, location: str) -> None:
        self.find_element(location).click()

    def find_element(self, location: str) -> WebElement:
        element = self.find_elements(location)
        if len(element) == 1:
            return element[0]
        msg = more_that_one_found.format(
            name=type(self).__name__,
            url=self.url,
            location=location,
        )
        raise ValueError(msg)

    def find_elements(self, location: str) -> list[WebElement]:
        loc = ('xpath', location)
        elements = expected_conditions.presence_of_all_elements_located(loc)
        msg = elements_not_found.format(
            name=type(self).__name__,
            url=self.url,
            location=location,
        )
        return self.driver_wait.until(elements, message=msg)

    def print_success(self, message: str) -> None:
        print('+' * 100)
        print('{:+^100}'.format(f' {message} '))
        print('+' * 100)
