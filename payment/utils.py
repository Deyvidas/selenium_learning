import re


def is_float(number: str) -> bool:
    """Return False if signs after `.` or `,` exceed 6 or if it is not possible
    to convert the string to float. Otherwise, return True.
    """
    return not re.fullmatch(r'^[\d]+[,.]?[\d]{0,6}$', number) is None
