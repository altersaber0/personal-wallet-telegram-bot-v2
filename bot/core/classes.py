from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime


class Command(Enum):
    EXPENSE = auto()
    INCOME = auto()
    SET_BALANCE = auto()
    MONTH = auto()
    UNKNOWN = auto()

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
class Category:
    name: str
    aliases: list[str]