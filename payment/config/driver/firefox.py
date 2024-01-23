from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager

from payment.config import CONFIG_DIR
from payment.config.driver.base import DriverBase


class DriverFirefox(DriverBase, WebDriver):
    def __init__(self):
        super().__init__(
            options=self.options,
            service=Service(executable_path=GeckoDriverManager().install()),
            keep_alive=True,
        )

    @property
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
    def profile_dir(self) -> str:
        profile_root = CONFIG_DIR / 'firefox_profile'
        if not profile_root.exists():
            profile_root.mkdir()

        gitignore = profile_root / '.gitignore'
        if not gitignore.exists() or gitignore.read_text() != '*':
            gitignore.write_text('*')

        return str(profile_root)
