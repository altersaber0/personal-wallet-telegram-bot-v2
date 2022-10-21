from datetime import datetime

def time_now() -> datetime:
    return datetime.now().replace(microsecond=0)

def str_from_time(time: datetime) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")

def time_from_str(string: str) -> datetime:
    return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
