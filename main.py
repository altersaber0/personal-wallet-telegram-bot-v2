import os
from pathlib import Path

import dotenv

from bot.controller import Controller
from bot.view import View
from bot.model import Model


def main():
    dotenv.load_dotenv(".env")
    TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
    TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
    DATA_DIR_PATH = Path("data")

    controller = Controller(
        telegram_api_key=TELEGRAM_API_KEY,
        telegram_user_id=TELEGRAM_USER_ID,
        view=View(),
        model=Model(DATA_DIR_PATH)
    )
    
    controller.start_bot(poll_interval=1, timeout=5)


if __name__ == "__main__":
    main()