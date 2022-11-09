from datetime import datetime

from telegram.update import Update

from .core.classes import Expense, Income, Command
from .core.utils import str_from_time


class View:
    
    def reply(self, update: Update, text: str) -> None:
        update.message.reply_text(text)
    
    def reply_error(self, update: Update, command: Command) -> None:
        match command:
            case Command.EXPENSE:
                self.reply(update, "Invalid expense message")
            case Command.INCOME:
                self.reply(update, "Invalid income message")
            case Command.SET_BALANCE:
                self.reply(update, "Invalid new balance message")
    
    def reply_expense(self, update: Update, expense: Expense) -> None:
        description = expense.description if expense.description is not None else ""
        response = "\n".join(["Added new expense:",
                             f"Amount: {expense.amount:.2f}",
                             f"Category: {expense.category.capitalize()}",
                             f"Description: {description}",
                             f"Time: {str_from_time(expense.time)}"])
        self.reply(update, response)
    
    def reply_income(self, update: Update, income: Income) -> None:
        response = "\n".join(["Added new income:",
                             f"Amount: {income.amount:.2f}",
                             f"Description: {income.description}",
                             f"Time: {str_from_time(income.time)}"])
        self.reply(update, response)
    
    def reply_cancel(self, update: Update, expense: Expense) -> None:
        description = expense.description if expense.description is not None else ""
        response = "\n".join(["Deleted expense:",
                             f"Amount: {expense.amount:.2f}",
                             f"Category: {expense.category.capitalize()}",
                             f"Description: {description}",
                             f"Time: {str_from_time(expense.time)}"])
        self.reply(update, response)
    
    def reply_balance(self, update: Update, balance: float) -> None:
        response = f"Current balance is: {balance:.2f}"
        self.reply(update, response)
        