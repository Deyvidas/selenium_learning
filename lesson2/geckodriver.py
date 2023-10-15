from selenium import webdriver
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

# Настройка браузера перед запуском.
options = Options()

# --devtools -> Open DevTools on initial load (запуск с панелью разработки).
options.add_argument('--devtools')

# --width=<int> --height=<int> указать какого размера должно быть окно
# браузера при его запуске (данный способ предпочтительнее).
options.add_argument('--width=1920')
options.add_argument('--height=1080')

# Загрузка профиля firefox или создание нового. Профиль нужен для хранения
# настроек, закладок, паролей, ... (профиль необходим даже в режиме private!)
options.add_argument('--profile')
options.add_argument(set_new_folder_or_get_existent('firefox_profile'))

service = Service(executable_path=GeckoDriverManager().install())
driver = webdriver.Firefox(options=options, service=service)
