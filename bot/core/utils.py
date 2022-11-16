from datetime import datetime


def time_now() -> datetime:
    """Get current time as a datetime object (without microseconds)."""

    return datetime.now().replace(microsecond=0)


def str_from_time(time: datetime) -> str:
    """Parse string into a datetime object."""

    return time.strftime("%Y-%m-%d %H:%M:%S")


def time_from_str(string: str) -> datetime:
    """Turn datetime object into a string (omitting microseconds)."""

    return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


def isfloat(string: str) -> bool:
    """Whether a string is a valid number."""

    if string.lower() in ["nan", "inf", "infinity"]:
        return False
    
    try:
        float(string)
        return True
    except ValueError:
        return False


def split_in_rows(lst: list, *, row_size: int) -> list[list]:
    """Split a list into even chunks (last chunk may be smaller than others)."""

    return [lst[i:i + row_size] for i in range(0, len(lst), row_size)]