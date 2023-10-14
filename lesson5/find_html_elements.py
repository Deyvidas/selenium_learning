from lesson2.geckodriver import driver


driver.get('https://the-internet.herokuapp.com/add_remove_elements/')
driver.maximize_window()

# Находим элемент `button` с атрибутом `onclick="addElement()"` .
add_element_button = driver.find_element('xpath', '//button[@onclick="addElement()"]')
assert add_element_button.text == 'Add Element'

# Нажимаем на кнопку `Add Element` после чего должна появиться кнопка `Delete` .
add_element_button.click()

# Находим новую сгенерированную кнопку `Delete` .
delete_button = driver.find_element('xpath', '//button[@class="added-manually"]')
assert delete_button.text == 'Delete'

# Нажимаем на кнопку `Delete` после чего она должна исчезнуть.
delete_button.click()
delete_button_remained = driver.find_elements('xpath', '//button[text()="Delete"]')

# Проверяем количество оставшихся кнопок `Delete` == 0.
assert delete_button_remained == list()

# Теперь заспамим кликами кнопку `Add Element` )).
add_element_button = driver.find_element('xpath', '//button[text()="Add Element"]')
[add_element_button.click() for _ in range(10)]

# Проверим правильное ли количество кнопок сгенерировалось.
delete_button_remained = driver.find_elements('xpath', '//button[@onclick="deleteElement()"]')
assert len(delete_button_remained) == 10

# Удалим 4 кнопки `Delete` в итоге их должно остаться 6.
[button.click() for button in delete_button_remained[:4]]
assert len(delete_button_remained) == 10
# Но как видим из проверки кнопки из списка не удаляются... Все так происходит,
# по тому, что из ДОМа они удаляются но из списка нет.

# Но если переопределить заново список то все будет правильно!
delete_button_remained_new = driver.find_elements('xpath', '//button[@onclick="deleteElement()"]')
assert len(delete_button_remained_new) == 6

# В списке `delete_button_remained` в конечном итоге будут лежат существующие в
# ДОМе объекты а также объекты которых уже нет в ДОМе и если попробовать
# сделать например `click()` по несущ. в ДОМе объекту выведется сообщение вроде
# `The element with the reference e1b7d...618a9 is stale.`
# `Элемент со ссылкой e1b7d...618a9 испортился.`
for index, delete_button in enumerate(delete_button_remained):
    try:
        delete_button.click()
        print(f'Кнопка с {index=}, нажата и сработала!')
    except Exception:
        print(f'Кнопка с {index=}, уже удалена из ДОМа! Не удалось её нажать.')

delete_button_total = driver.find_elements('xpath', '//button[@class="added-manually"]')
assert len(delete_button_total) == 0
