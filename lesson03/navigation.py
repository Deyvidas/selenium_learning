from time import sleep

from lesson02.geckodriver import driver


# Делаем основной запрос.
driver.get('https://www.google.com')
sleep(2)
# Имитируем ввод `hello world` в строке поиска.
driver.get('https://www.google.com/search?q=hello+world')
sleep(2)
# Имитируем нажатие на кнопку `назад` [ <- ].
driver.back()
sleep(2)
# Имитируем нажатие на кнопку `вперед` [ -> ].
driver.forward()
sleep(2)
# Имитируем нажатие на кнопку `обновить страницу`.
driver.refresh()
sleep(2)
