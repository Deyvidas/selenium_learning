from collections import namedtuple
from pprint import pprint
from typing import Any

from lesson02.geckodriver import driver
from lesson06.helpers.html_finders import (
    book_in_stock,
    get_book_price,
    get_book_title,
)


driver.get('http://books.toscrape.com/index.html')


# Сохраним все карточки книг.
book_card_list = driver.find_elements('xpath', '//article[@class="product_pod"]')

# Немножко побалуемся.
books_detail_json: list[dict[str, Any]] = list()
Book = namedtuple('Book', 'in_stock price title')

for book_card in book_card_list:
    in_stock = book_in_stock(book_card)
    price = get_book_price(book_card)
    title = get_book_title(book_card)
    book = Book(in_stock=in_stock, price=price, title=title)
    books_detail_json.append(book._asdict())

# Очень важное замечание при использовании `xpath`:
# book_card_list.find_element('xpath', '//p[@class="Some p class"]')
# ^^^^^^^^^^^^^^                       ^^^^
# В этом месте нужно быть предельно осторожным и осознать что такая запись
# равна сильна /users/.../... то есть этой записью мы начинаем поиск элемента
# не из ранее полученного элемента а из корня... Короче такая запись равна
# сильна -> driver.find_element('xpath', '//p[@class="Some p class"]')
#           ^^^^^^
# Но как быть если определенный ДОМ элемент уже сохранен и нам нужно вести
# поиск другого элемента внутри этого элемента?
# Очень просто! Достаточно добавить точку перед // -> вот так .//...
# таки образом поиск будет вестись относительно переданного элемента пример
# book_card_list.find_element('xpath', './/p[@class="Some p class"]')
# ^^^^^^^^^^^^^^                       ^^^^

# Итог:
# element = driver.find_elements('xpath', '//article[@class="product_pod"]')

# Как не надо:
# element[0].find_element('xpath', '//p[@class="Some p class"]')
# //p[@class="Some p class"]

# Как надо:
# element[0].find_element('xpath', './/p[@class="Some p class"]')
# //article[@class="product_pod"]/p[@class="Some p class"]

pprint(books_detail_json)
