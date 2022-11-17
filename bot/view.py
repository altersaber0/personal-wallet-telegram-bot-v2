from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.update import Update

from .core.classes import Expense, Income
from .core.utils import str_from_time


class View:
    def reply(self, update: Update, text: str) -> None:
        """Send the given text to the user."""

        update.message.reply_text(text)
    
    def reply_with_replykeyboard(self, update: Update, *, text: str, buttons: list[list[str]], placeholder: str = "") -> None:
        """Show a ReplyKeyboard with the given button labels to the user."""

        keyboard = ReplyKeyboardMarkup(
            buttons,
            input_field_placeholder=placeholder
        )
        update.message.reply_text(text, reply_markup=keyboard)
    
    def reply_and_remove_replykeyboard(self, update: Update, text: str) -> None:
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    
    def expense(self, update: Update, expense: Expense) -> None:
        """Show successful addition of an Expense."""

        description = expense.description if expense.description is not None else ""
        response = "\n".join(["Added new expense:",
                             f"Amount: {expense.amount:.2f}",
                             f"Category: {expense.category.capitalize()}",
                             f"Description: {description}",
                             f"Time: {str_from_time(expense.time)}"])
        self.reply(update, response)
    
    def income(self, update: Update, income: Income) -> None:
        """Show successful addition of an Income."""

        response = "\n".join(["Added new income:",
                             f"Amount: {income.amount:.2f}",
                             f"Description: {income.description}",
                             f"Time: {str_from_time(income.time)}"])
        self.reply(update, response)
    
    def cancel(self, update: Update, expense: Expense) -> None:
        """Show successful deletion of the last Expense."""

        description = expense.description if expense.description is not None else ""
        response = "\n".join(["Deleted expense:",
                             f"Amount: {expense.amount:.2f}",
                             f"Category: {expense.category.capitalize()}",
                             f"Description: {description}",
                             f"Time: {str_from_time(expense.time)}"])
        self.reply(update, response)
    
    def balance(self, update: Update, balance: float) -> None:
        """Show current balance."""

        response = f"Current balance is: {balance:.2f}"
        self.reply(update, response)
    
    def categories(self, update: Update, categories: list[str]) -> None:
        """Show the current list of categories."""

        response = f"Categories:\n"
        for idx, category in enumerate(categories, start=1):
            response += f"{idx}. {category.capitalize()}\n"
        self.reply(update, response)