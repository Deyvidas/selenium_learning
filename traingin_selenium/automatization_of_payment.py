import os
import platform
import re
import time

from datetime import date

from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from webdriver_manager.firefox import GeckoDriverManager

from config.settings import set_new_folder_or_get_existent


HOME_PAGE = 'https://lk.ric-ul.ru/'
RIZ_LOGIN = os.getenv('RIZ_LOGIN')
RIZ_PASSWORD = os.getenv('RIZ_PASSWORD')
SEND_TO_EMAIL = os.getenv('SEND_TO_EMAIL')
WATER_ACCOUNT_NUM = os.getenv('WATER_ACCOUNT_NUM')      # ЛC воды.
REPAIR_ACCOUNT_NUM = os.getenv('REPAIR_ACCOUNT_NUM')    # ЛC кап. ремонта.
HEATING_ACCOUNT_NUM = os.getenv('HEATING_ACCOUNT_NUM')  # ЛC отопления.
GAS_ACCOUNT_NUM = os.getenv('GAS_ACCOUNT_NUM')          # ЛC газа.
ENERGY_ACCOUNT_NUM = os.getenv('ENERGY_ACCOUNT_NUM')    # ЛC электроэнергии.

# =============================================================================
# Настройка браузера перед запуском.
# =============================================================================


options = Options()
options.add_argument('--private-window')
options.add_argument('--devtools')
options.add_argument('--width=1920')
options.add_argument('--height=1080')
options.add_argument('--profile')
options.add_argument(set_new_folder_or_get_existent('firefox_profile'))

service = Service(executable_path=GeckoDriverManager().install())
driver = Firefox(options=options, service=service)


driver.get(HOME_PAGE)
ac = ActionChains(driver)
driver_wait = WebDriverWait(driver=driver, timeout=10, poll_frequency=2)


# =============================================================================
# Вспомогательные функции.
# =============================================================================


def check_added_service_in_basket(service_name: str):
    driver.get('https://lk.ric-ul.ru/Basket')
    SERVICE_NAME = ('xpath', f'//*[contains(text(), \'{service_name}\')]')
    elements = driver.find_elements(*SERVICE_NAME)
    if elements == list():
        assert False, f'Услуги `{service_name}` нет в корзине.'
    driver.get(HOME_PAGE)


def clear_field(field):
    select_all = Keys.CONTROL + 'a'
    # Если ОС пользователя Mac то вместо Ctrl нажимаем Command.
    if platform.system() == 'Darwin':
        select_all = Keys.COMMAND + 'a'
    field.send_keys(select_all + Keys.BACKSPACE)


def click_button_with_text(button_text: str):
    # Находим кнопку с текстом `button_text` и нажимаем на неё.
    BUTTON = ('xpath', f'//button[text()=\'{button_text}\']')
    button = driver_wait.until(EC.element_to_be_clickable(BUTTON))
    button.click()


def click_card_with_text(text: str):
    # Находим карточку с текстом `text` ждем её кликабельность и кликаем её.
    CARD = ('xpath', f'//b[text()=\'{text}\']')
    card = driver_wait.until(EC.visibility_of_element_located(CARD))
    card.click()


def click_href_with_attribute(id_value: str):
    HREF = ('xpath', f'//a[@id=\'{id_value}\']')
    driver_wait.until(EC.visibility_of_element_located(HREF)).click()


def convert_string_to_number(regex: str, value: str) -> int | float:
    input_valid = bool(re.fullmatch(regex, value))
    to_number_func = int
    if input_valid is False:
        print(f'Введенное значение `{value}` не прошло валидацию.')
        return 0
    elif '.' in value:
        to_number_func = float
    return to_number_func(value)


def get_element_text(element_xpath: str):
    ELEMENT = ('xpath', element_xpath)
    element = driver_wait.until(EC.visibility_of_element_located(ELEMENT))
    return element.text


def get_service_name() -> str:
    # Ищем скрытое поле в котором хранится название оплачиваемого сервиса.
    SERVICE_NAME_FIELD = ('xpath', '//input[@id="serviceName"]')
    service_name_field = driver_wait.until(
        EC.presence_of_element_located(SERVICE_NAME_FIELD)
    )
    return service_name_field.get_attribute('value')


def select_checkbox_with_text(text: str):
    # Находим чекбокс с `text()={text}`.
    CHECKBOX_CHECK = ('xpath', f'//span[text()=\'{text}\']/../input')
    CHECKBOX_CLICK = ('xpath', f'//span[text()=\'{text}\']')
    checkbox_check = driver_wait.until(
        EC.presence_of_element_located(CHECKBOX_CHECK)
    )
    checkbox_click = driver_wait.until(
        EC.visibility_of_element_located(CHECKBOX_CLICK)
    )
    # Если чекбокс с `text()={text}` не выбрана, то выбираем её.
    if checkbox_check.is_selected() is not True:
        checkbox_click.click()
    # Проверяем выбран ли необходимый чекбокс.
    checkbox_check = driver_wait.until(
        EC.presence_of_element_located(CHECKBOX_CHECK)
    )
    assert checkbox_check.is_selected()


def type_value_in_input_with_attr(
        attr_name: str,
        attr_value: str,
        field_value: str,
):
    # Находим поле с атрибутом `{attr_name}="{attr_value}"`.
    FIELD = ('xpath', f'//input[@{attr_name}=\'{attr_value}\']')
    field = driver_wait.until(EC.element_to_be_clickable(FIELD))
    # Очищаем поле и вводим в него значение `field_value`.
    clear_field(field)
    field.click()
    field.send_keys(field_value)
    # Убеждаемся в том, что переданное значение введено корректно.
    assert driver_wait.until(
        EC.text_to_be_present_in_element_value(FIELD, field_value)
    )


# =============================================================================
# АВТОРИЗАЦИЯ.
# =============================================================================


def click_to_authentication_button():
    # Находим кнопку авторизации и нажимаем на неё.
    AUTH_BUTTON = ('xpath', '//a[@class="profile-login-btn"]')
    driver_wait.until(EC.presence_of_element_located(AUTH_BUTTON)).click()


click_to_authentication_button()
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='Input_Login',
    field_value=RIZ_LOGIN,
)
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='Input_Password',
    field_value=RIZ_PASSWORD
)
ac.send_keys(Keys.ENTER).perform()
print('*' * 5, 'Авторизация прошла успешно!', '*' * 5)


# =============================================================================
# ВВОД ПОКАЗАНИИ СЧЕТЧИКОВ ВОДЫ.
# =============================================================================


def set_new_water_data():
    # Получаем два элемента счетчика первый `ГВС`, второй `ХВС`.
    INDICATORS = ('xpath', '//div[@class="indication-table-body"]')
    indicators = driver_wait.until(
        EC.visibility_of_all_elements_located(INDICATORS)
    )
    for indicator in indicators:
        # Последний переданный показатель счетчика в цифрах `99.999`.
        LAST_VALUE = ('xpath', './/input[@readonly="readonly"]')
        last_value = indicator.find_element(*LAST_VALUE).get_attribute('value')
        last_value = float(last_value)

        # Tип счетчика `ГВС` или `ХВС`.
        INDICATOR = ('xpath', './/div[@class="indication-table-type"]')
        _indicator = indicator.find_element(*INDICATOR).text

        # Просим ввести новые показатели воды и преобразовываем в число.
        new_value = 0
        while new_value <= last_value:
            print(f'Введите показатель {_indicator}, БОЛЬШЕ чем {last_value}.')
            new_value = input('Новое показание: ')
            new_value = convert_string_to_number(
                regex=r'[\d]*[.]?[\d]{1,3}',
                value=new_value,
            )

        # Вводим введенные пользователем значения в поля
        INPUT_FIELD = ('xpath', './/input[contains(@class, "new-indication")]')
        input_field = indicator.find_element(*INPUT_FIELD)
        input_field.send_keys(new_value)
        assert input_field.get_attribute('value') == str(new_value)


# Находим карточку `Ввод показаний ЖКУ` и кликаем на нее.
click_card_with_text('Ввод показаний ЖКУ')
# Выбираем передачу `По лицевому счету`.
select_checkbox_with_text('По лицевому счету')
# Вводим номер лицевого счета в поле `Номер лицевого счета`.
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='AccountNumberValue',
    field_value=WATER_ACCOUNT_NUM,
)
# Нажимаем кнопку enter и идем дальше.
ac.send_keys(Keys.ENTER).perform()
# Запрашиваем и вводим новые показатели счетчиков.
set_new_water_data()
# Находим кнопку отправки данных и нажимаем на нее.
SEND_DATA_BUTTON_LOCATOR = ('xpath', '//button[text()="Отправить показания"]')
driver_wait.until(EC.element_to_be_clickable(SEND_DATA_BUTTON_LOCATOR)).click()
# Закрываем окно с результатом передачи данных (ОК - на кириллице).
OK_BUTTON_LOCATOR = ('xpath', '//button[@class="primary-btn" and text()="ОК"]')
driver_wait.until(EC.element_to_be_clickable(OK_BUTTON_LOCATOR)).click()
print('*' * 5, 'Новые показания счетчиков воды успешно переданы!', '*' * 5)


# =============================================================================
# ОПЛАТА ГАЗА.
# =============================================================================


driver.get(HOME_PAGE)
# Находим карточку `ПАО "Т Плюс"` и нажимаем на неё.
click_card_with_text('ООО "Газпром межрегионгаз Ульяновск"')
# Вводим номер лицевого счета.
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='group-1-field-0-value',
    field_value=GAS_ACCOUNT_NUM
)
# Нажимаем на enter и идем дальше.
ac.send_keys(Keys.ENTER).perform()
# Выберем чекбокс `Многоквартирные дома (6.81 руб./1 куб.м)` и кликнем на него.
select_checkbox_with_text('Многоквартирные дома (6.81 руб./1 куб.м)')


# Находим поле с предыдущем показанием и сохраняем его значение.
xpath = '//td[contains(@class, "pay-gazul-old")]'
last_gas_data = get_element_text(xpath)
# Преобразовываем строку в float или int.
last_gas_data = convert_string_to_number(
    regex=r'[\d]*[.]?[\d]{1,2}',
    value=last_gas_data,
)

# Запрашиваем новое показание у пользователя, проверяем переданное значение.
new_gas_data = 0
while new_gas_data <= last_gas_data:
    print(f'Введите показатель ГАЗА, БОЛЬШЕ чем {last_gas_data}.')
    new_gas_data = input('Новое показание: ')
    new_gas_data = convert_string_to_number(
        regex=r'[\d]*[.]?[\d]{1,2}',
        value=new_gas_data,
    )

# Ищем поле `Новое показание` и вводим переданное пользователем значение.
type_value_in_input_with_attr(
    attr_name='class',
    attr_value='form-input newReading',
    field_value=str(new_gas_data),
)
# Нажимаем на кнопку `Произвести расчет`.
click_href_with_attribute('calcButton')
# После нажатия на кнопку выполняется скрипт... Ждем пару секунд.
time.sleep(2)
# Выбираем необходимый способ оплаты (пробел в конце не опечатка так в HTML).
select_checkbox_with_text('Система быстрых платежей Банка России ')
# Сохраняем название сервиса, что-бы затем проверить добавился ли он в корзину.
SERVICE_NAME = get_service_name()
# Находим кнопку `Добавить в корзину` и нажимаем на неё.
click_button_with_text('Добавить в корзину')
# Проверяем добавлена ли услуга в корзину.
check_added_service_in_basket(SERVICE_NAME)
print('*' * 5, f'Услуга `{SERVICE_NAME}` добавлена в корзину!', '*' * 5)


# =============================================================================
# ОПЛАТА ЭЛЕКТРОЭНЕРГИИ.
# =============================================================================


# Находим карточку `АО "Ульяновскэнерго"` и нажимаем на неё.
click_card_with_text('АО "Ульяновскэнерго"')
# Вводим номер лицевого счета.
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='group-1-field-0-value',
    field_value=ENERGY_ACCOUNT_NUM
)
# Вводим период оплаты.
pay_period = f'{date.today().month}.{date.today().year}'
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='group-1-field-1-value',
    field_value=pay_period
)
# Нажимаем enter что-бы введенная дата преобразовалась в нужный формат.
ac.send_keys(Keys.ENTER).perform()
# Нажимаем на enter и идем дальше.
ac.send_keys(Keys.ENTER).perform()


# Находим поле с предыдущем показанием и сохраняем его значение.
xpath = '//td[contains(@class, "pay-ulenergo-old")]'
last_energy_data = get_element_text(xpath)
# Преобразовываем строку в int.
last_energy_data = convert_string_to_number(
    regex=r'[\d]+',
    value=last_energy_data
)

# Запрашиваем новое показание у пользователя, проверяем переданное значение.
new_energy_data = 0
while new_energy_data <= last_energy_data:
    print(f'Введите показатель ЭЛЕКТРОЭНЕРГИИ, БОЛЬШЕ чем {last_energy_data}.')
    new_energy_data = input('Новое показание: ')
    new_energy_data = convert_string_to_number(
        regex=r'[\d]+',
        value=new_energy_data,
    )

# Ищем поле `Новое показание` и вводим переданное пользователем значение.
type_value_in_input_with_attr(
    attr_name='class',
    attr_value='form-input newReading',
    field_value=str(new_energy_data),
)
# Нажимаем на кнопку `Произвести расчет`.
click_href_with_attribute('calcButton')
# После нажатия на кнопку выполняется скрипт... Ждем пару секунд.
time.sleep(5)
# Выбираем необходимый способ оплаты (пробел в конце не опечатка так в HTML).
select_checkbox_with_text('Система быстрых платежей Банка России ')
# Сохраняем название сервиса, что-бы затем проверить добавился ли он в корзину.
SERVICE_NAME = get_service_name()
# Находим кнопку `Добавить в корзину` и нажимаем на неё.
click_button_with_text('Добавить в корзину')
# Проверяем добавлена ли услуга в корзину.
check_added_service_in_basket(SERVICE_NAME)
print('*' * 5, f'Услуга `{SERVICE_NAME}` добавлена в корзину!', '*' * 5)


# =============================================================================
# ОПЛАТА ВОДЫ.
# =============================================================================


driver.get(HOME_PAGE)
# Находим карточку `Оплата ... услуг` и нажимаем на неё.
click_card_with_text('Оплата жилого помещения и коммунальных услуг')
# Вводим номер лицевого счета.
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='group-1-field-0-value',
    field_value=WATER_ACCOUNT_NUM
)
# Вводим период оплаты.
pay_period = f'{date.today().month}.{date.today().year}'
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='group-1-field-1-value',
    field_value=pay_period
)
# Нажимаем enter что-бы введенная дата преобразовалась в нужный формат.
ac.send_keys(Keys.ENTER).perform()
# Нажимаем на enter и идем дальше.
ac.send_keys(Keys.ENTER).perform()
# Находим карточку `Начисление РКЦ Ульяновск` и нажимаем на неё.
click_card_with_text('Начисление РКЦ Ульяновск')
# Нажимаем на чекбокс `Оплата с учетом задолженности ...` если он не выбран.
select_checkbox_with_text('Оплата с учетом задолженности за прошлые периоды')
# Вводим email куда отправится чек об оплате.
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='email',
    field_value=SEND_TO_EMAIL
)
# Выбираем необходимый способ оплаты (пробел в конце не опечатка так в HTML).
select_checkbox_with_text('Система быстрых платежей Банка России ')
# Сохраняем название сервиса, что-бы затем проверить добавился ли он в корзину.
SERVICE_NAME = get_service_name()
# Находим кнопку `Добавить в корзину` и нажимаем на неё.
click_button_with_text('Добавить в корзину')
# Проверяем добавлена ли услуга в корзину.
check_added_service_in_basket(SERVICE_NAME)
print('*' * 5, f'Услуга `{SERVICE_NAME}` добавлена в корзину!', '*' * 5)


# =============================================================================
# ОПЛАТА КАПИТАЛЬНОГО РЕМОНТА.
# =============================================================================


# Находим карточку `Фонд капитального ремонта` и нажимаем на неё.
click_card_with_text('Фонд капитального ремонта')
# Вводим номер лицевого счета.
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='group-1-field-0-value',
    field_value=REPAIR_ACCOUNT_NUM
)
# Вводим период оплаты.
pay_period = f'{date.today().month}.{date.today().year}'
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='group-1-field-1-value',
    field_value=pay_period
)
# Нажимаем enter что-бы введенная дата преобразовалась в нужный формат.
ac.send_keys(Keys.ENTER).perform()
# Нажимаем на enter и идем дальше.
ac.send_keys(Keys.ENTER).perform()
# Нажимаем на чекбокс `Оплата с учетом задолженности ...` если он не выбран.
select_checkbox_with_text('Оплата с учетом задолженности за прошлые периоды')
# Вводим email куда отправится чек об оплате.
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='email',
    field_value=SEND_TO_EMAIL
)
# Сохраняем название сервиса, что-бы затем проверить добавился ли он в корзину.
SERVICE_NAME = get_service_name()
# Находим кнопку `Добавить в корзину` и нажимаем на неё.
click_button_with_text('Добавить в корзину')
# Проверяем добавлена ли услуга в корзину.
check_added_service_in_basket(SERVICE_NAME)
print('*' * 5, f'Услуга `{SERVICE_NAME}` добавлена в корзину!', '*' * 5)


# =============================================================================
# ОПЛАТА ОТОПЛЕНИЯ.
# =============================================================================


# Находим карточку `ПАО "Т Плюс"` и нажимаем на неё.
click_card_with_text('ПАО "Т Плюс"')
# Вводим номер лицевого счета.
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='group-1-field-0-value',
    field_value=HEATING_ACCOUNT_NUM
)
# Вводим период оплаты.
pay_period = f'{date.today().month}.{date.today().year}'
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='group-1-field-1-value',
    field_value=pay_period
)
# Нажимаем enter что-бы введенная дата преобразовалась в нужный формат.
ac.send_keys(Keys.ENTER).perform()
# Нажимаем на enter и идем дальше.
ac.send_keys(Keys.ENTER).perform()
# Нажимаем на чекбокс `Оплата с учетом задолженности ...` если он не выбран.
select_checkbox_with_text('Оплата с учетом задолженности за прошлые периоды')
# Вводим email куда отправится чек об оплате.
type_value_in_input_with_attr(
    attr_name='id',
    attr_value='email',
    field_value=SEND_TO_EMAIL
)
# Сохраняем название сервиса, что-бы затем проверить добавился ли он в корзину.
SERVICE_NAME = get_service_name()
# Находим кнопку `Добавить в корзину` и нажимаем на неё.
click_button_with_text('Добавить в корзину')
# Проверяем добавлена ли услуга в корзину.
check_added_service_in_basket(SERVICE_NAME)
print('*' * 5, f'Услуга `{SERVICE_NAME}` добавлена в корзину!', '*' * 5)
