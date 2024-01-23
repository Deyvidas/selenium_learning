from pydantic import BaseModel
from pydantic import Field

from payment.config import config


url_regex = r'^http[s]?:\/\/[\S]+.[\S]+[\/]?$'
email_regex = r'^[\S]+@[\S]+.[\S]?$'
str_regex = r'^[\S]+.*[\S]?$'  # disallow ' some' | 'some ' | ' some ' | '   '

email_examples = [
    'https://some.site.com/',
    'https://some.site.com',
    'http://some-site.com/some/else/',
    'http://some_site.com/some/else',
]


class UserProfile(BaseModel):
    auth_url: str = Field(
        min_length=8,
        pattern=url_regex,
        examples=email_examples,
    )
    email: str = Field(min_length=5, pattern=email_regex)
    login: str = Field(min_length=1, pattern=str_regex)
    password: str = Field(min_length=1, pattern=str_regex)

    water_account: str = Field(min_length=1, pattern=str_regex)
    repair_account: str = Field(min_length=1, pattern=str_regex)
    heating_account: str = Field(min_length=1, pattern=str_regex)
    gas_account: str = Field(min_length=1, pattern=str_regex)
    energy_account: str = Field(min_length=1, pattern=str_regex)


user_profile = UserProfile(**config['user_profile'])
