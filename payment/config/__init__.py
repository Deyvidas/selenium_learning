from pathlib import Path
from typing import Any
from typing import Required
from typing import TypedDict

import yaml


CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / 'config.yaml'


class Config(TypedDict):
    user_profile: Required[dict[str, Any]]


with open(CONFIG_FILE) as file:
    config: Config = yaml.load(file, yaml.loader.FullLoader)

__all__ = [
    'CONFIG_DIR',
    'CONFIG_FILE',
    'config',
]
