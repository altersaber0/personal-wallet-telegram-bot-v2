from dataclasses import dataclass
from datetime import datetime


@dataclass
class Expense:
    amount: float
    category: str
    description: str | None
    time: datetime


@dataclass
class Income:
    amount: float
    description: str
    time: datetime


@dataclass
class MonthStatistics:
    year: int
    month: int
    statistics: dict[str, float]
    start_balance: float
    end_balance: float

    @property
    def difference(self) -> float:
        return self.end_balance - self.start_balance