from pydantic import BaseModel
from pydantic import Field


class Currency(BaseModel):
    symbol: str = Field(min_length=1, max_length=1, pattern=r'^[£]$')
    code: str = Field(min_length=3, max_length=3, pattern=r'^[A-Z]{3}$')
    unit: str = Field(min_length=3, pattern=r'^[a-z]{3,}$')
    plural: str = Field(min_length=3, pattern=r'^[a-z]{3,}$')


available_currencies = {
    '£': Currency(symbol='£', code='GBP', unit='pound', plural='pounds')
}
available_msg = f'Available list of currencies: {available_currencies.keys()}'
currency_not_found_msg = 'Currency {symbol} not found. ' + available_msg
