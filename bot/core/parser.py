from datetime import datetime

from classes import Command, Categories, Expense, Income 
import utils

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

    match msg[0]:
        case "-":
            return Command.EXPENSE
        case "+":
            return Command.INCOME
    
    match msg.split():
        case ["cancel"]:
            return Command.CANCEL
        case ["balance" | "bl"]:
            return Command.BALANCE
        case ["balance" | "bl", amount] if amount.isdigit():
            return Command.BALANCE_NEW
        case ["month"]:
            return Command.MONTH
        case [month] if month.lower() in _MONTH_NAMES.values():
            return Command.MONTH
        case [month, year] if month.lower() in _MONTH_NAMES.values() and year.isdigit():
            return Command.MONTH
        case _:
            return Command.UNKNOWN


def parse_expense(message: str) -> Expense:
    try:
        words = message[1:].strip().split()
        amount = int(words[0])
        category = "other"
        for cat in Categories:
            if words[1].lower() == cat.value:
                category = words[1].lower()
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

        return Expense(amount, category, description, utils.time_now())

    except Exception:
        raise ValueError("Incorrect expense message")


def parse_income(message: str) -> Income:
    try:
        words = message[1:].strip().split()
        if len(words) < 2:
            raise ValueError("Incorrect income message")

        amount = int(words[0])
        description = " ".join(words[1:])

        return Income(amount, description, utils.time_now())

    except Exception:
        raise ValueError("Incorrect income message")


def parse_month(message: str) -> datetime:
    words = message.split()
    month = words[0].lower()
    if month == "month":
        current = datetime.now()
        return datetime(current.year, current.month, 1)
        
    index = None
    for idx, name in _MONTH_NAMES.items():
        if name == month:
            index = idx
    try:
        year = int(words[1])
        return datetime(year, month, 1)
    except IndexError:
        pass

    return datetime(datetime.now().year, index, 1)
