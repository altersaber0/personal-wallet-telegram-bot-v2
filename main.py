import os

import dotenv
from telegram.ext import Updater, Filters

from bot.controllers import MasterController
from bot.view import View
from bot.model import Model


def main():
    dotenv.load_dotenv(".env")
    TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
    TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
    DATA_DIR_PATH = "data"

    updater = Updater(TELEGRAM_API_KEY)
    user_filter = Filters.user(TELEGRAM_USER_ID)
    view = View()
    model = Model(DATA_DIR_PATH)

    controller = MasterController(updater, user_filter, view, model)
    
    controller.start_bot(poll_interval=1, timeout=5)


if __name__ == "__main__":
    main()