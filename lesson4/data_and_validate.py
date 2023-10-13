from lesson2.geckodriver import driver


driver.get('https://www.wikipedia.org/')
# Получение url адреса из строки ввода url браузера в моменте.
url = driver.current_url
# Получение заголовка страницы [head/title].
title = driver.title
# Получение исходного HTML кода полученной страницы типа `str` .
html = driver.page_source
