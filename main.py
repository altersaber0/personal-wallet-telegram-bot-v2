import os
import dotenv
from bot.controller import Controller


def main():
    dotenv.load_dotenv(".env")
    TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
    TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))

    controller = Controller(TELEGRAM_API_KEY, TELEGRAM_USER_ID)
    controller.start_bot()


if __name__ == "__main__":
    main()