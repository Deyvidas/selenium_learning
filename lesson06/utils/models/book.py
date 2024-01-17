from pydantic import BaseModel
from pydantic import Field

from lesson06.utils.models.price import Price


class Book(BaseModel):
    in_stock: bool
    price: Price
    title: str = Field(min_length=3)
