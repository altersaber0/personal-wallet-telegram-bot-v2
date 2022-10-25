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
        response = f"""Added new expense:
                    Amount: {expense.amount:.2f}
                    Category: {expense.category}
                    Description: {expense.description}
                    Time: {str_from_time(expense.time)}"""
        self.reply(update, response)
    
    def reply_income(self, update: Update, income: Income) -> None:
        response = f"""Added new income:
                    Amount: {income.amount:.2f}
                    Description: {income.description}
                    Time: {str_from_time(income.time)}"""
        self.reply(update, response)
    
    def reply_cancel(self, update: Update, expense: Expense) -> None:
        response = f"""Deleted expense:
                    Amount: {expense.amount:.2f}
                    Category: {expense.category}
                    Description: {expense.description}
                    Time: {str_from_time(expense.time)}"""
        self.reply(update, response)
    
    def reply_month(self, update: Update, month: datetime) -> None:
        ...
