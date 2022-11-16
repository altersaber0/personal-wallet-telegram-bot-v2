from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.update import Update

from .core.classes import Command, Expense, Income, Category
from .core.utils import str_from_time


class View:
    def reply(self, update: Update, text: str) -> None:
        update.message.reply_text(text)
    
    def reply_keyboard(self, update: Update, text: str, *, buttons: list[list[str]], placeholder: str = "") -> None:
        keyboard = ReplyKeyboardMarkup(
            buttons,
            one_time_keyboard=True,
            input_field_placeholder=placeholder
        )
        update.message.reply_text(text, reply_markup=keyboard)

    def error(self, update: Update, command: Command) -> None:
        match command:
            case Command.EXPENSE:
                self.reply(update, "Invalid expense message")
            case Command.INCOME:
                self.reply(update, "Invalid income message")
            case Command.SET_BALANCE:
                self.reply(update, "Invalid new balance message")
    
    def expense(self, update: Update, expense: Expense) -> None:
        description = expense.description if expense.description is not None else ""
        response = "\n".join(["Added new expense:",
                             f"Amount: {expense.amount:.2f}",
                             f"Category: {expense.category.capitalize()}",
                             f"Description: {description}",
                             f"Time: {str_from_time(expense.time)}"])
        self.reply(update, response)
    
    def income(self, update: Update, income: Income) -> None:
        response = "\n".join(["Added new income:",
                             f"Amount: {income.amount:.2f}",
                             f"Description: {income.description}",
                             f"Time: {str_from_time(income.time)}"])
        self.reply(update, response)
    
    def cancel(self, update: Update, expense: Expense) -> None:
        description = expense.description if expense.description is not None else ""
        response = "\n".join(["Deleted expense:",
                             f"Amount: {expense.amount:.2f}",
                             f"Category: {expense.category.capitalize()}",
                             f"Description: {description}",
                             f"Time: {str_from_time(expense.time)}"])
        self.reply(update, response)
    
    def balance(self, update: Update, balance: float) -> None:
        response = f"Current balance is: {balance:.2f}"
        self.reply(update, response)
    
    def categories(self, update: Update, categories: list[Category]) -> None:
        response = f"Categories:\n"
        for idx, category in enumerate(categories, start=1):
            name = category.name
            aliases = category.aliases
            response += f"{idx}. {name.capitalize()}: {', '.join(aliases)}\n"
        self.reply(update, response)