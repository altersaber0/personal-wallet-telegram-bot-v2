from datetime import datetime
from pathlib import Path
import json

from .classes import Command, Expense, Income, Category
from .utils import time_now

# mapping between month index and name
_MONTH_NAMES = {
    1: "january",
    2: "february",
    3: "march",
    4: "april",
    5: "may",
    6: "june",
    7: "july",
    8: "august",
    9: "september",
    10: "oktober",
    11: "november",
    12: "december"
}


def command_type(message: str) -> Command:
    msg = message.strip().lower()

    # match on first character
    match msg[0]:
        case "-":
            return Command.EXPENSE
        case "+":
            return Command.INCOME
    
    # match on individual words
    match msg.split():
        case ["balance", amount]:
            return Command.SET_BALANCE
        case ["month"]:
            return Command.MONTH
        case [month] if month.lower() in _MONTH_NAMES.values():
            return Command.MONTH
        case [month, year] if month.lower() in _MONTH_NAMES.values() and year.isdigit():
            return Command.MONTH
        case _:
            return Command.UNKNOWN


def parse_expense(message: str, categories: list[Category]) -> Expense:
    try:
        words = message[1:].strip().split()
        amount = float(words[0])

        # check if any category is present in message
        category = "other"
        for cat in categories:
            if words[1].lower() in cat.aliases:
                category = cat.name

        # description is either text after category, if it was stated
        # or text after amount
        description = None
        if category == "other":
            try:
                description = " ".join(words[1:])
            except:
                pass
        else:
            try:
                description = " ".join(words[2:])
            except:
                pass

        return Expense(amount, category, description, time_now())

    except Exception:
        raise ValueError("Incorrect expense message")


def parse_income(message: str) -> Income:
    try:
        words = message[1:].strip().split()

        # should contain at least 1 word of description
        if len(words) < 2:
            raise ValueError("Incorrect income message")

        amount = float(words[0])
        description = " ".join(words[1:])

        return Income(amount, description, time_now())

    except Exception:
        raise ValueError("Incorrect income message")


def parse_month(message: str) -> datetime:
    words = message.split()
    month = words[0].lower()
    # return datetime of current month
    if month == "month":
        current = datetime.now()
        return datetime(current.year, current.month, 1)

    # get month index based on name  
    index = None
    for idx, name in _MONTH_NAMES.items():
        if name == month:
            index = idx
    # check if concrete year was stated
    try:
        year = int(words[1])
        return datetime(year, index, 1)
    except IndexError:
        pass
    # return concrete month in current year
    return datetime(datetime.now().year, index, 1)


def parse_new_balance(message: str) -> float:
    _, balance = message.split()
    try:
        amount = float(balance)
        return amount
    except ValueError:
        raise ValueError("Incorrect new balance")