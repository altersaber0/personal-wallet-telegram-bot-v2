import io

import matplotlib.pyplot as plt
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

        # creating response text
        response = ""
        header = f"{self.month_names[month_stat.month]} {month_stat.year}"
        response += header
        response += "\n\n"
        
        response += "Biggest expenses:\n"
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

        # creating statistics bar chart
        # preparing data
        sorted_statistics = dict(sorted(month_stat.statistics.items(), key=lambda x: x[1]))
        categories = [cat.capitalize() for cat in sorted_statistics.keys()]
        amounts = list(sorted_statistics.values())

        # creating barchart
        plt.figure(figsize=(10, 6), dpi=100)
        plt.grid(True, linestyle=":", color="gray", linewidth=0.5)
        barchart = plt.barh(categories, amounts, height=0.7)
        plt.title(header)
        plt.xlabel("Amount of money spent")

        # adding amounts into respective bars
        for bar, amount in zip(barchart, amounts):
            plt.text(bar.get_width() - 10, bar.get_y() + bar.get_height() / 2, f"{amount:.0f}", color="white", ha="right", va="center", size=18)

        plt.tight_layout()

        # save figure to an io buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png")
        img_buffer.seek(0)

        update.message.reply_photo(caption=response, photo=img_buffer)