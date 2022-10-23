from classes import Command, Categories, Expense, Income 
import utils

_MONTH_NAMES = (
    "январь",
    "февраль",
    "март",
    "апрель",
    "май",
    "июнь",
    "июль",
    "август",
    "сентябрь",
    "октябрь",
    "ноябрь",
    "декабрь"
)


def command_type(message: str) -> Command:
    msg = message.strip().lower()

    match msg[0]:
        case "-":
            return Command.EXPENSE
        case "+":
            return Command.INCOME
    
    match msg.split():
        case ["cancel" | "отмена"]:
            return Command.CANCEL
        case ["balance" | "bl"]:
            return Command.BALANCE
        case ["balance" | "bl", amount] if amount.isdigit():
            return Command.BALANCE_NEW
        case ["month" | "месяц"]:
            return Command.MONTH
        case [month] if month.lower() in _MONTH_NAMES:
            return Command.CONCRETE_MONTH
        case [month, year] if month.lower() in _MONTH_NAMES and year.isdigit():
            return Command.CONCRETE_MONTH_AND_YEAR
        case _:
            return Command.UNKNOWN


def parse_expense(message: str) -> Expense:
    try:
        words = message[1:].strip().split()
        amount = int(words[0])
        category = "другое"
        for cat in Categories:
            if words[1].lower() == cat.value:
                category = words[1].lower()
        description = None
        if category == "другое":
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