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
class Category:
    name: str
    aliases: list[str]