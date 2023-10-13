from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from webdriver_manager.firefox import GeckoDriverManager

from config.settings import firefox_profile_folder

options = Options()
options.add_argument('--profile')
options.add_argument(firefox_profile_folder())
service = Service(executable_path=GeckoDriverManager().install())
driver = webdriver.Firefox(options=options, service=service)
