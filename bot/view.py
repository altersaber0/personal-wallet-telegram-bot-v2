from datetime import datetime

from telegram.update import Update

from .core.classes import Expense, Income
from .core.utils import str_from_time


class View:
    def __init__(self) -> None:
        ...
    
    def reply(self, update: Update, text: str) -> None:
        update.message.reply_text(text)
    
    def reply_expense(self, update: Update, expense: Expense) -> None:
        response = "\n".join(["Added new expense:",
                             f"Amount: {expense.amount:.2f}",
                             f"Category: {expense.category}",
                             f"Description: {expense.description}",
                             f"Time: {str_from_time(expense.time)}"])
        self.reply(update, response)
    
    def reply_income(self, update: Update, income: Income) -> None:
        response = "\n".join(["Added new income:",
                             f"Amount: {income.amount:.2f}",
                             f"Description: {income.description}",
                             f"Time: {str_from_time(income.time)}"])
        self.reply(update, response)
    
    def reply_cancel(self, update: Update, expense: Expense) -> None:
        response = "\n".join(["Deleted expense:",
                             f"Amount: {expense.amount:.2f}",
                             f"Category: {expense.category}",
                             f"Description: {expense.description}",
                             f"Time: {str_from_time(expense.time)}"])
        self.reply(update, response)
    
    def reply_balance(self, update: Update, balance: float) -> None:
        response = f"Current balance is: {balance:.2f}"
        self.reply(update, response)
    
    def reply_month(self, update: Update, month: datetime) -> None:
        ...
