import sys
import os

import dotenv
from telegram.ext import Updater, Filters

from bot.controllers import MasterController
from bot.view import View
from bot.model import Model, DummyModel


def main():
    dotenv.load_dotenv(".env")
    TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
    TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
    DATA_DIR_PATH = "data"

    updater = Updater(TELEGRAM_API_KEY)
    user_filter = Filters.user(TELEGRAM_USER_ID)
    view = View()

    if len(sys.argv) == 1:
        model = Model(DATA_DIR_PATH)
    else:
        match sys.argv[1:]:
            case ["-ro" | "--read-only"]:
                model = DummyModel(DATA_DIR_PATH)
            case _:
                print("Invalid command line arguments.")
                return


    controller = MasterController(updater, user_filter, view, model)
    
    controller.start_bot(poll_interval=1, timeout=5)


if __name__ == "__main__":
    main()