from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

from config.settings import set_new_folder_or_get_existent


# Что-бы видеть курсор (https://stackoverflow.com/a/76068212/20084479)
cursor_script = '''
var cursor = document.createElement('div');
cursor.style.position = 'absolute';
cursor.style.zIndex = '9999';
cursor.style.width = '5px';
cursor.style.height = '5px';
cursor.style.borderRadius = '50%';
cursor.style.backgroundColor = 'red';
cursor.style.pointerEvents = 'none';
document.body.appendChild(cursor);

document.addEventListener('mousemove', function(e) {
  cursor.style.left = e.pageX - 5 + 'px';
  cursor.style.top = e.pageY - 5 + 'px';
});
'''


options = Options()
# Профиль.
options.add_argument('--profile')
options.add_argument(set_new_folder_or_get_existent('firefox_profile'))
# Папка download.
download_dir = set_new_folder_or_get_existent('firefox_download')
options.set_preference('browser.download.dir', download_dir)
options.set_preference('browser.download.folderList', 2)
# Панель разработчика.
options.add_argument('--devtools')
# Размер окна.
options.add_argument('--width=1920')
options.add_argument('--height=1080')
# Установка драйвера.
service = Service(GeckoDriverManager().install())
driver = Firefox(options=options, service=service)


driver.get('https://practice.expandtesting.com/download')
driver.execute_script(cursor_script)
ac = ActionChains(driver)
downloads = driver.find_elements('xpath', '//a[@download=""]')
ac.move_to_element(downloads[0]).click().perform()
