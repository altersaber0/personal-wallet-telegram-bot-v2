from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.update import Update

from .core.classes import Expense, Income, Categories
from .core.parser import command_type, parse_expense, parse_income, parse_month
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
    
    def categories(self, update: Update, context) -> None:
        response = f"Categories:\n"
        for cat in Categories:
            response += f"{cat.value}\n"
        self.view.reply(update, response)
    
    def handle_message(self, update: Update, context) -> None:
        self.view.reply(update, update.message.text)

    
    def start_bot(self, poll_interval: float, timeout: float) -> None:
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start, filters=self.user_filter))
        dp.add_handler(CommandHandler("help", self.help, filters=self.user_filter))
        dp.add_handler(CommandHandler("categories", self.categories, filters=self.user_filter))
        dp.add_handler(MessageHandler(Filters.text & (~Filters.command) & self.user_filter, self.handle_message))

        print("Bot running...")
        self.updater.start_polling(poll_interval=poll_interval, timeout=timeout)
        self.updater.idle()