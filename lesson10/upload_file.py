from selenium.webdriver.common.action_chains import ActionChains

from config.settings import set_new_folder_or_get_existent
from lesson02.geckodriver import cursor_script
from lesson02.geckodriver import driver


path = set_new_folder_or_get_existent('lesson10') + '/' + 'image_to_upload.png'
driver.get('https://practice.expandtesting.com/upload')
driver.execute_script(cursor_script)
ac = ActionChains(driver)

# Вставляем картинку в поле.
upload_field = driver.find_element('xpath', '//input[@type="file"]')
upload_field.send_keys(path)

# Жмякаем кнопку upload
upload_button = driver.find_element(
    'xpath', '//button[@type="submit" and text()="Upload"]'
)
ac.move_to_element(upload_button).click().perform()
