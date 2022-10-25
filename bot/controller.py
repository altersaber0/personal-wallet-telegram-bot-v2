from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.update import Update

from .core.classes import Expense, Income, Categories, Command
from .core.parser import command_type, parse_expense, parse_income, parse_month, parse_new_balance
from .view import View
from .model import Model

class Controller:
    def __init__(self, telegram_api_key: str, telegram_user_id: int, view: View, model: Model) -> None:
        self.updater = Updater(token=telegram_api_key)
        self.user_filter = Filters.user(user_id=telegram_user_id)
        self.view = view
        self.model = model
    
    def start(self, update: Update, context) -> None:
        self.view.reply(update, "Bot started.")
    
    def help(self, update: Update, context) -> None:
        self.view.reply(update, "\n".join([
        "Text commands:",
        "add expense: \"- amount (category | description)\"",
        "add income: \"+ amount description\"",
        "check balance: \"(balance | bl)\"",
        "change balance: \"(balance | bl) amount\"",
        "month statistics: \"(month | {concrete}) (year)\"",
        "cancel last expense: \"cancel\"",
        "",
        "Slash commands:",
        "/start - start the bot",
        "/help - this message",
        "/expense - add expense",
        "/income - add income",
        "/balance - check balance",
        "/month - current month statistics",
        "/cancel - cancel last expense",
        "/categories - show category names",
        ]))
    
    def balance(self, update: Update, context) -> None:
        balance = self.model.get_balance()
        self.view.reply_balance(update, balance)
    
    def categories(self, update: Update, context) -> None:
        response = f"Categories:\n"
        for idx, cat in enumerate(Categories, start=1):
            response += f"{idx}. {cat.value}\n"
        self.view.reply(update, response)
    
    def handle_message(self, update: Update, context) -> None:
        message = update.message.text
        command = command_type(message)
        match command:
            case Command.EXPENSE:
                try:
                    expense = parse_expense(message)
                    balance = self.model.get_balance()
                    self.model.set_balance(balance - expense.amount)
                    self.view.reply_expense(update, expense)
                except ValueError:
                    self.view.reply("Invalid expense message.")
            case Command.INCOME:
                try:
                    income = parse_income(message)
                    balance = self.model.get_balance()
                    self.model.set_balance(balance + income.amount)
                    self.view.reply_income(update, income)
                except ValueError:
                    self.view.reply("Invalid income message.")
            case Command.BALANCE:
                balance = self.model.get_balance()
                self.view.reply_balance(update, balance)
            case Command.BALANCE_NEW:
                try:
                    new = parse_new_balance(message)
                    self.model.set_balance(new)
                    self.view.reply_balance(update, new)
                except ValueError:
                    self.view.reply("Invalid new balance.")

            case Command.UNKNOWN:
                self.view.reply(update, "Unknown text command.")
    
    def start_bot(self, poll_interval: float, timeout: float) -> None:
        self.model.setup()
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start, filters=self.user_filter))
        dp.add_handler(CommandHandler("help", self.help, filters=self.user_filter))
        dp.add_handler(CommandHandler("categories", self.categories, filters=self.user_filter))
        dp.add_handler(MessageHandler(Filters.text & (~Filters.command) & self.user_filter, self.handle_message))

        print("Bot running...")
        self.updater.start_polling(poll_interval=poll_interval, timeout=timeout)
        self.updater.idle()