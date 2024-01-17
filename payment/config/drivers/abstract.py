from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.common.service import Service
from selenium.webdriver.remote.webdriver import WebDriver


_Driver = TypeVar('_Driver', bound=WebDriver)
_Options = TypeVar('_Options', bound=ArgOptions)
_Service = TypeVar('_Service', bound=Service)


class AbstractDriver(ABC, Generic[_Driver, _Options, _Service]):
    @property
    @abstractmethod
    def driver(self) -> _Driver:
        raise NotImplementedError

    @property
    @abstractmethod
    def options(self) -> _Options:
        raise NotImplementedError

    @property
    @abstractmethod
    def service(self) -> _Service:
        raise NotImplementedError
