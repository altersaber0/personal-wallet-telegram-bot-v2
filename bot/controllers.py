from telegram.update import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
    CallbackContext,
    BaseFilter
)

from .core.classes import Expense, Income
from .core.utils import time_now, isfloat, split_in_rows
from .core.controller_abc import Controller, block_if_in_blocked_mode
from .view import View
from .model import Model


class AddExpense(Controller):
    # states of the conversation
    AMOUNT = 0
    CATEGORY = 1
    DESCRIPTION = 2

    def __init__(self, updater: Updater, user_filter: BaseFilter, view: View, model: Model) -> None:
        super().__init__(updater, user_filter, view, model)
        # save expense object for filling up between conversation states
        self.exp = None
    
    @block_if_in_blocked_mode
    def expense(self, update: Update, context: CallbackContext) -> int:
        """/expense command - entry point to conversation."""

        # create dummy Expense object to fill in the process
        self.exp = Expense(0, "", None, time_now())
        self.view.reply(update, "Adding new expense.\nEnter the amount:")
        return AddExpense.AMOUNT
    
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
        return AddExpense.CATEGORY
    
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
        return AddExpense.DESCRIPTION
    
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

    def add_handlers(self) -> None:
        dp = self.updater.dispatcher
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "expense",
                    self.expense,
                    filters=self.user_filter
                )
            ],
            states={
                AddExpense.AMOUNT: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.amount
                    )
                ],
                AddExpense.CATEGORY: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.category
                    )
                ],
                AddExpense.DESCRIPTION: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.description
                    ),
                    CommandHandler(
                        "skip",
                        self.skip_description,
                        filters=self.user_filter
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.cancel,
                    filters=self.user_filter
                )
            ]
        ))


class AddIncome(Controller):
    # states of the conversation
    AMOUNT = 0
    DESCRIPTION = 1

    def __init__(self, updater: Updater, user_filter: BaseFilter, view: View, model: Model) -> None:
        super().__init__(updater, user_filter, view, model)
        # save income object for filling up between conversation states
        self.inc = None
    
    @block_if_in_blocked_mode
    def income(self, update: Update, context: CallbackContext) -> int:
        """/income command - entry point to conversation."""

        self.inc = Income(0, "", time_now())
        self.view.reply(update, "Adding new income.\nEnter the amount:")
        return AddIncome.AMOUNT
    
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
        return AddIncome.DESCRIPTION
    
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
    
    def add_handlers(self) -> None:
        dp = self.updater.dispatcher
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "income",
                    self.income,
                    filters=self.user_filter
                )
            ],
            states={
                AddIncome.AMOUNT: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.amount
                    )
                ],
                AddIncome.DESCRIPTION: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.description
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.cancel,
                    filters=self.user_filter
                )
            ]
        ))


class AddCategory(Controller):
    # states of the conversation
    CATEGORY = 0

    @block_if_in_blocked_mode
    def add_category(self, update: Update, context: CallbackContext) -> int:
        """/add_category command - entry point to conversation."""

        self.view.reply(update, "Enter the name of a new category:")
        return AddCategory.CATEGORY
    
    def category(self, update: Update, context: CallbackContext) -> int:
        """Ask user for a new category name."""

        category = update.message.text.lower()

        # ask for a name until it is unique
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
    
    def add_handlers(self) -> None:
        dp = self.updater.dispatcher
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "add_category",
                    self.add_category,
                    filters=self.user_filter
                )
            ],
            states={
                AddCategory.CATEGORY: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.category
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.cancel,
                    filters=self.user_filter
                )
            ]
        ))


class UpdateCategory(Controller):
    # states of the conversation
    CATEGORY = 0
    NEW_NAME = 1

    def __init__(self, updater: Updater, user_filter: BaseFilter, view: View, model: Model) -> None:
        super().__init__(updater, user_filter, view, model)
        # save old name of the category between conversation states
        self.old_name = None

    @block_if_in_blocked_mode
    def update_category(self, update: Update, context: CallbackContext) -> int:
        """/update_category command - entry point to conversation."""

        buttons = split_in_rows(self.model.db.get_categories(), row_size=3)
        self.view.reply_with_replykeyboard(
            update,
            text="Choose which category to update:",
            buttons=buttons,
            placeholder="Category:"
        )
        return UpdateCategory.CATEGORY
    
    def category(self, update: Update, context: CallbackContext) -> int:
        """Ask the user which category to update."""

        old = update.message.text.lower()

        # exclude "other" category from the list so it can't be updated
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
        """Ask the user for a new category name."""

        new = update.message.text.lower()

        # ask for a name until it is unique
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
    
    def add_handlers(self) -> None:
        dp = self.updater.dispatcher
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "update_category",
                    self.update_category,
                    filters=self.user_filter
                )
            ],
            states={
                UpdateCategory.CATEGORY: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.category
                    )
                ],
                UpdateCategory.NEW_NAME: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.new_name
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.cancel,
                    filters=self.user_filter
                )
            ]
        ))


class DeleteCategory(Controller):
    # states of the conversation
    CATEGORY = 0
    CONFIRM = 1

    def __init__(self, updater: Updater, user_filter: BaseFilter, view: View, model: Model) -> None:
        super().__init__(updater, user_filter, view, model)
        # save category between conversation states
        self.cat = None
    
    @block_if_in_blocked_mode
    def delete_category(self, update: Update, context: CallbackContext) -> int:
        """/delete_category command - entry point to conversation."""

        buttons = split_in_rows(self.model.db.get_categories(), row_size=3)
        self.view.reply_with_replykeyboard(
            update,
            text="Choose which category to delete:",
            buttons=buttons,
            placeholder="Category:"
        )
        return DeleteCategory.CATEGORY
    
    def category(self, update: Update, context: CallbackContext) -> int:
        """Ask the user which category to delete."""

        cat = update.message.text.lower()

        # exclude "other" category from the list so it can't be deleted
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
        """Ask the user to confirm deletion of the selected category."""

        answer = update.message.text

        # match the action based on confirmation answer
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
        self.view.reply_and_remove_replykeyboard(update, "Command cancelled.")
        return ConversationHandler.END
    
    def add_handlers(self) -> None:
        dp = self.updater.dispatcher
        dp.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler(
                    "delete_category",
                    self.delete_category,
                    filters=self.user_filter
                )
            ],
            states={
                DeleteCategory.CATEGORY: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.category
                    )
                ],
                DeleteCategory.CONFIRM: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.confirm
                    )
                ]
            },
            fallbacks=[
                CommandHandler(
                    "cancel",
                    self.cancel,
                    filters=self.user_filter
                )
            ]
        ))


class PlainCallbacks(Controller):

    @block_if_in_blocked_mode
    def start(self, update: Update, context: CallbackContext) -> None:
        """/start - command to start the bot."""

        self.view.reply(update, "Bot started.")
    
    @block_if_in_blocked_mode
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
            "/categories - show category names",
            "/add_category - add new category",
            "/update_category - rename existing category (except \"other\")",
            "/delete_category - delete existing category (expenses become \"other\")"
        ]))
    
    @block_if_in_blocked_mode
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

    @block_if_in_blocked_mode
    def categories(self, update: Update, context: CallbackContext) -> None:
        """/categories - command to show current list of categories."""

        categories = self.model.db.get_categories()
        self.view.categories(update, categories)
    
    @block_if_in_blocked_mode
    def cancel_last(self, update: Update, context: CallbackContext) -> None:
        """/cancel_last - command to delete the last added expense."""

        expense = self.model.db.delete_last_expense()
        # return to previous balance
        balance = self.model.get_balance()
        self.model.set_balance(balance + expense.amount)
        self.view.cancel(update, expense)
    
    def add_handlers(self) -> None:
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start, filters=self.user_filter))
        dp.add_handler(CommandHandler("help", self.help, filters=self.user_filter))
        dp.add_handler(CommandHandler("balance", self.balance, filters=self.user_filter))
        dp.add_handler(CommandHandler("categories", self.categories, filters=self.user_filter))
        dp.add_handler(CommandHandler("cancel_last", self.cancel_last, filters=self.user_filter))


class MasterController(Controller):
    def __init__(self, updater: Updater, user_filter: BaseFilter, view: View, model: Model) -> None:
        super().__init__(updater, user_filter, view, model)
        self.plain_callbacks = PlainCallbacks(updater, user_filter, view, model)
        self.add_expense = AddExpense(updater, user_filter, view, model)
        self.add_income = AddIncome(updater, user_filter, view, model)
        self.add_category = AddCategory(updater, user_filter, view, model)
        self.update_category = UpdateCategory(updater, user_filter, view, model)
        self.delete_category = DeleteCategory(updater, user_filter, view, model)
        self.controllers: list[Controller] = [
            self.plain_callbacks,
            self.add_expense,
            self.add_income,
            self.add_category,
            self.update_category,
            self.delete_category
        ]

    def block(self, update: Update, context: CallbackContext) -> None:
        """/block command - block all commands from executing until next /block."""

        for controller in self.controllers:
            controller.blocked_mode = not controller.blocked_mode

    def add_handlers(self) -> None:
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("block", self.block, filters=self.user_filter))

    def start_bot(self, poll_interval: float, timeout: float) -> None:
        """
        Create all data files if the don't exist yet,
        initialize handlers in controllers 
        and start polling updates from Telegram servers.
        """

        # create DB and balance files if they don't exist yet
        self.model.setup()

        # add handlers of all controllers to the dispatcher
        self.add_handlers()
        for controller in self.controllers:
            controller.add_handlers()
        
        # start polling updates from Telegram servers
        print("Bot running...")
        self.updater.start_polling(poll_interval=poll_interval, timeout=timeout)
        self.updater.idle()