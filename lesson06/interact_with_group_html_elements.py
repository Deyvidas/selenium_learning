from pprint import pprint

from pydantic import TypeAdapter
from selenium.webdriver.remote.webelement import WebElement

from lesson02.geckodriver import driver
from lesson06.utils.html_finders import find_element
from lesson06.utils.html_finders import find_elements
from lesson06.utils.models.book import Book
from lesson06.utils.models.price import Price


xpath = {
    'card': '//article[@class="product_pod"]',
    'book_in_stock': './/p[@class="instock availability"]',
    'book_price': './/div[@class="product_price"]/p[@class="price_color"]',
    'book_title': './/h3/a',
}


def get_book_in_stock(card: WebElement) -> bool:
    """Return True if text of element in ('In stock',), else False."""
    text = find_element(root=card, xpath=xpath['book_in_stock']).text
    return text in ('In stock',)


def get_book_price(card: WebElement) -> Price:
    """Return price of book."""
    text = find_element(root=card, xpath=xpath['book_price']).text
    return Price(price=text)


def get_book_title(card: WebElement) -> str:
    """Return title of the book."""
    element = find_element(root=card, xpath=xpath['book_title'])
    # The text of this element has short title e.g. 'Some title w...'.
    # And in the attribute 'title' stored original title.
    text = element.get_attribute('title')
    if text is not None:
        return text
    raise ValueError(f'Attribute \'title\' not found in {xpath["book_title"]}')


def main() -> list[Book]:
    driver.get('http://books.toscrape.com/index.html')
    book_cards = find_elements(root=driver, xpath=xpath['card'])
    return [
        Book(
            in_stock=get_book_in_stock(card),
            price=get_book_price(card),
            title=get_book_title(card),
        )
        for card in book_cards
    ]


if __name__ == '__main__':
    books = main()
    pprint(TypeAdapter(list[Book]).dump_python(books))


# Очень важное замечание при использовании `xpath`:
# book_cards.find_element('xpath', '//p[@class="Some p class"]')
#                                   ^^
# В этом месте нужно быть предельно осторожным и осознать что такая запись
# равна сильна /users/.../... то есть этой записью мы начинаем поиск элемента
# не из ранее полученного элемента а из корня ДОМа. Короче такая запись равна
# сильна -> driver.find_element('xpath', '//p[@class="Some p class"]')
#           ^^^^^^
# Но как быть если определенный ДОМ элемент уже сохранен и нам нужно вести
# поиск другого элемента внутри этого элемента?
# Очень просто! Достаточно добавить точку перед // -> вот так .//...
# таки образом поиск будет вестись относительно переданного элемента пример
# book_cards.find_element('xpath', './/p[@class="Some p class"]')
#                                   ^^^

# Итог:
# element = driver.find_elements('xpath', '//article[@class="product_pod"]')

# Как не надо:
# element[0].find_element('xpath', '//p[@class="Some p class"]')
# //p[@class="Some p class"]

# Как надо:
# element[0].find_element('xpath', './/p[@class="Some p class"]')
# //article[@class="product_pod"]/p[@class="Some p class"]
