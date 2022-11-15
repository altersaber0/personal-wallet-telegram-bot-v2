from enum import Enum, auto
from typing import NamedTuple
from datetime import datetime


class Command(Enum):
    EXPENSE = auto()
    INCOME = auto()
    SET_BALANCE = auto()
    MONTH = auto()
    UNKNOWN = auto()


class Expense(NamedTuple):
    amount: float
    category: str
    description: str | None
    time: datetime


class Income(NamedTuple):
    amount: float
    description: str
    time: datetime


class Category(NamedTuple):
    name: str
    aliases: list[str]