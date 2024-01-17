from selenium.webdriver.common.action_chains import ActionChains

from lesson02.geckodriver import cursor_script
from lesson02.geckodriver import driver


driver.get('https://practice.expandtesting.com/form-validation')
driver.execute_script(cursor_script)  # Для отображения движения курсора.
ac = ActionChains(driver)


# Вбиваем имя.
name = driver.find_element('xpath', '//input[@name="ContactName"]')
name.clear()
ac.send_keys_to_element(name, 'Pythonist').perform()
assert name.get_attribute('value') == 'Pythonist'

# Вбиваем номер телефона.
number = driver.find_element('xpath', '//input[@name="contactnumber"]')
number.clear()
ac.send_keys_to_element(number, '012-3456789').perform()
assert number.get_attribute('value') == '012-3456789'

# Выбираем удобную дату доставки.
pickup_date = driver.find_element('xpath', '//input[@name="pickupdate"]')
pickup_date.clear()
ac.send_keys_to_element(pickup_date, '12282024').perform()
assert pickup_date.get_attribute('value') == '2024-12-28'

# Выбираем удобный способ оплаты.
payment = driver.find_element('xpath', '//select[@name="payment"]')
cash = driver.find_element('xpath', '//option[@value="cashondelivery"]')
card = driver.find_element('xpath', '//option[@value="card"]')
cash.click()
assert payment.get_attribute('value') == 'cashondelivery'

# Наводимся на кнопку и жмякаем.
register_button = driver.find_element('xpath', '//button[text()=" Register "]')
(
    ac.move_to_element(register_button)
    .move_by_offset(0, 99)
    .move_by_offset(-99, -99)
    .move_by_offset(99, -99)
    .move_by_offset(99, 99)
    .move_by_offset(-99, 99)
    .move_by_offset(0, -99)
    .click()
    .perform()
)
