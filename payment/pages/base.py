from dataclasses import dataclass

from payment.config.driver.base import DriverBase


@dataclass(kw_only=True)
class PageBase:
    driver: DriverBase
    url: str

    def __post_init__(self) -> None:
        self.driver.get(self.url)
