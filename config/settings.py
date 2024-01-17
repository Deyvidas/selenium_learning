import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def set_new_folder_or_get_existent(suffix: str) -> str:
    """Create if not exist and return path BASE_DIR/<suffix>."""
    path = str(BASE_DIR / suffix)
    if not os.path.isdir(path):
        os.mkdir(path)
    return path
