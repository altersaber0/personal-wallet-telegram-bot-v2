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


class ExpenseConv:
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
        return ExpenseConv.AMOUNT
    
    def amount(self, update: Update, context: CallbackContext) -> int:
        """
        Getting expense amount from user until it's a valid number.
        Then ask to choose a category with a keyboard.
        """

        message = update.message.text.lower()
        if not isfloat(message):
            self.view.reply(update, f"\"{message}\" is not a valid number.\nTry again.")
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
        return ExpenseConv.CATEGORY
    
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
        return ExpenseConv.DESCRIPTION
    
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
        self.view.reply(update, "Command cancelled.")
        return ConversationHandler.END


class IncomeConv:
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
        return IncomeConv.AMOUNT
    
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
        return IncomeConv.DESCRIPTION
    
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

    def cancel(self, update: Update, context: CallbackContext) -> int:
        """/cancel command to stop the conversation at any state."""

        self.inc = None
        self.view.reply(update, "Command cancelled.")
        return ConversationHandler.END


class AddCategory:
    CATEGORY = 0

    def __init__(self, view: View, model: Model) -> None:
        self.view = view
        self.model = model

    def add_category(self, update: Update, context: CallbackContext) -> int:
        self.view.reply(update, "Enter the name of a new category:")
        return AddCategory.CATEGORY
    
    def category(self, update: Update, context: CallbackContext) -> int:
        category = update.message.text.lower()
        if category in self.model.db.get_categories():
            self.view.reply(update, "This name is already taken. Try again:")
            return
        
        self.model.db.add_category(category)
        self.view.reply(update, f"Added new category: \"{category}\"")

        return ConversationHandler.END
    
    def cancel(self, update: Update, context: CallbackContext) -> int:
        """/cancel command to stop the conversation at any state."""

        self.view.reply(update, "Command cancelled.")
        return ConversationHandler.END


class UpdateCategory:
    CATEGORY = 0
    NEW_NAME = 1

    def __init__(self, view: View, model: Model) -> None:
        self.view = view
        self.model = model
        self.old_name = None
    
    def update_category(self, update: Update, context: CallbackContext) -> int:
        buttons = split_in_rows(self.model.db.get_categories(), row_size=3)
        self.view.reply_with_replykeyboard(
            update,
            text="Choose which category to update:",
            buttons=buttons,
            placeholder="Category:"
        )
        return UpdateCategory.CATEGORY
    
    def category(self, update: Update, context: CallbackContext) -> int:
        old = update.message.text.lower()

        categories = self.model.db.get_categories()
        categories.remove("other")

        if old not in categories:
            self.view.reply(update, "This category doesn't exist. Try again.")
            return
        if old == "other":
            self.view.reply(update, "You cannot update \"other\". Try again.")
            return
        
        self.old_name = old
        self.view.reply_and_remove_replykeyboard(update, f"Enter new name for category \"{old}\":")
        return UpdateCategory.NEW_NAME
    
    def new_name(self, update: Update, context: CallbackContext) -> int:
        new = update.message.text.lower()
        if new in self.model.db.get_categories():
            self.view.reply(update, f"Name \"{new}\" is already taken. Try again:")
            return
        
        self.model.db.update_category(self.old_name, new)
        self.view.reply(update, f"Renamed category \"{self.old_name}\" to \"{new}\".")
        self.old_name = None
        return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext) -> int:
        """/cancel command to stop the conversation at any state."""

        self.old_name = None
        self.view.reply(update, "Command cancelled.")
        return ConversationHandler.END


class DeleteCategory:
    CATEGORY = 0
    CONFIRM = 1

    def __init__(self, view: View, model: Model) -> None:
        self.view = view
        self.model = model
        self.cat = None
    
    def delete_category(self, update: Update, context: CallbackContext) -> int:
        buttons = split_in_rows(self.model.db.get_categories(), row_size=3)
        self.view.reply_with_replykeyboard(
            update,
            text="Choose which category to delete:",
            buttons=buttons,
            placeholder="Category:"
        )
        return DeleteCategory.CATEGORY
    
    def category(self, update: Update, context: CallbackContext) -> int:
        cat = update.message.text.lower()

        categories = self.model.db.get_categories()
        categories.remove("other")

        if cat not in categories:
            self.view.reply(update, "This category doesn't exist. Try again.")
            return
        if cat == "other":
            self.view.reply(update, "You cannot delete \"other\". Try again.")
            return
        
        self.cat = cat
        self.view.reply_with_replykeyboard(
            update,
            text=f"Do you confirm deleting \"{cat}\"?",
            buttons=[["Yes"], ["No"]]
        )
        return UpdateCategory.NEW_NAME
    
    def confirm(self, update: Update, context: CallbackContext) -> int:
        answer = update.message.text

        if answer == "Yes":
            self.model.db.delete_category(self.cat)
            self.view.reply_and_remove_replykeyboard(update, f"Deleted category \"{self.cat}\".")
            self.cat = None
            return ConversationHandler.END
        elif answer == "No":
            self.view.reply_and_remove_replykeyboard(update, "Operation cancelled.")
            self.cat = None
            return ConversationHandler.END
        else:
            self.view.reply(update, "Answer must be \"Yes\" or \"No\".\nTry again:")
            return
    
    def cancel(self, update: Update, context: CallbackContext) -> int:
        """/cancel command to stop the conversation at any state."""

        self.old_name = None
        self.view.reply(update, "Command cancelled.")
        return ConversationHandler.END


class Controller:
    def __init__(self, telegram_api_key: str, telegram_user_id: int, view: View, model: Model) -> None:
        self.updater = Updater(token=telegram_api_key)
        self.user_filter = Filters.user(user_id=telegram_user_id)
        self.view = view
        self.model = model
        self.expconv = ExpenseConv(self.view, self.model)
        self.incconv = IncomeConv(self.view, self.model)
        self.addcat = AddCategory(self.view, self.model)
        self.updcat = UpdateCategory(self.view, self.model)
        self.delcat = DeleteCategory(self.view, self.model)
    
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

        # no context - show balance
        if len(context.args) == 0:
            balance = self.model.get_balance()
            self.view.balance(update, balance)
        # 1 numeric argument - set new balance
        elif len(context.args) == 1 and isfloat(context.args[0]):
            balance = self.model.get_balance()
            new_balance = float(context.args[0])
            self.model.set_balance(new_balance)
            self.view.balance(update, new_balance)
        # invalid command
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

        # /expense
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "expense",
                    self.expconv.expense,
                    filters=self.user_filter
                )
            ],
            states={
                ExpenseConv.AMOUNT: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.expconv.amount
                    )
                ],
                ExpenseConv.CATEGORY: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.expconv.category
                    )
                ],
                ExpenseConv.DESCRIPTION: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.expconv.description
                    ),
                    CommandHandler(
                        "skip",
                        self.expconv.skip_description,
                        filters=self.user_filter
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.expconv.cancel,
                    filters=self.user_filter
                )
            ]
        ))

        # /income
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "income",
                    self.incconv.income,
                    filters=self.user_filter
                )
            ],
            states={
                IncomeConv.AMOUNT: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.incconv.amount
                    )
                ],
                IncomeConv.DESCRIPTION: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.incconv.description
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.incconv.cancel,
                    filters=self.user_filter
                )
            ]
        ))

        # /add_category
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "add_category",
                    self.addcat.add_category,
                    filters=self.user_filter
                )
            ],
            states={
                AddCategory.CATEGORY: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.addcat.category
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.addcat.cancel,
                    filters=self.user_filter
                )
            ]
        ))

        # /update_category
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "update_category",
                    self.updcat.update_category,
                    filters=self.user_filter
                )
            ],
            states={
                UpdateCategory.CATEGORY: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.updcat.category
                    )
                ],
                UpdateCategory.NEW_NAME: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.updcat.new_name
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.updcat.cancel,
                    filters=self.user_filter
                )
            ]
        ))

        # /delete_category
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "delete_category",
                    self.delcat.delete_category,
                    filters=self.user_filter
                )
            ],
            states={
                DeleteCategory.CATEGORY: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.delcat.category
                    )
                ],
                DeleteCategory.CONFIRM: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.delcat.confirm
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.delcat.cancel,
                    filters=self.user_filter
                )
            ]
        ))
        
        # start polling updates from Telegram servers
        print("Bot running...")
        self.updater.start_polling(poll_interval=poll_interval, timeout=timeout)
        self.updater.idle()