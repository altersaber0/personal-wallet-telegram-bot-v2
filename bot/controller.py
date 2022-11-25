from telegram.update import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
    CallbackContext
)

from .core.classes import Expense, Income
from .core.utils import time_now, isfloat, split_in_rows
from .view import View
from .model import Model


class ExpenseController:
    # states of the conversation
    AMOUNT = 0
    CATEGORY = 1
    DESCRIPTION = 2

    def __init__(self, view: View, model: Model) -> None:
        self.view = view
        self.model = model
        self.exp = None

    def expense(self, update: Update, context: CallbackContext) -> int:
        """/expense command - entry point to conversation."""

        # create dummy Expense object to fill in the process
        self.exp = Expense(0, "", None, time_now())
        self.view.reply(update, "Adding new expense.\nEnter the amount:")
        return ExpenseController.AMOUNT
    
    def amount(self, update: Update, context: CallbackContext) -> int:
        """
        Getting expense amount from user until it's a valid number.
        Then ask to choose a category with a keyboard.
        """

        message = update.message.text.lower()
        if not isfloat(message):
            return

        self.exp.amount = float(message)
        
        # send keyboard with categories to choose from
        buttons = split_in_rows(self.model.db.get_categories(), row_size=3)
        self.view.reply_with_replykeyboard(
            update,
            text="Choose category name:",
            buttons=buttons,
            placeholder="Category:"
        )
        return ExpenseController.CATEGORY
    
    def category(self, update: Update, context: CallbackContext) -> int:
        """
        Getting category name via keyboard or message.
        Category becomes \"other\" if the message doesn't match to any category.
        Then ask to add a description or /skip.
        """

        category = update.message.text
        if category not in self.model.db.get_categories():
            category = "other"
            self.view.reply(update, "Choosing \"other\"")

        self.exp.category = category
        self.view.reply_and_remove_replykeyboard(update, "Add a description or /skip")
        return ExpenseController.DESCRIPTION
    
    def description(self, update: Update, context: CallbackContext) -> int:
        """
        Getting description of the expense, adding expense to the database,
        updating balance and finishing off the conversation.
        """

        self.exp.description = update.message.text
        # add and update data in model
        self.model.db.add_expense(self.exp)
        balance = self.model.get_balance()
        self.model.set_balance(balance - self.exp.amount)
        # reply and reset
        self.view.expense(update, self.exp)
        self.exp = None
        return ConversationHandler.END
    
    def skip_description(self, update: Update, context: CallbackContext) -> int:
        """
        Adding expense to the database, updating balance
        and finishing off the conversation.
        """

        # add and update data in model
        self.model.db.add_expense(self.exp)
        balance = self.model.get_balance()
        self.model.set_balance(balance - self.exp.amount)
        # reply and reset
        self.view.expense(update, self.exp)
        self.exp = None
        return ConversationHandler.END
    
    def cancel(self, update: Update, context: CallbackContext) -> int:
        """/cancel command to stop the conversation at any state."""

        # reset and reply
        self.exp = None
        self.view.reply(update, "Stopping /expense conversation.")
        return ConversationHandler.END


class IncomeController:
    # states of the conversation
    AMOUNT = 0
    DESCRIPTION = 1

    def __init__(self, view: View, model: Model) -> None:
        self.view = view
        self.model = model
        self.inc = None

    def income(self, update: Update, context: CallbackContext) -> int:
        """/income command - entry point to conversation."""

        self.inc = Income(0, "", time_now())
        self.view.reply(update, "Adding new income.\nEnter the amount:")
        return IncomeController.AMOUNT
    
    def amount(self, update: Update, context: CallbackContext) -> int:
        """
        Getting income amount from user until it's a valid number.
        Then asking to add a description.
        """

        # getting amount until it's a valid number
        message = update.message.text.lower()
        if not isfloat(message):
            return

        self.inc.amount = float(message)
        self.view.reply(update, "Add a description:")
        return IncomeController.DESCRIPTION
    
    def description(self, update: Update, context: CallbackContext) -> int:
        """
        Getting description, adding income to the database,
        updating balance and finishing off the conversation.
        """

        self.inc.description = update.message.text
        # add and update data in model
        self.model.db.add_income(self.inc)
        balance = self.model.get_balance()
        self.model.set_balance(balance + self.inc.amount)
        # reply and reset
        self.view.income(update, self.inc)
        self.inc = None
        return ConversationHandler.END

    # /cancel command to stop the conversation at any state
    def cancel(self, update: Update, context: CallbackContext) -> int:
        """/cancel command to stop the conversation at any state."""

        self.inc = None
        self.view.reply(update, "Stopping /income conversation.")
        return ConversationHandler.END


class Controller:
    def __init__(self, telegram_api_key: str, telegram_user_id: int, view: View, model: Model) -> None:
        self.updater = Updater(token=telegram_api_key)
        self.user_filter = Filters.user(user_id=telegram_user_id)
        self.view = view
        self.model = model
        self.exp_c = ExpenseController(self.view, self.model)
        self.inc_c = IncomeController(self.view, self.model)
    
    def start(self, update: Update, context: CallbackContext) -> None:
        """/start - command to start the bot."""

        self.view.reply(update, "Bot started.")
    
    def help(self, update: Update, context: CallbackContext) -> None:
        """/help - command to show the list of available commands."""

        self.view.reply(update, "\n".join([
            "Commands:",
            "/start - start the bot",
            "/help - this message",
            "/balance (num) - show (set) balance",
            "/expense - add new expense",
            "/income - add new income",
            "/cancel_last - cancel last expense",
            "/categories - show category names"
        ]))
    
    def balance(self, update: Update, context: CallbackContext) -> None:
        """
        /balance - command to show the current balance. First and only context argument 
        can set new balance if it's a valid number.
        """

        if len(context.args) == 0:
            balance = self.model.get_balance()
            self.view.balance(update, balance)
        elif len(context.args) == 1 and isfloat(context.args[0]):
            balance = self.model.get_balance()
            new_balance = float(context.args[0])
            self.model.set_balance(new_balance)
            self.view.balance(update, new_balance)
        else:
            self.view.reply(update, "Invalid /balance command")

    def cancel_last(self, update: Update, context: CallbackContext) -> None:
        """/cancel_last - command to delete the last added expense."""

        expense = self.model.db.delete_last_expense()
        # return to previous balance
        balance = self.model.get_balance()
        self.model.set_balance(balance + expense.amount)
        self.view.cancel(update, expense)

    def categories(self, update: Update, context: CallbackContext) -> None:
        """/categories - command to show current list of categories."""

        categories = self.model.db.get_categories()
        self.view.categories(update, categories)

    def start_bot(self, poll_interval: float, timeout: float) -> None:
        """
        Create all data files if the don't exist yet,
        initialize command and conversation handlers 
        and start polling updates from Telegram servers.
        """

        # create DB and balance files if they don't exist yet
        self.model.setup()

        # /command handlers
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start, filters=self.user_filter))
        dp.add_handler(CommandHandler("help", self.help, filters=self.user_filter))
        dp.add_handler(CommandHandler("categories", self.categories, filters=self.user_filter))
        dp.add_handler(CommandHandler("balance", self.balance, filters=self.user_filter))
        dp.add_handler(CommandHandler("cancel_last", self.cancel_last, filters=self.user_filter))

        # /expense conversation handler
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "expense",
                    self.exp_c.expense,
                    filters=self.user_filter
                )
            ],
            states={
                ExpenseController.AMOUNT: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.exp_c.amount
                    )
                ],
                ExpenseController.CATEGORY: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.exp_c.category
                    )
                ],
                ExpenseController.DESCRIPTION: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.exp_c.description
                    ),
                    CommandHandler(
                        "skip",
                        self.exp_c.skip_description,
                        filters=self.user_filter
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.exp_c.cancel,
                    filters=self.user_filter
                )
            ]
        ))

        # /income conversation handler
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "income",
                    self.inc_c.income,
                    filters=self.user_filter
                )
            ],
            states={
                IncomeController.AMOUNT: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.inc_c.amount
                    )
                ],
                IncomeController.DESCRIPTION: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.inc_c.description
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.inc_c.cancel,
                    filters=self.user_filter
                )
            ]
        ))
        
        # start polling updates from Telegram servers
        print("Bot running...")
        self.updater.start_polling(poll_interval=poll_interval, timeout=timeout)
        self.updater.idle()