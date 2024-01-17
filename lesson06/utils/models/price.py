from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationError
from pydantic import computed_field

from lesson06.utils.models.currency import Currency
from lesson06.utils.models.currency import available_currencies
from lesson06.utils.models.currency import currency_not_found_msg


class Price(BaseModel):
    price: str = Field(min_length=5, pattern=r'^.{1}[\d]{1,}[.,][\d]{2}$')

    @computed_field  # type: ignore[misc]
    @property
    def currency(self) -> Currency:
        currency = available_currencies.get(self.price[0], None)
        if currency is not None:
            return currency
        msg = currency_not_found_msg.format(symbol=self.price[0])
        raise ValidationError(msg)

    @computed_field  # type: ignore[misc]
    @property
    def price_float(self) -> float:
        return eval(f'{self.integer_part}.{self.fractional_part}')

    @computed_field  # type: ignore[misc]
    @property
    def fractional_part(self) -> str:
        return self.price[-2:]

    @computed_field  # type: ignore[misc]
    @property
    def integer_part(self) -> str:
        return self.price[1:-3]
