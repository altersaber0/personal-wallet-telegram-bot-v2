from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.update import Update

from core.classes import Expense, Income
from view import View
from model import Model

class Controller:
    def __init__(self, telegram_api_key: str, telegram_user_id: int, view: View, model: Model) -> None:
        self.updater = Updater(token=telegram_api_key)
        self.user_filter = Filters.user(user_id=telegram_user_id)
        self.view = view
        self.model = model
    
    def start(self, update: Update, context) -> None:
        update.message.reply_text("Bot started.")
    
    def handle_message(self, update: Update, context) -> None:
        update.message.reply_text(update.message.text)
    
    def start_bot(self) -> None:
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start, filters=self.user_filter))
        dp.add_handler(MessageHandler(Filters.text & self.user_filter, self.handle_message))

        print("Bot running...")
        self.updater.start_polling(poll_interval=1, timeout=5)
        self.updater.idle()