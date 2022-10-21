from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.update import Update

class Controller:
    def __init__(self, telegram_api_key: str, telegram_user_id: int) -> None:
        self.updater = Updater(token=telegram_api_key)
        self.user_filter = Filters.user(user_id=telegram_user_id)
    
    def start(self, update: Update, context) -> None:
        update.message.reply_text("Bot started.")
    
    def handle_message(self, update: Update, context):
        update.message.reply_text(update.message.text)
    
    def start_bot(self) -> None:
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start, filters=self.user_filter))
        dp.add_handler(MessageHandler(Filters.text & self.user_filter, self.handle_message))

        print("Bot running...")
        self.updater.start_polling(poll_interval=1, timeout=5)
        self.updater.idle()