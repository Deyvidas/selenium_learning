from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from webdriver_manager.firefox import GeckoDriverManager

from config.settings import firefox_profile_folder


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
options.add_argument('--profile')
options.add_argument(firefox_profile_folder())
service = Service(executable_path=GeckoDriverManager().install())
driver = webdriver.Firefox(options=options, service=service)
