import os

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def firefox_profile_folder() -> str:
    """Create and return path where firefox profile will saved if not exist."""
    path = str(BASE_DIR / 'firefox_profile')
    if not os.path.isdir(path):
        os.mkdir(path)
    return path
