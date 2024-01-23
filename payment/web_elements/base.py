from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import TypeVar
from typing import override

from selenium.common import JavascriptException
from selenium.common import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as _ec

from payment.config.driver.base import DriverBase
from payment.web_elements.exceptions import ErrorElementDoesNotFound
from payment.web_elements.exceptions import ErrorElementDoesNotHaveAttribute
from payment.web_elements.exceptions import ErrorElementNotClickable
from payment.web_elements.exceptions import ErrorElementNotVisible
from payment.web_elements.exceptions import ErrorFoundMultipleElements
from payment.web_elements.exceptions import ErrorStubIsNotAccessible
from payment.web_elements.exceptions import KwargsBaseError


T = TypeVar('T', bound='ElementBase')


class WebElementStub(WebElement):
    def __init__(self) -> None:
        super().__init__(parent=None, id_=None)


@dataclass(kw_only=True)
class ElementBase:
    location: str
    driver: DriverBase
    x_loc: tuple[str, str] = field(init=False)

    def __post_init__(self):
        self.x_loc = ('xpath', self.location)

    @abstractmethod
    def _get_web_elements(self) -> list[WebElement]:
        """Return a list of WebElements found in the DOM structure of the
        driver.current_url, or an empty list if not found.
        """
        raise NotImplementedError

    @property
    def element(self) -> WebElement:
        return self._get_web_element_one_strict()

    @property
    def html_attributes(self) -> dict[str, str]:
        """Returns a dictionary with all attributes of the HTML tag, that is
        related to WebElement.

        Returns:
            dict[str, str]: The dictionary with all attributes of HTML tag.
        """
        self.raise_if_stub()
        script = 'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;'  # noqa: E501
        return self.driver.execute_script(script, self.element)

    @property
    def text(self) -> str:
        self.raise_if_stub()
        text = self.element.get_attribute('value')
        if text is None:
            text = self.element.text
        return text

    @property
    def error_required_kwargs(self) -> KwargsBaseError:
        """Provides just the necessary values to initialize BaseError."""
        kwargs: KwargsBaseError = {
            'class_name': type(self).__name__,
            'location': self.location,
            'url': self.driver.current_url,
        }
        return kwargs

    def raise_if_stub(self, element: WebElement | None = None) -> None:
        """If the element is a stub, raise the ErrorStubIsNotAccessible
        exception.
        """
        if element is None:
            element = self.element
        if element.parent == element.id is None:
            raise ErrorStubIsNotAccessible(**self.error_required_kwargs)

    def get_html_attr(self, html_attr: str) -> str:
        """Returns the HTML element attribute value if it has this attribute,
        otherwise raises an exception.

        Args:
            html_attr (str): The attribute that must have HTML element.

        Returns:
            str: The HTML element attribute value.
            empty[str]: If the HTML element has an attribute, but its value is an empty string.

        Raise:
            ErrorElementDoesNotHaveAttribute: If the HTML element does not have this attribute.
        """
        self.raise_if_stub()
        attr_value = self.html_attributes.get(html_attr, None)
        if attr_value is not None:
            return attr_value
        kwargs = self.error_required_kwargs
        kwargs['attribute'] = html_attr
        raise ErrorElementDoesNotHaveAttribute(**kwargs)

    def get_parent(self, element_type: type[T], depth: int = 1) -> T:
        """Find the parent WebElement that is X steps higher than the current
        WebElement in the HTML structure, Then obtain his xpath and create a
        new instance of element_type and return it.
        If the depth is less than 1 or the depth provokes the exit from the
        borders of the DOM structure, raise ValueError.

        Args:
            element_type (type[ElementBase]): The class that needs to be returned.
            depth (int): How many nodes higher is the parent of the child located.

        Returns:
            ElementBase: The instance of the class received in the element_type parameter.

        Raise:
            ValueError: If the depth is less than 1.
            ValueError: If the depth provokes the exit from the borders of the DOM structure.
        """
        self.raise_if_stub()
        if depth < 1:
            msg = f'The value of parameter depth cannot be less than 0, {depth=}'  # fmt: skip
            raise ValueError(msg)
        html_parent = 'Can\'t get the parent of the HTML tag, it doesn\'t have a parent.'  # fmt: skip

        script = 'return arguments[0].parentNode;'
        element = self.element
        if element.tag_name == 'html':
            try:  # Make a try because in one html tag may be another html tag.
                element = self.driver.execute_script(script, element)
            except JavascriptException:
                raise ValueError(html_parent)

        while depth > 0:
            if not isinstance(element, WebElement):
                msg = f'The script {script} should return the WebElement, but was returned {type(element)}.'
                raise TypeError(msg)

            depth -= 1
            try:
                element = self.driver.execute_script(script, element)
            except JavascriptException:
                raise ValueError(html_parent)

        element_xpath = self._get_xpath_absolute(element)
        return element_type(location=element_xpath, driver=self.driver)

    def get_child(self, element_type: type[T], location: str) -> T:
        """Generate a new instance of the class received in the element_type
        parameter, with a new location attribute value.

        Args:
            element_type (type[ElementBase]): The class that needs to be returned.
            location (str): The xpath location that is combined with the parent location attribute through `/.`.

        Returns:
            ElementBase: The instance of the class received in the element_type parameter.

        Examples::

            parent = TextVisible(location='//div[@class="card-padding"]', ...)
            children = parent.get_child(TextHidden, '//div[@class="alert alert-danger"]')

            isinstance(parent, TextVisible)
            >>> True
            isinstance(children, TextHidden)
            >>> True

            parent.location
            >>> '//div[@class="card-padding"]'
            children.location
            >>> '//div[@class="card-padding"]/.//div[@class="alert alert-danger"]'

            parent.element.get_attribute('class')
            >>> 'card-padding'
            children.element.get_attribute('class')
            >>> 'alert alert-danger'
        """
        self.raise_if_stub()
        return element_type(
            location=f'{self.location}/.{location}',
            driver=self.driver,
        )

    def _get_web_element_one_strict(self) -> WebElement:
        """Return strictly one WebElement if it is present in the DOM structure
        of the driver.current_url, otherwise raises an exception.

        Returns:
            WebElement: Found selenium WebElement on the current URL of the driver.

        Raise:
            ErrorFoundMultipleElements: If the count of found elements is more than one.
            ErrorElementDoesNotFound: If no elements were found.
        """
        elements = self._get_web_elements()
        if len(elements) == 1:
            return elements[0]

        if len(elements) > 1:
            raise ErrorFoundMultipleElements(**self.error_required_kwargs)
        raise ErrorElementDoesNotFound(**self.error_required_kwargs)

    def _get_web_element_one_or_stub(self) -> WebElement:
        """Return one WebElement if it is present in the DOM structure of the
        driver.current_url, otherwise return a stub of WebElement.

        Returns:
            WebElement: Found selenium WebElement on the current URL of the driver.
            WebElementStub: If there are more than one found element or no elements were found.
        """
        elements = self._get_web_elements()
        if len(elements) == 1:
            return elements[0]
        return WebElementStub()

    def _get_xpath_absolute(self, element: WebElement | None = None) -> str:
        """Returns absolute xpath of the WebElement in the DOM structure.

        Args:
            element (WebElement): The selenium WebElement.
            element (None): The WebElement is taken from the self.element property.

        Returns:
            str: The absolute xpath of the element in the DOM structure.

        Examples::

            '/html[@class="..." and @lang="..."]'
            '/html[@class="..." and @lang="..."]/head'
            '/html[@class="..." and @lang="..."]/body[@style="..."]/div[@class="..."]/div[@class="..."]/main[@id="..."]'
        """
        if element is None:
            element = self.element
        self.raise_if_stub(element)

        script = 'return arguments[0].parentNode;'
        full_path = f'/{self._get_attr_as_xpath(element)}'
        if element.tag_name == 'html':
            try:  # Make a try because in one html tag may be another html tag.
                element = self.driver.execute_script(script, element)
            except JavascriptException:
                return full_path

        while True:
            if not isinstance(element, WebElement):
                msg = f'The script {script} should return the WebElement, but was returned {type(element)}.'
                raise TypeError(msg)

            try:
                element = self.driver.execute_script(script, element)
            except JavascriptException:
                return full_path

            node = self._get_attr_as_xpath(element)
            full_path = f'/{node}{full_path}'

    def _get_attr_as_xpath(self, element: WebElement | None = None) -> str:
        """Return the tag name and attributes of the WebElement in xpath format,
        but without slashes, if WebElement does not have attributes, return only
        the tag_name (the attributes are located alphabetically a->z).

        Args:
            element (WebElement): The selenium WebElement.
            element (None): The WebElement is taken from the self.element property.

        Examples::

            <a class="..." aria-label="..." href="...">...</a>
            'a[@aria-label="..." and @class="..." and @href="..."]'

            <section class="..." data-modal="..." id="..." data-background="...">...</section>
            'section[@class="..." and @data-background="..." and @data-modal="..." and @id="..."]'

            <title>...</title>
            'title'
        """
        self.raise_if_stub(element)
        if element is None:
            element = self.element
        script = 'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;'  # noqa: E501
        attrs = self.driver.execute_script(script, element)
        attrs_str = ' and '.join([f'@{a}="{v}"' for a, v in attrs.items()])
        match attrs_str:
            case '':
                return element.tag_name
            case _:
                return f'{element.tag_name}[{attrs_str}]'


class ElementHidden(ElementBase):
    @override
    def _get_web_elements(self) -> list[WebElement]:
        condition = _ec.presence_of_all_elements_located(self.x_loc)
        try:
            return self.driver.driver_wait.until(condition)
        except TimeoutException:
            return list()


class ElementVisible(ElementBase):
    @property
    @override
    def element(self) -> WebElement:
        try:
            return super().element
        except ErrorElementDoesNotFound as error:
            kwargs = self.error_required_kwargs
            kwargs['original_error'] = f'Or may be that: {error.message}'
            raise ErrorElementNotVisible(**kwargs)

    @override
    def _get_web_elements(self) -> list[WebElement]:
        condition = _ec.visibility_of_all_elements_located(self.x_loc)
        try:
            return self.driver.driver_wait.until(condition)
        except TimeoutException:
            return list()


class ElementClickable(ElementBase):
    @property
    @override
    def element(self) -> WebElement:
        try:
            return super().element
        except ErrorElementDoesNotFound as error:
            kwargs = self.error_required_kwargs
            kwargs['original_error'] = f'Or may be that: {error.message}'
            raise ErrorElementNotClickable(**kwargs)

    @override
    def _get_web_elements(self) -> list[WebElement]:
        condition = _ec.element_to_be_clickable(self.x_loc)
        try:
            return [self.driver.driver_wait.until(condition)]
        except TimeoutException:
            return list()
