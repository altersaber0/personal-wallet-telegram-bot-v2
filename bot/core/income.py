from typing import NamedTuple
from datetime import datetime

class Income(NamedTuple):
    amount: float
    description: str
    time: datetime