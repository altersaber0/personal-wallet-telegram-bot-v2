from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.update import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters
)

from .core.classes import Expense, Income, Command
from .core.parser import (
    command_type,
    parse_expense,
    parse_income,
    parse_month,
    parse_new_balance
)
from .core.utils import time_now
from .view import View
from .model import Model


class ExpenseConversation:
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
        return ExpenseConversation.AMOUNT
    
    def amount(self, update: Update, context) -> int:
        message = update.message.text.lower()
        try:
            number = float(message)
        except ValueError:
            return

        self.exp.amount = number
        keyboard = [[category.name for category in self.model.db.get_categories()]]  
        self.view.reply_keyboard(
            update,
            "Choose category name:",
            buttons=keyboard,
            placeholder="Category:"
        )
        return ExpenseConversation.CATEGORY
    
    def category(self, update: Update, context) -> int:
        category = update.message.text
        if category not in [cat.name for cat in self.model.db.get_categories()]:
            category = "other"
            self.view.reply(update, "Choosing \"other\"")

        self.exp.category = category
        self.view.reply(update, "Add a description or /skip")
        return ExpenseConversation.DESCRIPTION
    
    def description(self, update: Update, context) -> int:
        self.exp.description = update.message.text
        self.model.db.add_expense(self.exp)
        balance = self.model.get_balance()
        self.model.set_balance(balance - self.exp.amount)
        self.view.expense(update, self.exp)
        self.exp = None
        return ConversationHandler.END
    
    def skip_description(self, update: Update, context) -> int:
        self.model.db.add_expense(self.exp)
        balance = self.model.get_balance()
        self.model.set_balance(balance - self.exp.amount)
        self.view.expense(update, self.exp)
        self.exp = None
        return ConversationHandler.END
    
    def cancel(self, update: Update, context) -> int:
        self.exp = None
        self.view.reply(update, "Stopping /expense conversation.")
        return ConversationHandler.END
        

class Controller:
    def __init__(self, telegram_api_key: str, telegram_user_id: int, view: View, model: Model) -> None:
        self.updater = Updater(token=telegram_api_key)
        self.user_filter = Filters.user(user_id=telegram_user_id)
        self.view = view
        self.model = model
        self.exp_c = ExpenseConversation(self.view, self.model)
    
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
        balance = self.model.get_balance()
        self.view.balance(update, balance)

    # /cancel_last command
    def cancel_last(self, update: Update, context) -> None:
        expense = self.model.db.delete_last_expense()
        # return to previous balance
        balance = self.model.get_balance()
        self.model.set_balance(balance + expense.amount)
        self.view.cancel(update, expense)

    # /categories command
    def categories(self, update: Update, context) -> None:
        response = f"Categories:\n"
        for idx, category in enumerate(self.model.db.get_categories(), start=1):
            name = category.name
            aliases = category.aliases
            response += f"{idx}. {name.capitalize()}: {', '.join(aliases)}\n"
        self.view.reply(update, response)
    
    # match text message type to corresponding reply or error
    def handle_message(self, update: Update, context) -> None:
        message = update.message.text
        command = command_type(message)
        try:
            match command:
                case Command.EXPENSE:
                    categories = self.model.db.get_categories()
                    expense = parse_expense(message, categories)
                    # update data in model
                    self.model.db.add_expense(expense)
                    balance = self.model.get_balance()
                    self.model.set_balance(balance - expense.amount)
                    self.view.expense(update, expense)

                case Command.INCOME:
                    income = parse_income(message)
                    # update data in model
                    self.model.db.add_income(income)
                    balance = self.model.get_balance()
                    self.model.set_balance(balance + income.amount)
                    self.view.income(update, income)

                case Command.SET_BALANCE:
                    new = parse_new_balance(message)
                    self.model.set_balance(new)
                    self.view.balance(update, new)

                case Command.UNKNOWN:
                    self.view.reply(update, "Unknown text command.")
                    
        except ValueError:
            self.view.error(update, command)

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

        # filter out /command messages
        # dp.add_handler(MessageHandler(
        #     Filters.text & (~Filters.command) & self.user_filter,
        #     self.handle_message
        # ))
        # /expense conversation handler
        dp.add_handler(ConversationHandler(
            entry_points=[CommandHandler("expense", self.exp_c.expense)],
            states={
                ExpenseConversation.AMOUNT: [
                    MessageHandler(
                        Filters.text & self.user_filter,
                        self.exp_c.amount
                    )
                ],
                ExpenseConversation.CATEGORY: [
                    MessageHandler(
                        Filters.text & self.user_filter,
                        self.exp_c.category
                    )
                ],
                ExpenseConversation.DESCRIPTION: [
                    MessageHandler(
                        Filters.text & (~Filters.command) & self.user_filter,
                        self.exp_c.description
                    ),
                    CommandHandler("skip", self.exp_c.skip_description)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.exp_c.cancel)]
        ))
        
        # start polling updates from Telegram servers
        print("Bot running...")
        self.updater.start_polling(poll_interval=poll_interval, timeout=timeout)
        self.updater.idle()