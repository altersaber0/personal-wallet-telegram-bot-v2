from typing import NamedTuple
from datetime import datetime

class Expense(NamedTuple):
    amount: float
    category: str
    description: str
    time: datetime