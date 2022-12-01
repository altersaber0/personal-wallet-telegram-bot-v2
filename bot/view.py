from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.update import Update

from .core.interfaces import Expense, Income, MonthStatistics
from .core.utils import str_from_time


class View:
    def __init__(self) -> None:
        self.month_names = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }

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
    
    def month_statistics(self, update: Update, month_stat: MonthStatistics) -> None:
        """Show the given month statistics."""

        response = f"{self.month_names[month_stat.month]} {month_stat.year}\n\n"

        for category, amount in month_stat.statistics.items():
            response += f"{category.capitalize()}: {amount}\n"
        
        response += "\nBiggest expenses:\n"
        for idx, expense in enumerate(month_stat.biggest_expenses, start=1):
            response += f"{idx}) {expense.category.capitalize()} {expense.amount:.2f}\n"
            response += f"Description: {expense.description}\n"
            response += f"Time: {str_from_time(expense.time)}\n"
        
        response += f"\nStart balance: {month_stat.start_balance:.2f}\n"
        response += f"Last balance: {month_stat.end_balance}\n"

        diff = month_stat.balance_difference
        diff_signed_str = f"+{diff:.2f}" if diff > 0 else f"-{abs(diff):.2f}"
        percentage = (month_stat.end_balance / month_stat.start_balance - 1) * 100
        percentage_signed_str = f"+{percentage:.2f}" if percentage > 0 else f"-{abs(percentage):.2f}"
        response += f"Difference: {diff_signed_str} ({percentage_signed_str}%)"

        self.reply(update, response)