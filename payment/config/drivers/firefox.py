from typing import override

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager

from payment.config import CONFIG_DIR
from payment.config.drivers.abstract import AbstractDriver


class FirefoxDriver(AbstractDriver[WebDriver, Options, Service]):
    @property
    @override
    def driver(self) -> WebDriver:
        return WebDriver(options=self.options, service=self.service)

    @property
    @override
    def options(self) -> Options:
        options = Options()
        options.add_argument('--private-window')
        options.add_argument('--devtools')
        options.add_argument('--width=1920')
        options.add_argument('--height=1080')
        options.add_argument('--profile')
        options.add_argument(self.profile_dir)
        return options

    @property
    @override
    def service(self) -> Service:
        return Service(executable_path=GeckoDriverManager().install())

    @property
    def profile_dir(self) -> str:
        profile_root = CONFIG_DIR / 'firefox_profile'
        if not profile_root.exists():
            profile_root.mkdir()

        gitignore = profile_root / '.gitignore'
        if not gitignore.exists() or gitignore.read_text() != '*':
            gitignore.write_text('*')

        return str(profile_root)


firefox_driver = FirefoxDriver().driver
