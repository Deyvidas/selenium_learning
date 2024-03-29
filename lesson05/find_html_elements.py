from lesson02.geckodriver import driver


driver.get('https://the-internet.herokuapp.com/add_remove_elements/')
driver.maximize_window()

# Находим элемент `button` с атрибутом `onclick="addElement()"`.
by_value = ('xpath', '//button[@onclick="addElement()"]')
add_element_button = driver.find_element(*by_value)
assert add_element_button.text == 'Add Element'

# Нажимаем на кнопку `Add Element` после чего должна появиться кнопка `Delete`.
add_element_button.click()

# Находим новую сгенерированную кнопку `Delete`.
by_value = ('xpath', '//button[@class="added-manually"]')
delete_button = driver.find_element(*by_value)
assert delete_button.text == 'Delete'

# Нажимаем на кнопку `Delete` после чего она должна исчезнуть.
delete_button.click()
by_value = ('xpath', '//button[text()="Delete"]')
delete_button_remained = driver.find_elements(*by_value)

# Проверяем количество оставшихся кнопок `Delete` == 0.
assert delete_button_remained == list()

# Теперь заспамим кликами кнопку `Add Element` )).
by_value = ('xpath', '//button[text()="Add Element"]')
add_element_button = driver.find_element(*by_value)
[add_element_button.click() for _ in range(10)]  # type: ignore[func-returns-value]

# Проверим правильное ли количество кнопок сгенерировалось.
by_value = ('xpath', '//button[@onclick="deleteElement()"]')
delete_button_remained = driver.find_elements(*by_value)
assert len(delete_button_remained) == 10

# Удалим 4 кнопки `Delete` в итоге их должно остаться 6.
[button.click() for button in delete_button_remained[:4]]  # type: ignore[func-returns-value]
assert len(delete_button_remained) == 10
# Но как видим из проверки кнопки из списка не удаляются... Все так происходит,
# по тому, что из ДОМа они удаляются но из списка нет.

# Но если переопределить заново список то все будет правильно!
by_value = ('xpath', '//button[@onclick="deleteElement()"]')
delete_button_remained_new = driver.find_elements()
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

by_value = ('xpath', '//button[@class="added-manually"]')
delete_button_total = driver.find_elements(*by_value)
assert len(delete_button_total) == 0
