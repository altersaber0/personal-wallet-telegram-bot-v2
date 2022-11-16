from datetime import datetime


def time_now() -> datetime:
    return datetime.now().replace(microsecond=0)


def str_from_time(time: datetime) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def time_from_str(string: str) -> datetime:
    return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


def isfloat(string: str) -> bool:
    if string.lower() in ["nan", "inf", "infinity"]:
        return False
    
    try:
        float(string)
        return True
    except ValueError:
        return False


def split_in_chunks(lst: list, *, chunk_size: int) -> list[list]:
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]