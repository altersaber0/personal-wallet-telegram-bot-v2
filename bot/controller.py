from telegram.update import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters
)

from .core.classes import Expense, Income

from .core.utils import time_now, isfloat, split_in_chunks
from .view import View
from .model import Model


class ExpenseController:
    AMOUNT = 0
    CATEGORY = 1
    DESCRIPTION = 2

    def __init__(self, view: View, model: Model) -> None:
        self.view = view
        self.model = model
        self.exp = None

    def expense(self, update: Update, context) -> int:
        self.exp = Expense(0, "", None, time_now())
        self.view.reply(update, "Adding new expense.\nEnter the amount:")
        return ExpenseController.AMOUNT
    
    def amount(self, update: Update, context) -> int:
        message = update.message.text.lower()
        if not isfloat(message):
            return

        self.exp.amount = float(message)
        
        buttons = split_in_chunks(
            [category.name for category in self.model.db.get_categories()],
            chunk_size=3)

        self.view.reply_keyboard(
            update,
            text="Choose category name:",
            buttons=buttons,
            placeholder="Category:"
        )
        return ExpenseController.CATEGORY
    
    def category(self, update: Update, context) -> int:
        category = update.message.text
        if category not in [cat.name for cat in self.model.db.get_categories()]:
            category = "other"
            self.view.reply(update, "Choosing \"other\"")

        self.exp.category = category
        self.view.reply(update, "Add a description or /skip")
        return ExpenseController.DESCRIPTION
    
    def description(self, update: Update, context) -> int:
        self.exp.description = update.message.text
        # add and update data in model
        self.model.db.add_expense(self.exp)
        balance = self.model.get_balance()
        self.model.set_balance(balance - self.exp.amount)
        # reply and reset
        self.view.expense(update, self.exp)
        self.exp = None
        return ConversationHandler.END
    
    def skip_description(self, update: Update, context) -> int:
        # add and update data in model
        self.model.db.add_expense(self.exp)
        balance = self.model.get_balance()
        self.model.set_balance(balance - self.exp.amount)
        # reply and reset
        self.view.expense(update, self.exp)
        self.exp = None
        return ConversationHandler.END
    
    def cancel(self, update: Update, context) -> int:
        self.exp = None
        self.view.reply(update, "Stopping /expense conversation.")
        return ConversationHandler.END


class IncomeController:
    AMOUNT = 0
    DESCRIPTION = 1

    def __init__(self, view: View, model: Model) -> None:
        self.view = view
        self.model = model
        self.inc = None

    def income(self, update: Update, context) -> int:
        self.inc = Income(0, "", time_now())
        self.view.reply(update, "Adding new income.\nEnter the amount:")
        return IncomeController.AMOUNT
    
    def amount(self, update: Update, context) -> int:
        message = update.message.text.lower()
        if not isfloat(message):
            return

        self.inc.amount = float(message)
        self.view.reply(update, "Add a description:")
        return IncomeController.DESCRIPTION
    
    def description(self, update: Update, context) -> int:
        self.inc.description = update.message.text
        # add and update data in model
        self.model.db.add_income(self.inc)
        balance = self.model.get_balance()
        self.model.set_balance(balance + self.inc.amount)
        # reply and reset
        self.view.income(update, self.inc)
        self.inc = None
        return ConversationHandler.END
    
    def cancel(self, update: Update, context) -> int:
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
    
    # /start command
    def start(self, update: Update, context) -> None:
        self.view.reply(update, "Bot started.")
    
    # /help command
    def help(self, update: Update, context) -> None:
        self.view.reply(update, "\n".join([
        "Text commands:",
        "add expense: \"- amount (category | description)\"",
        "add income: \"+ amount description\"",
        "set balance: \"'balance' amount\"",
        "month statistics: \"(month | {concrete}) (year)\"",
        "",
        "Slash commands:",
        "/start - start the bot",
        "/help - this message",
        "/expense - add expense (conversation)",
        "/income - add income (conversation)",
        "/balance - check balance",
        "/month - current month statistics",
        "/cancel_last - cancel last expense",
        "/categories - show category names"
        ]))
    
    # /balance command
    def balance(self, update: Update, context) -> None:
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

    # /cancel_last command
    def cancel_last(self, update: Update, context) -> None:
        expense = self.model.db.delete_last_expense()
        # return to previous balance
        balance = self.model.get_balance()
        self.model.set_balance(balance + expense.amount)
        self.view.cancel(update, expense)

    # /categories command
    def categories(self, update: Update, context) -> None:
        categories = self.model.db.get_categories()
        self.view.categories(update, categories)

    def start_bot(self, poll_interval: float, timeout: float) -> None:
        # create DB and balance files if they don't exist yet
        self.model.setup()

        # add /command and message handlers
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start, filters=self.user_filter))
        dp.add_handler(CommandHandler("help", self.help, filters=self.user_filter))
        dp.add_handler(CommandHandler("categories", self.categories, filters=self.user_filter))
        dp.add_handler(CommandHandler("balance", self.balance, filters=self.user_filter))
        dp.add_handler(CommandHandler("cancel_last", self.cancel_last, filters=self.user_filter))

        # /expense conversation command
        dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler("expense", self.exp_c.expense)],
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
                    CommandHandler("skip", self.exp_c.skip_description)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.exp_c.cancel)]
        ))

        # /income conversation command
        dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler("income", self.inc_c.income)],
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
            fallbacks=[CommandHandler("cancel", self.inc_c.cancel)]
        ))
        
        # start polling updates from Telegram servers
        print("Bot running...")
        self.updater.start_polling(poll_interval=poll_interval, timeout=timeout)
        self.updater.idle()