from enum import Enum, auto
from typing import NamedTuple
from datetime import datetime


class Command(Enum):
    EXPENSE = auto()
    INCOME = auto()
    CANCEL = auto()
    BALANCE = auto()
    BALANCE_NEW = auto()
    MONTH = auto()
    CONCRETE_MONTH = auto()
    CONCRETE_MONTH_AND_YEAR = auto()
    UNKNOWN = auto()


class Categories(Enum):
    FOOD = "продукты"
    TRANSPORT = "транспорт"
    ACTIVITIES = "развлечения"
    MEDICINE = "лекарства"
    MISC = "расходники"
    MONTHLY = "ежемесячные"
    OTHER = "другое"



class Expense(NamedTuple):
    amount: float
    category: str
    description: str | None
    time: datetime


class Income(NamedTuple):
    amount: float
    description: str
    time: datetime